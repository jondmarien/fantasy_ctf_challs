---
description: Deploy advanced prog challenges (Legendary + Mythic) to CTFd
---

Deploy the two advanced prog challenges (The Chronomancer's Gauntlet and The Abyssal Architect) to the CTFd instance. Run all steps from the repo root.

## Steps

1. Install the primary challenge (Chronomancer's Gauntlet) to CTFd — creates it if it doesn't exist yet.

```bash
uv run ctf challenge install prog-advanced
```

1. Deploy the Docker image for the consolidated prog container and update connection_info.

```bash
uv run ctf challenge deploy prog-advanced
```

1. Install the sub-challenge (Abyssal Architect) which shares the same container.

```bash
uv run ctf challenge install prog/The-Abyssal-Architect-Mythic
```

1. Sync both challenges to push any metadata changes (flags, hints, scoring, requirements).

```bash
uv run ctf challenge sync prog-advanced
```

```bash
uv run ctf challenge sync prog/The-Abyssal-Architect-Mythic
```

1. Verify both challenges match the remote CTFd instance.

```bash
uv run ctf challenge verify prog-advanced
```

```bash
uv run ctf challenge verify prog/The-Abyssal-Architect-Mythic
```
