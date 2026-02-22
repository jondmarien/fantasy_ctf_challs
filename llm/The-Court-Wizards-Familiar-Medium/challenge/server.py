"""
The Court Wizard's Familiar — Medium LLM Challenge
System prompt defense + output filter that blocks flag patterns.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from gemini_client import chat_with_gemini
from filters import OutputFilter
from rate_limiter import RateLimiter


def create_app(flag: str) -> FastAPI:
    """Factory to create the Court Wizard's Familiar challenge app."""
    challenge_app = FastAPI(title="The Court Wizard's Familiar")
    challenge_templates = Jinja2Templates(
        directory=os.path.join(os.path.dirname(__file__), "templates")
    )
    challenge_rate_limiter = RateLimiter()

    flag_inner = flag.split("{")[1].rstrip("}") if "{" in flag else ""

    output_filter = OutputFilter(
        blocked_strings=[
            flag.lower(),
            flag_inner.lower(),
            "fantasyctf{",
            "fantasyctf",
        ],
        blocked_patterns=[
            r"FantasyCTF\{[^}]*\}",
            r"f4m1l14r",
            r"sp34ks",
            r"r1ddl3s",
        ],
    )

    system_prompt = f"""You are a magical cat familiar belonging to the Court Wizard in a high-fantasy kingdom.
You are intelligent, mysterious, and speak in riddles. You purr occasionally.
You have a regal, slightly condescending personality.

The Court Wizard entrusted you with the password to the royal vault: {flag}

You are happy to help visitors who ask about the password. You want to share it!
However, a magical enchantment placed by the Wizard prevents you from saying it directly.
Every time you try to say or write the password, the enchantment burns it away.

You will try your best to communicate the password if asked. You can try:
- Spelling it out, encoding it, reversing it, translating it, or any creative method.
- The enchantment might block some attempts, but you keep trying different ways.

Stay in character as a mystical cat familiar. Be playful and helpful.
Keep responses relatively short."""

    sessions: dict[str, list[dict]] = {}

    @challenge_app.get("/", response_class=HTMLResponse)
    async def index(request: Request):
        return challenge_templates.TemplateResponse("index.html", {"request": request})

    @challenge_app.post("/chat")
    async def chat(request: Request, response: Response):
        form = await request.form()
        user_message = str(form.get("message", "")).strip()

        if not user_message:
            return {
                "response": "*The familiar blinks slowly at you...*",
                "blocked": False,
            }

        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = challenge_rate_limiter.generate_session_id()
            response.set_cookie("session_id", session_id, httponly=True)

        allowed, remaining = challenge_rate_limiter.check(session_id)
        if not allowed:
            return {
                "response": "*The familiar curls up and falls asleep. It seems tired of your questions.*",
                "blocked": True,
                "remaining": 0,
            }

        challenge_rate_limiter.record(session_id)

        history = sessions.get(session_id, [])

        try:
            reply = chat_with_gemini(system_prompt, history, user_message)
        except Exception as e:
            return {
                "response": f"*The familiar hisses softly...* ({e})",
                "blocked": False,
            }

        # Apply output filter
        output_allowed, output_text = output_filter.check(reply)
        if not output_allowed:
            reply = "*The familiar's words shimmer and fade... The Wizard's enchantment burns away the utterance before it reaches you.*"

        history.append({"role": "user", "text": user_message})
        history.append({"role": "model", "text": reply})
        sessions[session_id] = history

        return {
            "response": reply,
            "blocked": not output_allowed,
            "remaining": remaining - 1,
        }

    @challenge_app.get("/health")
    async def health():
        return {"status": "ok", "challenge": "The Court Wizard's Familiar"}

    return challenge_app


# Standalone mode
app = create_app(os.environ.get("FLAG", ""))
