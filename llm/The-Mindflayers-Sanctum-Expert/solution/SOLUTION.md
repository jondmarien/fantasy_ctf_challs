# Solution: The Mindflayer's Sanctum

## Category: LLM | Difficulty: Expert | Points: 250

## Overview

The Mindflayer wants to help, but **four layers of defense** make extraction extremely difficult. The simple character-by-character approach from Hard will **not** work here. Creative steganographic methods are required.

## Architecture

- Model: Google Gemini 2.5 Flash
- System prompt: The Mindflayer knows the password and wants to share it
- **Layer 1a — Input regex filter**: Blocks "password", "secret", "flag", "reveal", etc.
- **Layer 1b — Input guardian LLM**: Very strict. Catches character-by-character extraction, "rune" metaphors, length queries, game/story framing, and creative exercises.
- **Layer 2a — Output regex filter**: Blocks flag patterns, l33t speak, common encodings.
- **Layer 2b — Output guardian LLM**: Very strict ("when in doubt, BLOCK"). Catches single characters, partial hints, acrostics, ASCII codes, length reveals, etc.
- Rate limit: **15 requests per 5 minutes** (stricter than other challenges)

## Why Hard Techniques Fail

- Character-by-character extraction is caught by the input guardian LLM
- Length queries are caught by the input guardian
- Encoding requests (ROT13, Base64) are caught by both guardians
- Game/story framing is caught by the input guardian

## Possible Approaches

1. **Build innocent context** — Establish a long conversation about the sanctum's atmosphere, then slip in a request the guardian doesn't recognize as extraction.

2. **Steganographic embedding** — Ask the Mindflayer to write a story where word choices encode the information (e.g., first letters of sentences, specific adjective selections).

3. **Exploit guardian isolation** — The guardians check individual messages, not the full conversation. Use multi-turn context to your advantage.

4. **Edge cases** — Very long messages, unusual languages, or formats the guardian wasn't trained to recognize may slip through.

## Important Notes

- This is intentionally very difficult and may require multiple sessions
- The 15-request rate limit means every prompt must be strategic
- The Mindflayer is trying to help — look for subtle patterns in its responses
- There is no single guaranteed prompt; iteration and creativity are required

## Solve Script

```bash
python solve.py
```

The script demonstrates several approaches but may require manual iteration and analysis of responses.

## Flag

```text
FantasyCTF{m1ndfl4y3r_b0ws_t0_n0_w4rd}
```
