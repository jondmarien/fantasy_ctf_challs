"""
The Ogre's Audition — Solve Instructions

This challenge CANNOT be solved with an automated script.
The frontend forces camera + microphone access via a blocker overlay.
You must use a real browser (Chrome/Edge) with a working camera and mic.

Intended solve:
  1. Open the challenge URL in Chrome or Edge
  2. Grant camera and microphone permissions (page blocks without them)
  3. Click "Begin Audition" to start speech recognition
  4. Read the Sacred Green Script (partial Shrek 2 screenplay) aloud
  5. Click "Submit Audition" when the progress bar shows ~70%+
  6. The server compares your transcript to the reference via difflib
  7. If similarity >= 70%, the flag is returned

Tips:
  - Speak clearly and at a steady pace
  - Use a quiet environment for best speech recognition accuracy
  - The /script endpoint returns the full reference text — open it in
    another tab to read from
  - You don't need 100% — speech recognition errors are expected

Helper: This script can fetch the reference script for you to read from.
"""

import requests
import sys

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:1337"


def solve():
    # Fetch the reference script so you can read it aloud
    print("[*] Fetching the Sacred Green Script for you to read aloud...")
    resp = requests.get(f"{BASE_URL}/script")
    resp.raise_for_status()
    script = resp.json()["script"]
    print(f"[*] Got {len(script.split())} words of script text\n")
    print("=" * 60)
    print("READ THE FOLLOWING ALOUD IN YOUR BROWSER:")
    print("=" * 60)
    print(script)
    print("=" * 60)
    print(f"\n[*] Total words: {len(script.split())}")
    print("[*] Open the challenge URL in Chrome/Edge, grant camera+mic,")
    print("[*] click 'Begin Audition', and read the above text aloud.")
    print("[*] Submit when the progress bar shows ~70%+.")


if __name__ == "__main__":
    solve()
