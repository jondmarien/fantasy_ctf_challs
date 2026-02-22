"""
Consolidated LLM Challenge Server
All 5 challenges served from one FastAPI app with path-based routing:
  /parrot/     — Beginner (The Enchanted Parrot)
  /merchant/   — Easy (The Whispering Merchant)
  /familiar/   — Medium (The Court Wizard's Familiar)
  /oracle/     — Hard (The Oracle of Shadows)
  /mindflayer/ — Expert (The Mindflayer's Sanctum)
"""

import os
import sys

# Add shared libs to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "shared"))

from fastapi import FastAPI

# Import challenge factories
from importlib.machinery import SourceFileLoader

BASE = os.path.dirname(__file__)


def _load_factory(challenge_dir: str):
    """Load create_app from a challenge's server.py."""
    path = os.path.join(BASE, challenge_dir, "challenge", "server.py")
    mod = SourceFileLoader(challenge_dir.replace("-", "_"), path).load_module()
    return mod.create_app


# Load factories
parrot_factory = _load_factory("The-Enchanted-Parrot-Beginner")
merchant_factory = _load_factory("The-Whispering-Merchant-Easy")
familiar_factory = _load_factory("The-Court-Wizards-Familiar-Medium")
oracle_factory = _load_factory("The-Oracle-of-Shadows-Hard")
mindflayer_factory = _load_factory("The-Mindflayers-Sanctum-Expert")

# Create sub-apps with per-challenge flags
parrot_app = parrot_factory(os.environ.get("FLAG_PARROT", ""))
merchant_app = merchant_factory(os.environ.get("FLAG_MERCHANT", ""))
familiar_app = familiar_factory(os.environ.get("FLAG_FAMILIAR", ""))
oracle_app = oracle_factory(os.environ.get("FLAG_ORACLE", ""))
mindflayer_app = mindflayer_factory(os.environ.get("FLAG_MINDFLAYER", ""))

# Root app
app = FastAPI(title="Fantasy CTF — LLM Challenges")


@app.get("/")
async def root():
    return {
        "challenges": {
            "parrot": "/parrot/ (Beginner)",
            "merchant": "/merchant/ (Easy)",
            "familiar": "/familiar/ (Medium)",
            "oracle": "/oracle/ (Hard)",
            "mindflayer": "/mindflayer/ (Expert)",
        }
    }


@app.get("/health")
async def health():
    return {"status": "ok", "service": "llm-challenges-consolidated"}


# Mount sub-applications
app.mount("/parrot", parrot_app)
app.mount("/merchant", merchant_app)
app.mount("/familiar", familiar_app)
app.mount("/oracle", oracle_app)
app.mount("/mindflayer", mindflayer_app)
