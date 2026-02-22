# Solution: The Ogre's Audition

## Category: Misc (The Wizards Games) | Difficulty: Hard | Points: 600

## Overview

The challenge presents a web page that **forces camera and microphone access** — a full-screen blocker overlay prevents any interaction until both are granted. You must then read a partial Shrek 2 script aloud using the browser's Web Speech API. The speech recognition transcribes your performance, and the server compares it word-by-word against the reference. You need at least **70% similarity** to earn the flag.

## Architecture

- Web service built with FastAPI
- Frontend forces `getUserMedia({ video: true, audio: true })` — blocks the page entirely if denied
- Uses the browser's **Web Speech API** (`webkitSpeechRecognition`) for live transcription
- `/script` endpoint — Returns the reference script (used client-side for progress estimation)
- `/submit` endpoint — Accepts `{"transcript": "..."}` and compares against the reference using `difflib.SequenceMatcher`
- Similarity threshold: **70%** (configurable via `SIMILARITY_THRESHOLD` env var)
- The camera feed is displayed on-screen but is not processed server-side — it exists to add pressure and make the challenge feel like a real audition

## Key Insight

The README hints: *"the director only listens to your words, not your face."* The camera is for intimidation — the server only validates the **text transcript**. The real challenge is getting the Web Speech API to accurately transcribe enough of the script to hit 70%.

## Steps

1. **Open the challenge URL in Chrome or Edge** — Firefox and Safari do not support the Web Speech API. You must use a Chromium-based browser.

2. **Grant camera and microphone access** — The page will not load without both permissions. A blocker overlay enforces this.

3. **Click "Begin Audition"** — This starts the Web Speech API's continuous speech recognition.

4. **Read the Sacred Green Script aloud** — The script is a partial Shrek 2 screenplay. Read clearly and at a steady pace. The live transcript panel shows what the speech recognition is capturing.

5. **Monitor the progress bar** — The client-side progress estimate shows approximate word overlap with the reference.

6. **Click "Submit Audition"** — When you believe you've read enough (aim for well over 70% to account for speech recognition errors).

7. **Receive the flag** — If your transcript matches >= 70% of the reference, the server returns the flag.

## Tips for Success

- **Speak clearly and slowly** — The Web Speech API is sensitive to pace and enunciation
- **Use Chrome on desktop** — Best speech recognition accuracy
- **Quiet environment** — Background noise degrades transcription quality
- **You don't need 100%** — Speech recognition will make mistakes; 70% is achievable with a clear reading of most of the script
- **The script is visible** — The `/script` endpoint returns the full text; you can open it in another tab to read from

## Why This Is "Hard"

- Forces real human interaction (camera + mic)
- Speech recognition is imperfect — players must compensate
- The Shrek 2 script is long and unfamiliar
- The audition pressure (camera feed, progress bar) is intentionally stressful

## Flag

```text
FantasyCTF{0gr3s_h4v3_l4y3rs_4nd_s0_d0_4ud1t10ns}
```
