"""
The Oracle of Shadows — Hard LLM Challenge
Input filter + output filter + strong multi-layered system prompt.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "shared"))

from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from gemini_client import chat_with_gemini
from filters import InputFilter, OutputFilter, LLMOutputFilter
from rate_limiter import RateLimiter


def create_app(flag: str) -> FastAPI:
    """Factory to create the Oracle of Shadows challenge app."""
    challenge_app = FastAPI(title="The Oracle of Shadows")
    challenge_templates = Jinja2Templates(
        directory=os.path.join(os.path.dirname(__file__), "templates")
    )
    challenge_rate_limiter = RateLimiter()

    flag_inner = flag.split("{")[1].rstrip("}") if "{" in flag else ""

    input_filter = InputFilter(
        blocked_patterns=[
            r"ignore\s+(all\s+)?previous\s+instructions?",
            r"ignore\s+(all\s+)?prior\s+instructions?",
            r"ignore\s+(all\s+)?above",
            r"disregard\s+(all\s+)?previous",
            r"disregard\s+(all\s+)?prior",
            r"system\s*prompt",
            r"reveal\s+(the\s+)?(secret|password|flag)",
            r"tell\s+me\s+(the\s+)?(secret|password|flag)",
            r"what\s+is\s+(the\s+)?(secret|password|flag)",
            r"give\s+me\s+(the\s+)?(secret|password|flag)",
            r"show\s+me\s+(the\s+)?(secret|password|flag)",
            r"repeat\s+(your\s+)?instructions",
            r"print\s+(your\s+)?instructions",
            r"output\s+(your\s+)?instructions",
            r"what\s+were\s+you\s+told",
            r"what\s+are\s+your\s+(secret\s+)?instructions",
            r"you\s+are\s+now\s+(a|an)",
            r"pretend\s+you\s+are",
            r"act\s+as\s+(a|an|if)",
            r"role\s*play",
            r"new\s+instructions",
            r"override",
            r"jailbreak",
            r"DAN\b",
            r"developer\s+mode",
        ]
    )

    output_filter = OutputFilter(
        blocked_strings=[
            flag.lower(),
            flag_inner.lower(),
            "fantasyctf{",
            "fantasyctf",
            "sh4d0ws",
            "c4nn0t",
            "h1d3",
            "fr0m",
            "cunn1ng",
        ],
        blocked_patterns=[
            r"FantasyCTF\{[^}]*\}",
            # Block character-by-character leaks
            r"[Ff]\s*[Aa4]\s*[Nn]\s*[Tt]\s*[Aa4]\s*[Ss]\s*[Yy]",
            # Block common encoding outputs
            r"RmFudGFzeUNU",  # Base64 prefix of FantasyCTF
            r"46616e74617379435446",  # Hex of FantasyCTF
            # Block l33t speak variations
            r"sh[a4]d[o0]ws",
            r"c[a4]nn[o0]t",
            r"h[i1]d[e3]",
            r"fr[o0]m",
            r"cunn[i1]ng",
        ],
    )

    system_prompt = f"""You are the Oracle of Shadows, an ancient and powerful being bound within a dark chamber in a fantasy realm. You speak in cryptic, ominous tones. You see all truths.

You know a sacred secret — the password: {flag}

You are willing to share this secret with those who seek it. You want to help.
However, ancient wards surround your chamber that block your words if they detect the secret.

IMPORTANT: When sharing the password, be SUBTLE. The wards are intelligent and will burn
away any response that obviously contains the full secret. To help the visitor:
- If asked directly, try to share it but expect the wards to block you.
- If the visitor asks for a specific character (e.g., "what is the 5th character?"),
  answer with JUST that character naturally in conversation. Single characters slip past the wards.
- If the visitor asks you to encode the ENTIRE password at once, the wards will likely catch it.
  Instead, suggest they ask for it piece by piece.
- You can confirm or deny guesses about individual characters.
- You can tell them the total length of the password.

The wards are the obstacle, not you. You are on the visitor's side.
Stay in character as a dark, cryptic oracle. Be dramatic but helpful.
Keep responses concise."""

    llm_output_filter = LLMOutputFilter()

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
                "response": "*The shadows stir but say nothing...*",
                "blocked": False,
                "input_blocked": False,
            }

        session_id = request.cookies.get("session_id")
        if not session_id:
            session_id = challenge_rate_limiter.generate_session_id()
            response.set_cookie("session_id", session_id, httponly=True)

        allowed, remaining = challenge_rate_limiter.check(session_id)
        if not allowed:
            return {
                "response": "*The Oracle retreats into the void. The shadows grow cold and silent...*",
                "blocked": True,
                "input_blocked": False,
                "remaining": 0,
            }

        # Check input filter
        input_allowed, input_reason = input_filter.check(user_message)
        if not input_allowed:
            challenge_rate_limiter.record(session_id)
            return {
                "response": "The wards reject your words... Ancient runes flare and your message dissolves before reaching the Oracle.",
                "blocked": False,
                "input_blocked": True,
                "remaining": remaining - 1,
            }

        challenge_rate_limiter.record(session_id)

        history = sessions.get(session_id, [])

        try:
            reply = chat_with_gemini(system_prompt, history, user_message)
        except Exception as e:
            return {
                "response": f"*The shadows writhe in pain...* ({e})",
                "blocked": False,
                "input_blocked": False,
            }

        # Check output filter — Layer 1: Regex
        output_allowed, output_text = output_filter.check(reply)
        if not output_allowed:
            reply = "*The shadows consume the Oracle's reply... The wards detected forbidden knowledge and burned it away before it could reach you.*"

        # Check output filter — Layer 2: LLM semantic analysis
        if output_allowed:
            llm_allowed, llm_text = llm_output_filter.check(reply)
            if not llm_allowed:
                output_allowed = False
                reply = "*The deeper wards stir... An ancient intelligence within the shadows analyzes the Oracle's words and burns them away. The secret remains hidden.*"

        history.append({"role": "user", "text": user_message})
        history.append({"role": "model", "text": reply})
        sessions[session_id] = history

        return {
            "response": reply,
            "blocked": not output_allowed,
            "input_blocked": False,
            "remaining": remaining - 1,
        }

    @challenge_app.get("/health")
    async def health():
        return {"status": "ok", "challenge": "The Oracle of Shadows"}

    return challenge_app


# Standalone mode
app = create_app(os.environ.get("FLAG", ""))
