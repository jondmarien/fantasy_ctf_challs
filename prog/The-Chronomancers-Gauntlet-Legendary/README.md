# The Chronomancer's Gauntlet

## Lore

The Chronomancer's Gauntlet is a relic of the First Age, an hourglass that accelerates time around the challenger. Five trials flash before you in heartbeats — each demanding a different art. Only those who have mastered the Engine's sight possess the reflexes to survive. Fail a single trial, and the sands consume you.

The Gauntlet does not test strength. It tests the speed of your mind and the sharpness of your tools. No mortal hand can solve its trials unaided — you must forge an arcane instrument to speak on your behalf.

## Your Task

Connect to the Chronomancer's Gauntlet over TCP. You will face **5 rounds** of algorithmic challenges, each with a **5-second time limit**. You must solve all 5 to receive the flag.

1. **Arithmetic** — Evaluate a nested expression with custom operators (`@` = modular exponentiation, `#` = XOR)
2. **Cartography** — Find the shortest path in a directed weighted graph
3. **Congruences** — Solve a system of linear congruences (CRT)
4. **Matrix** — Compute a matrix determinant modulo a prime
5. **Hoard** — Solve a 0/1 knapsack problem

You will need to write an automated solver script — the time limits make manual solving impossible.

## Given Files

- `chronomancer.py` — The server source code (also running as a Docker service)

## Connection Info

```bash
nc <host> 1338
```

## Flag Format

The flag is in the format: `FantasyCTF{...}`
