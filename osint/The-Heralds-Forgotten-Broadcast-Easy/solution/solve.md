# Solution: The Herald's Forgotten Broadcast

## Difficulty: Easy (250 pts)

## Technique: Username Enumeration → GitHub → Git History

### Steps

1. **Read the challenge file** — `herald_note.txt` contains the alias `FantasyCTF-Herald-2026`.

2. **Search for the username** — The hint says "the world's largest code forge" → GitHub. Navigate to:

   ```
   https://github.com/FantasyCTF-Herald-2026
   ```

3. **Find the repository** — The account has a single repo called `royal-decrees`. The README says:
   > *"The decree was sealed before it was published. Look to the past."*

4. **Check git history** — The current repo has no decree files, but the hint says "Git never truly forgets." Click on the commit history (or clone the repo and run `git log`). You'll see a previous commit called `Add classified decree` that added a file called `decree.txt`.

5. **View the old commit** — Click on the commit or run:

   ```bash
   git clone https://github.com/FantasyCTF-Herald-2026/royal-decrees.git
   cd royal-decrees
   git log --all --oneline
   git show HEAD~1:decree.txt
   ```

6. **Read the decree** — The deleted `decree.txt` contains the flag:

```
FantasyCTF{th3_h3r4ld_sp34ks_thr0ugh_t1m3}
```
