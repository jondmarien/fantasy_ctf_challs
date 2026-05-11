#!/usr/bin/env bash
# Run as root on a freshly-provisioned Hetzner droplet AFTER cloud-init has completed.
# Idempotent: safe to re-run.
set -euo pipefail

REPO_URL="https://github.com/jondmarien/fantasy_ctf_challs.git"
REPO_DIR="/opt/fantasy_ctf_challs"
CTF_USER="ctf"

log() { echo "[$(date +%T)] $*"; }

# 1. Docker
if ! command -v docker >/dev/null 2>&1; then
  log "Installing Docker..."
  curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

# 2. ctf user
if ! id -u "$CTF_USER" >/dev/null 2>&1; then
  log "Creating $CTF_USER user..."
  useradd -m -s /bin/bash -G docker,sudo "$CTF_USER"
  mkdir -p "/home/$CTF_USER/.ssh"
  cp /root/.ssh/authorized_keys "/home/$CTF_USER/.ssh/"
  chown -R "$CTF_USER:$CTF_USER" "/home/$CTF_USER/.ssh"
  chmod 700 "/home/$CTF_USER/.ssh"
  chmod 600 "/home/$CTF_USER/.ssh/authorized_keys"
fi

# Sudoers: ctf can run the deploy script without password, nothing else
echo "$CTF_USER ALL=(ALL) NOPASSWD: $REPO_DIR/infra/deploy.sh" > /etc/sudoers.d/ctf-deploy
chmod 440 /etc/sudoers.d/ctf-deploy

# 3. Repo clone
if [ ! -d "$REPO_DIR/.git" ]; then
  log "Cloning repo to $REPO_DIR..."
  git clone "$REPO_URL" "$REPO_DIR"
fi
chown -R "$CTF_USER:$CTF_USER" "$REPO_DIR"

# 4. Secrets dir
mkdir -p "$REPO_DIR/infra/secrets"
chmod 700 "$REPO_DIR/infra/secrets"
chown "$CTF_USER:$CTF_USER" "$REPO_DIR/infra/secrets"

# 5. Docker log rotation
if [ ! -f /etc/docker/daemon.json ]; then
  log "Configuring Docker log rotation..."
  cat > /etc/docker/daemon.json <<'EOF'
{
  "log-driver": "json-file",
  "log-opts": { "max-size": "10m", "max-file": "3" },
  "live-restore": true
}
EOF
  systemctl restart docker
fi

# 6. Block droplet metadata from challenge nets (defense-in-depth)
if ! iptables -C DOCKER-USER -d 169.254.169.254 -j DROP 2>/dev/null; then
  log "Blocking metadata from Docker networks..."
  iptables -I DOCKER-USER -d 169.254.169.254 -j DROP
fi
apt-get install -y iptables-persistent
netfilter-persistent save

# 7. Disable root SSH login
sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
systemctl restart ssh

log "Bootstrap complete. SSH back in as '$CTF_USER'."
