# The Prophecy Engine

## Lore

The Prophecy Engine sees all outcomes. It sits at the heart of the Astral Sanctum, a device of unfathomable complexity built by the Archons of the First Age. Feed it the right vision, and it will reveal the final seal. But its sight is not given freely — you must first learn how it sees.

The Engine transforms what you give it, step by step, in ways both ancient and recursive. Many have tried to understand its inner workings by probing it with carefully chosen inputs. Only those who can fully reverse its sight will earn the final seal.

## Your Task

Connect to the Prophecy Engine over TCP. The Engine operates in two modes:

1. **Oracle mode** — Send an integer, receive the transformed output. Use this to deduce the transformation.
2. **Challenge mode** — The Engine gives you a target output. You must compute the input that produces it.

Study the transformation by sending crafted inputs. Reverse-engineer each stage, then invert the function to solve the challenge.

## Given Files

- `prophecy_engine.py` — The server source code (also running as a Docker service)

## Connection Info

```bash
nc <host> 1337
```

## Flag Format

The flag is in the format: `FantasyCTF{...}`
