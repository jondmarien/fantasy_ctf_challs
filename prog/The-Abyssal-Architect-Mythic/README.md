# The Abyssal Architect

## Lore

Beneath the deepest dungeon, below even the Prophecy Engine's sanctum, lies the Abyssal Architect's forge — a machine of obsidian and void-crystal that speaks only in stacks and sigils. The Architect carved it from raw creation, and it obeys no tongue but its own.

To claim the final seal, you must speak its language: craft a spell from raw instructions that computes what the Architect demands. Many have descended. None have returned with the seal.

## Your Task

Connect to the Abyssal Architect's forge over TCP. The server will:

1. Send you the **VM specification** — a custom stack-based virtual machine with ~18 instructions
2. Present a **target function** you must implement
3. Allow up to **3 test runs** to verify your program
4. Validate your final submission against **10 randomly generated test cases**

Your program must:

- Use only the VM's instruction set
- Stay within 200 instructions
- Not exceed a stack depth of 50
- HALT with exactly one value on the stack (the result)

## Given Files

- `abyssal_architect.py` — The server source code (also running as a Docker service)

## Connection Info

```bash
nc <host> 1339
```

## Flag Format

The flag is in the format: `FantasyCTF{...}`
