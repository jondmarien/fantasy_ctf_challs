# Terminal agent brief — deploy custom CTFd theme

**Context:** Cursor built a custom CTFd theme in a separate repo (`jondmarien/fantasy-ctfd-theme`) and added a bind-mount to the production docker-compose. Your job is to clone the theme repo onto the VPS into the bind-mount source path, then recreate the CTFd container so the new mount applies. Jon then activates the theme via the admin UI.

**Companion docs:**
- `DESIGN_OVERHAUL_BRIEF.md` — the design plan Cursor's executing
- `VPS_OPERATIONS.md` — broader operational reference

**Run as `ctf` user on the VPS.**

---

## Where this fits in the sequence

```
Cursor: builds theme in fantasy-ctfd-theme repo
     + adds bind-mount to fantasy_ctf_challs/infra/docker-compose.prod.yml
     + pushes both
                                  │
                                  ▼
       You (this doc): pull monorepo, clone theme repo, recreate CTFd container
                                  │
                                  ▼
       Jon: admin UI → Config → Theme → select "fantasy" → save
```

Jon is blocked on your part until the container recreate finishes and `fantasy` appears in the admin dropdown.

---

## Preconditions

Before starting, confirm:

- [ ] Cursor's monorepo PR is merged to `feat/hosting`. The PR adds a volume line under the `ctfd` service in `infra/docker-compose.prod.yml`. Confirm by checking the commit on GitHub or via `git log`.
- [ ] Cursor's `fantasy-ctfd-theme` repo exists and has built assets committed (the `static/` directory must be present in the repo, not gitignored).
- [ ] Jon has admin access to `https://api.ctf.chron0.tech/admin`.

If any of these are false: stop and tell Jon.

---

## Step 1 — Pull the monorepo (gets the new bind-mount)

```bash
cd /opt/fantasy_ctf_challs
git fetch origin
git checkout feat/hosting
git pull origin feat/hosting

# Confirm the volume line is now in the compose:
grep -A 1 'CTFd/themes' infra/docker-compose.prod.yml
# Expect something like:
#   - ./ctfd/themes/fantasy:/opt/CTFd/CTFd/themes/fantasy:ro
```

If the grep returns nothing: Cursor's PR didn't land or you're on the wrong branch. Don't proceed.

---

## Step 2 — Clone the theme repo BEFORE recreating the container

