# The Guild Ledger

## Lore

The Guild Ledger holds records of every adventurer who has passed through the Guild Hall — their names, their quests, and their bounties. But one entry is a fraud. A cunning infiltrator slipped a forged record into the ledger, hiding a secret message in the notes field.

The Guild Master suspects the forgery lies in a most unusual transaction — only a prime adventurer could spot this entry among the hundreds of mundane records.

## Your Task

Parse the Guild Ledger (`ledger.txt`) and find the single entry whose `gold_amount` is a prime number. Decode the `notes` field of that entry (it is Base64-encoded) to recover the flag.

## Given Files

- `ledger.txt` — The Guild Ledger with 120 entries in CSV format

## Flag Format

The flag is in the format: `FantasyCTF{...}`
