# Terminal agent brief — restrict SSH at the ufw layer

**Context:** Jon removed the Hetzner Cloud Firewall during debugging. ufw on the host is now the only inbound filter. The bootstrap script added `ufw allow 22/tcp` with no source restriction, which means SSH is currently open to the entire internet. fail2ban will mitigate brute-force noise, but the SSH attack surface is wider than Jon wants.

You're going to:
1. Audit current ufw rules
2. Add an SSH rule scoped to Jon's home IP
3. Verify SSH still works through the new rule (with a separate session as proof)
4. Remove the wide-open SSH rule
5. Confirm final state

**Run as `ctf` user on the VPS.**

**Input from Jon:** his current public IPv4 address. Jon: get this with `curl -4 https://ifconfig.me` from your laptop and tell the agent before starting. Refer to it as `JON_IP` below.

---

## Where this fits in the sequence

```
Jon provides his public IP ──► You apply ufw changes ──► Jon verifies SSH still works ──► You remove old rule
```

This is a tightly-coupled handshake. Don't skip ahead.

---

## Step 0 — Safety first

**Before touching ufw, open a second SSH session to the VPS from your shell.** Keep it alive in a separate terminal tab. If your primary session breaks during the change, you have a fallback. If both break, Jon has to use the Hetzner web console to recover.

Confirm both sessions work:

```bash
# In session 1 (primary):
who am i

# Open session 2 in a separate terminal. Run:
who am i
# Confirm both sessions show up in: who
```

---

## Step 1 — Audit current ufw state

```bash
sudo ufw status verbose
sudo ufw status numbered
```

Capture the output. You're looking for:
- Default policy (should be `deny (incoming)` / `allow (outgoing)`)
- Rules for ports 22, 80, 443
- Any other rules (Docker may have added some; that's normal)

Report what you see to Jon before changing anything.

---

## Step 2 — Add the IP-scoped SSH rule

Jon provided `JON_IP`. Substitute it into:

```bash
JON_IP=<paste the IP Jon provided, e.g. 198.51.100.42>
sudo ufw allow from "$JON_IP"/32 to any port 22 proto tcp comment 'SSH from Jon home'
```

Verify the rule was added:

```bash
sudo ufw status numbered | grep -i ssh
sudo ufw status numbered | grep 22
```

Expect to see BOTH rules listed at this point:
- The new IP-scoped rule for `JON_IP`
- The old wide-open `22/tcp` rule

That's intentional — they coexist briefly while you verify.

---

## Step 3 — Have Jon verify SSH through the new rule

**Stop here. Tell Jon:**

> "New SSH rule added for `<JON_IP>`. Old wide-open rule is still in place as fallback. Please open a third SSH session from your laptop to confirm the new rule works. Reply 'verified' when you're in. If you can't connect, tell me immediately and I'll keep the wide-open rule for now."

Wait for Jon's confirmation. **Do not proceed** until he replies.

> If Jon can't connect with the IP-scoped rule: either he gave you the wrong IP, his IP changed (e.g. ISP rotated, or he's on mobile data instead of home WiFi), or there's a typo. Have him re-run `curl -4 https://ifconfig.me` and check the value. Don't proceed to Step 4 — leave the old rule as the unbroken path.

---

## Step 4 — Remove the wide-open SSH rule

Once Jon has confirmed:

```bash
# Find the rule number for the wide-open 22/tcp rule:
sudo ufw status numbered | grep '22/tcp' | grep -v "$JON_IP"

# It'll be something like:
# [ 1] 22/tcp                     ALLOW IN    Anywhere

# Delete by number (replace N with the actual number):
sudo ufw delete N
# It'll prompt for confirmation — type 'y'.

# OR, equivalently, delete by rule specification:
sudo ufw delete allow 22/tcp
```

Verify only the IP-scoped rule remains:

```bash
sudo ufw status numbered | grep 22
# Expect: only ONE row, the one with JON_IP
```

---

## Step 5 — Verify Jon can still connect

**Tell Jon:**

> "Wide-open SSH rule removed. The IP-scoped rule is now the only path. Please confirm by opening a fresh SSH session from your laptop. Reply 'still works' when you're in."

If Jon can still connect: done with the SSH side.

If Jon CANNOT connect: re-add the wide-open rule **fast** so he isn't locked out:

```bash
sudo ufw allow 22/tcp
```

Then debug — likely `JON_IP` was wrong or his actual source IP differs from what `ifconfig.me` reported (sometimes NAT/CGNAT scenarios cause this).

---

## Step 6 — Confirm 80 and 443 are still in ufw

These should already be allowed from anywhere — they're public-facing.

```bash
sudo ufw status verbose | grep -E '80|443'
# Expect to see:
#   80/tcp                     ALLOW IN    Anywhere
#   443/tcp                    ALLOW IN    Anywhere
#   (and v6 equivalents)
```

If 80 or 443 is missing for some reason:

```bash
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

---

## Step 7 — Note on Docker-published ports

You'll notice ufw has no rules for 1337-1340 or 7001-7005, but those challenges work fine from the public internet anyway. That's because Docker inserts its iptables rules in the FORWARD chain *before* ufw's filtering, so Docker-published ports bypass ufw entirely.

**Don't try to add ufw rules for those ports** — they won't help (the traffic isn't going through ufw's input chain). If you ever need to actually filter Docker traffic, the right tool is [`ufw-docker`](https://github.com/chaifeng/ufw-docker) or re-attaching a Hetzner Cloud Firewall on top. Jon's choice.

For this brief, leave Docker ports unchanged.

---

## Step 8 — Final state confirmation

```bash
sudo ufw status verbose
```

Expected output (roughly):

```
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), disabled (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    <JON_IP>           # SSH from Jon home
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
80/tcp (v6)                ALLOW IN    Anywhere (v6)
443/tcp (v6)               ALLOW IN    Anywhere (v6)
```

---

## Step 9 — Report back

Paste to Jon:

- The final `sudo ufw status verbose` output
- Confirmation that both your primary session and Jon's verification sessions worked through the new rule
- Anything unusual you saw during the audit (e.g. unexpected rules already in ufw)

---

## ⚠️ Don't touch

- **`/etc/ssh/sshd_config`** — that's already correctly set (PermitRootLogin no, PasswordAuthentication no). Don't fiddle.
- **fail2ban** — already running, has reasonable defaults for SSH. Don't reconfigure.
- **iptables directly** — ufw manages iptables for you. Editing `iptables` rules directly will conflict with ufw on the next `ufw reload`.
- **The Hetzner Cloud Firewall** — Jon removed it. If he wants it back, that's a separate UI task he'll handle.

## ⚠️ If something goes wrong mid-operation

- Lost both sessions but firewall in unknown state: Jon uses Hetzner web console (browser-based serial terminal), logs in as root (after his password reset earlier), runs `ufw disable` to clear all rules temporarily, then you both reconvene and re-apply cleanly.
- Rule mid-applied but locked out: same recovery path — Hetzner web console → `ufw disable` → start fresh.

The Hetzner web console is the always-available escape hatch because it's not affected by ufw or iptables.