**Order matters.** If you recreate the container first, Docker auto-creates the bind-mount source path as an empty directory owned by `root`. Then `git clone` fails because you don't have write access, and you'd need `sudo` (the bootstrap explicitly didn't give `ctf` broad sudo for that reason).

So: clone first, then recreate.

```bash
# Make sure the parent directory exists and is owned by ctf:
mkdir -p /opt/fantasy_ctf_challs/infra/ctfd/themes

# Clone the theme repo into the path the bind-mount expects:
cd /opt/fantasy_ctf_challs/infra/ctfd/themes
git clone https://github.com/jondmarien/fantasy-ctfd-theme.git fantasy

# Confirm the static/ directory is present (CTFd needs the built assets):
ls fantasy/static/ 2>&1 | head -5
# Expect: assets/, manifest.json, manifest-css.json, possibly index.html

# If static/ is missing or empty: the theme wasn't built before commit.
# Stop and tell Jon — Cursor needs to run `yarn build` and re-push.
```

---

## Step 3 — Recreate the CTFd container so the bind-mount applies

A plain `restart` doesn't apply new volume definitions — only `up -d` with `--force-recreate` (or stopping and starting) does.

```bash
cd /opt/fantasy_ctf_challs/infra
docker compose -f docker-compose.prod.yml up -d --force-recreate ctfd

# Wait for CTFd to be ready (10-15s for boot):
sleep 12

# Confirm the new mount is live inside the container:
docker exec $(docker compose -f docker-compose.prod.yml ps -q ctfd) \
  ls /opt/CTFd/CTFd/themes/

# Expect to see at least: core, core-beta, fantasy
# If "fantasy" is missing, the bind-mount didn't take. See troubleshooting below.
```

---

## Step 4 — Verify CTFd recognises the theme

```bash
# CTFd scans themes/ on every request. Hit the admin themes endpoint:
docker exec $(docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml ps -q ctfd) \
  ls /opt/CTFd/CTFd/themes/fantasy/templates/ 2>&1 | head -10

# Should list: base.html, challenges.html, etc.
# If empty or "No such file": the bind-mount points at a directory but the directory
# is empty — the git clone didn't put files where expected. Re-check Step 2.
```

Also confirm CTFd didn't error on startup:

```bash
docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml \
  logs ctfd --tail=100 2>&1 | grep -iE "error|exception|traceback" | head -20
```

Any plugin errors mentioning "theme" or "manifest" — capture and send to Jon. Otherwise proceed.

---

## Step 5 — Report back to Jon

Paste:

- Output of `ls fantasy/` (host side) showing `templates/`, `static/`, `assets/`, `package.json` are present
- Output of `docker exec ... ls /opt/CTFd/CTFd/themes/` (container side) confirming `fantasy` appears
- Any error log lines from Step 4 (if none, say "no errors")

Then Jon activates the theme in the admin UI. You're done from the VPS side.

---

## Ongoing — How to update the theme

After the initial install, Cursor will push design changes to the theme repo. To deploy each update:

```bash
cd /opt/fantasy_ctf_challs/infra/ctfd/themes/fantasy
git pull origin main

# That's it. NO container restart needed.
# CTFd's theme loader scans templates on each request, and the bind-mount
# is read-through. Hard-refresh in Jon's browser shows the new version.
```

Exception: if Cursor changed `vite.config.js` in ways that alter asset filenames or the manifest, CTFd may cache the old manifest in-memory. In that case:

```bash
docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml restart ctfd
```

That's the only case you'd restart.

---

## Rollback

If something breaks after a theme update:

```bash
# Roll back to the previous version:
cd /opt/fantasy_ctf_challs/infra/ctfd/themes/fantasy
git log --oneline -5             # find the previous good SHA
git checkout <previous-sha>      # detached HEAD on the known-good version
# Page reload → site reverts. No restart needed.
```

Or, more drastic — switch theme back to core via admin UI (Config → Theme → "core" → Save). Tell Jon to do that if any catastrophic failure makes the site unusable; takes 5 seconds and is fully reversible.

---

## Troubleshooting

### `fantasy` directory exists on host but not in container

The bind-mount didn't apply. Likely because you ran `docker compose restart` instead of `up -d --force-recreate`. Re-run Step 3 with `--force-recreate`.

### `fantasy` directory exists in container but is empty

The host-side directory was created (probably by Docker auto-creating it when the container recreated before you cloned). The clone went somewhere else or didn't happen.

```bash
ls /opt/fantasy_ctf_challs/infra/ctfd/themes/fantasy/
# If empty: rm -rf the empty dir, then re-do Step 2 (clone) before Step 3.
# If owned by root: needs sudo to remove. Tell Jon — he has the password.
```

### Theme appears in dropdown but pages render broken

Open browser DevTools → Network tab → reload a CTFd page. Look for:

- 404 on hashed asset filenames (e.g. `assets/index.abc123.js`): the `static/` directory is missing or stale. Verify `ls fantasy/static/` on the host.
- 500 from CTFd: a Jinja template error. Get the traceback:
  ```bash
  docker compose -f /opt/fantasy_ctf_challs/infra/docker-compose.prod.yml \
    logs ctfd --tail=200 2>&1 | grep -A 20 -i "traceback"
  ```
  Send the traceback to Jon — Cursor needs to fix the template.

### Admin theme dropdown doesn't show `fantasy`

CTFd reads themes on every request, but the dropdown might be cached client-side in the admin UI. Tell Jon to hard-refresh the admin page. If still missing after a hard refresh: the container can't actually see the theme directory (Step 4 verification should have caught this).

---

## ⚠️ Don't touch

- **The contents of the theme repo itself** — that's Cursor's territory. You only `git pull`, never edit files inside `infra/ctfd/themes/fantasy/`.
- **`/etc/sshd_config` or `ufw`** — unrelated to themes.
- **CTFd's `core` or `core-beta` theme directories** inside the container — those ship with CTFd's image and aren't supposed to be modified.
- **The admin's theme selector** — that's Jon's web-UI step, not yours. You verify the theme is *available*; he activates it.

## ⚠️ Safety reminders

- Don't run `docker compose down -v` (the `-v` deletes volumes including the CTFd uploads + Postgres data).
- Don't `git pull --rebase` or `git reset --hard` on the monorepo if you have local uncommitted state (unlikely, since you're operating as ctf user with read-only intent on the monorepo, but worth being explicit).
- If the theme directory's git state diverges from upstream (`git status` shows local commits or modifications), STOP and tell Jon. The VPS should never have local theme edits — that's a sign someone hand-edited a template file directly on the box, which gets blown away by the next `git pull`.

---

## Quick reference

| Task | Command |
|---|---|
| Initial theme deploy | `git clone https://github.com/jondmarien/fantasy-ctfd-theme infra/ctfd/themes/fantasy && docker compose up -d --force-recreate ctfd` |
| Update theme | `cd infra/ctfd/themes/fantasy && git pull` |
| Roll back theme | `cd infra/ctfd/themes/fantasy && git checkout <sha>` |
| Restart CTFd (only if manifest cached) | `docker compose -f infra/docker-compose.prod.yml restart ctfd` |
| Check theme files visible in container | `docker exec $(docker compose -f infra/docker-compose.prod.yml ps -q ctfd) ls /opt/CTFd/CTFd/themes/fantasy/templates/` |
| Tail CTFd logs for theme errors | `docker compose -f infra/docker-compose.prod.yml logs -f --tail 100 ctfd` |
