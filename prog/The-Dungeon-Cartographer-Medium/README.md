# The Dungeon Cartographer

## Lore

A dungeon map was recovered from the pack of a fallen adventurer at the edge of the Abyssal Caverns. The map reveals a grid of chambers, each marked with a toll — the cost in gold to pass through. The treasure chamber lies at the far corner, but its door does not care for bravery, only for the *shortest* toll from entrance to exit.

The door will only open when fed the exact minimum cost of traversal. No more, no less.

## Your Task

You are given a weighted grid (`dungeon.txt`) representing the dungeon. Each cell contains a positive integer representing the cost to enter that cell. Find the minimum-cost path from the top-left corner `(0,0)` to the bottom-right corner `(N-1,N-1)`, moving only up, down, left, or right.

The flag is `FantasyCTF{<minimum_cost>}` where `<minimum_cost>` is the total cost of the cheapest path (including both the start and end cells).

## Given Files

- `dungeon.txt` — A 25x25 weighted grid (space-separated integers)
- `challenge.py` — A script that loads the grid and accepts your answer

## Flag Format

The flag is in the format: `FantasyCTF{<number>}`
