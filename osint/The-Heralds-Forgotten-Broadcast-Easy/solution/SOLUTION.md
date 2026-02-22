# Solution: The Herald's Forgotten Broadcast

## Category: OSINT | Difficulty: Easy | Points: 250

## Overview

Find a GitHub account from a username in the challenge file, then recover a deleted file from git history.

## Given Files

- `challenge/herald_note.txt` — Contains the alias `FantasyCTF-Herald-2026`.

## Steps

1. **Read the challenge file** — `herald_note.txt` provides the alias `FantasyCTF-Herald-2026`.

2. **Search GitHub** — The hint says "the world's largest code forge" = GitHub. Navigate to `https://github.com/FantasyCTF-Herald-2026`.

3. **Find the repository** — The account has a single repo called `royal-decrees`. The README says: *"The decree was sealed before it was published. Look to the past."*

4. **Check git history** — The current repo has no decree files, but the hint says "Git never truly forgets." View the commit history:

   ```bash
   git clone https://github.com/FantasyCTF-Herald-2026/royal-decrees.git
   cd royal-decrees
   git log --all --oneline
   git show HEAD~1:decree.txt
   ```

5. **Read the deleted file** — A previous commit called `Add classified decree` added `decree.txt`, which was later removed. The file contains the flag.

## Flag

```text
FantasyCTF{th3_h3r4ld_sp34ks_thr0ugh_t1m3}
```
