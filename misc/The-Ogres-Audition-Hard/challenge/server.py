import os
import re
import difflib
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel

app = FastAPI(title="The Ogre's Audition")

FLAG = os.environ.get("FLAG")
if not FLAG:
    raise RuntimeError("FLAG environment variable is required")
SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD", "0.70"))

SCRIPT_PATH = Path(__file__).parent / "shrek2_script_partial.txt"
REFERENCE_SCRIPT = SCRIPT_PATH.read_text(encoding="utf-8")


def normalize(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def compute_similarity(transcript: str, reference: str) -> float:
    """Compute word-level similarity between transcript and reference."""
    norm_transcript = normalize(transcript)
    norm_reference = normalize(reference)

    ref_words = norm_reference.split()
    trans_words = norm_transcript.split()

    matcher = difflib.SequenceMatcher(None, trans_words, ref_words)
    return matcher.ratio()


class TranscriptSubmission(BaseModel):
    transcript: str


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.get("/script")
async def get_script():
    return {"script": REFERENCE_SCRIPT}


@app.post("/submit")
async def submit_transcript(submission: TranscriptSubmission):
    transcript = submission.transcript.strip()

    if not transcript:
        return JSONResponse(
            status_code=400,
            content={"error": "Empty transcript. The Ogre heard nothing."},
        )

    similarity = compute_similarity(transcript, REFERENCE_SCRIPT)

    if similarity >= SIMILARITY_THRESHOLD:
        return {
            "success": True,
            "flag": FLAG,
            "similarity": round(similarity * 100, 2),
            "message": "The Ogre King is impressed! You have earned your passage.",
        }
    else:
        return {
            "success": False,
            "similarity": round(similarity * 100, 2),
            "message": f"The director is not impressed. You matched {round(similarity * 100, 1)}% of the Sacred Green Script. You need at least {round(SIMILARITY_THRESHOLD * 100)}%.",
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=1337)
