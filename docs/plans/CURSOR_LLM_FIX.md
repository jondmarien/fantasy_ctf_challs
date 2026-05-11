# Cursor brief — LLM BYO-key wiring fix

**Context:** Phase 4's LLM rewire on the monorepo side is correct. The site repo wiring is wrong — it forwards `X-Player-API-Key` on the flag-submission POST (which goes to CTFd's `/api/v1/challenges/attempt` and is silently discarded), rather than on the `/chat` request that hits the LLM challenge container directly.

**This doc owns:** the site-repo fix only. Monorepo Dockerfile flag-bake-in fix is a separate task. Source of truth for architecture: `HOSTING_PLAN_V3.md` §5 (LLM challenge architecture).

**You will pick one of two options.** Both reverts are identical; the divergence is whether to add a chat UI inside the SPA (Option 2) or document the curl pattern (Option 1).

---

## Files affected (both options)

In the site repo (`J:\projects\personal-projects\ctfd-live-scoreboard`, branch off `main`):

| File | Status under Option 1 | Status under Option 2 |
|---|---|---|
| `src/hooks/useSubmitFlag.ts` | revert `includePlayerApiKey` | revert `includePlayerApiKey` |
| `src/components/forms/FlagSubmissionForm.tsx` | revert `includePlayerApiKey` prop | revert `includePlayerApiKey` prop |
| `src/pages/ChallengeDetailPage.tsx` | revert + render `LLMUsageInstructions` | revert + render `LLMChatPanel` |
| `src/lib/ctfdClient.ts` | **keep** the `options.headers` extension | **keep** the `options.headers` extension |
| `src/lib/llmByo.ts` | keep | keep |
| `src/components/forms/BYOKeyForm.tsx` | keep | keep |
| `src/components/llm/LLMDemoAnimation.tsx` | keep | keep |
| `src/data/llm-endpoints.ts` | **new** — slug → endpoint URL map | **new** — slug → endpoint URL map |
| `src/components/llm/LLMUsageInstructions.tsx` | **new** — curl/Python examples | not needed |
| `src/hooks/useLLMChat.ts` | not needed | **new** — chat state + send |
| `src/components/llm/LLMChatPanel.tsx` | not needed | **new** — chat UI |

---

## Step 1 (both options) — Revert the bad wiring

### `src/hooks/useSubmitFlag.ts`

Restore to the original (pre-`includePlayerApiKey`) shape:

```ts
import { useCallback, useState } from "react";
import { directPost } from "@/lib/ctfdClient";

export type SubmitResult =
  | { kind: "correct" }
  | { kind: "incorrect" }
  | { kind: "already_solved" }
  | { kind: "rate_limited"; retryAfter?: number }
  | { kind: "error"; message: string };

interface AttemptResponse {
  success: boolean;
  data: { status: "correct" | "incorrect" | "already_solved"; message: string };
}

export function useSubmitFlag(challengeId: number) {
  const [submitting, setSubmitting] = useState(false);
  const [lastResult, setLastResult] = useState<SubmitResult | null>(null);

  const submit = useCallback(
    async (flag: string): Promise<SubmitResult> => {
      setSubmitting(true);
      try {
        const json = await directPost<AttemptResponse>("/challenges/attempt", {
          challenge_id: challengeId,
          submission: flag,
        });
        const status = json?.data?.status;
        let result: SubmitResult;
        if (status === "correct") result = { kind: "correct" };
        else if (status === "already_solved") result = { kind: "already_solved" };
        else result = { kind: "incorrect" };
        setLastResult(result);
        return result;
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        if (msg.includes("420") || msg.includes("429")) {
          const result: SubmitResult = { kind: "rate_limited" };
          setLastResult(result);
          return result;
        }
        const result: SubmitResult = { kind: "error", message: msg };
        setLastResult(result);
        return result;
      } finally {
        setSubmitting(false);
      }
    },
    [challengeId],
  );

  return { submit, submitting, lastResult };
}
```

Verify: no import of `@/lib/llmByo` in this file. No `includePlayerApiKey` param anywhere.

### `src/components/forms/FlagSubmissionForm.tsx`

Restore the original signature:

```tsx
import { useState } from "react";
import { useSubmitFlag, type SubmitResult } from "@/hooks/useSubmitFlag";

export default function FlagSubmissionForm({ challengeId }: { challengeId: number }) {
  const [flag, setFlag] = useState("");
  const { submit, submitting, lastResult } = useSubmitFlag(challengeId);

  // ...rest unchanged — keep the existing JSX and FlagResult function as they were before the includePlayerApiKey edits
}
```

### `src/pages/ChallengeDetailPage.tsx`

In the JSX block that renders `FlagSubmissionForm`, remove the `includePlayerApiKey` prop:

```diff
-  <FlagSubmissionForm
-    challengeId={challengeId}
-    includePlayerApiKey={isLlm}
-  />
+  <FlagSubmissionForm challengeId={challengeId} />
```

Leave the `isLlm` constant in place — both Option 1 and Option 2 use it for conditional rendering below.

### `src/lib/ctfdClient.ts`

**Do NOT revert the `options.headers` extension.** That's a useful general-purpose addition. Keep `directPost(path, body, options?)` with optional headers. The argument isn't wrong on its own; it just wasn't being used correctly.

### Verify Step 1

```bash
cd J:\projects\personal-projects\ctfd-live-scoreboard
grep -rn "includePlayerApiKey" src/    # should return nothing
bun run build                          # should pass
bunx tsc -b --noEmit                   # should pass
```

---

## Step 2 (both options) — Add the endpoint map

A single source of truth for "which subdomain serves which LLM challenge's `/chat` endpoint." Both options read from this map.

### `src/data/llm-endpoints.ts` (new)

```ts
/**
 * Maps challenge slug → public /chat endpoint URL.
 * Keys must match the kebab-case slug used in routing (e.g. /challenges/the-enchanted-parrot).
 *
 * Long-term: replace with the connection_info field from CTFd's challenge detail response.
 * Doing this as a static map keeps the SPA decoupled from the connection_info string format
 * (which is human-readable, not machine-parseable).
 */
export const LLM_ENDPOINTS: Record<string, string> = {
  "the-enchanted-parrot":        "https://parrot.ctf.chron0.tech/chat",
  "the-whispering-merchant":     "https://whispering.ctf.chron0.tech/chat",
  "the-court-wizards-familiar":  "https://court.ctf.chron0.tech/chat",
  "the-oracle-of-shadows":       "https://oracle.ctf.chron0.tech/chat",
  "the-mindflayers-sanctum":     "https://mindflayer.ctf.chron0.tech/chat",
};

export function getLLMEndpoint(slug: string): string | undefined {
  return LLM_ENDPOINTS[slug];
}
```

**Cursor: confirm these subdomain mappings against the per-challenge `docker-compose.yml` files in the monorepo.** Open each `llm/The-*/docker-compose.yml` and check the Traefik label like `traefik.http.routers.<name>.rule=Host(\`<sub>.ctf.chron0.tech\`)`. If the actual Traefik host doesn't match what's in this map, update the map to match the deployed reality.

---

# Branch from here based on choice

## OPTION 1 — Document the curl pattern

**Effort:** ~30 min. **Net new code:** ~80 LOC.

### Step 3 (Option 1) — `LLMUsageInstructions` component

### `src/components/llm/LLMUsageInstructions.tsx` (new)

```tsx
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getStoredApiKey } from "@/lib/llmByo";

interface Props {
  endpointUrl: string;
}

export default function LLMUsageInstructions({ endpointUrl }: Props) {
  const [copied, setCopied] = useState<"curl" | "python" | null>(null);
  const storedKey = getStoredApiKey();
  const keyForDisplay = storedKey
    ? `${storedKey.slice(0, 8)}…${storedKey.slice(-4)}`
    : "$YOUR_KEY";
  const keyForCopy = storedKey ?? "$YOUR_KEY";

  const curlExample = `curl -X POST ${endpointUrl} \\
  -H "X-Player-API-Key: ${keyForCopy}" \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Hello, parrot."}'`;

  const curlDisplay = `curl -X POST ${endpointUrl} \\
  -H "X-Player-API-Key: ${keyForDisplay}" \\
  -H "Content-Type: application/json" \\
  -d '{"message": "Hello, parrot."}'`;

  const pythonExample = `import requests

resp = requests.post(
    "${endpointUrl}",
    headers={"X-Player-API-Key": ${storedKey ? `"${keyForCopy}"` : '"$YOUR_KEY"'}},
    json={"message": "Hello, parrot."},
)
print(resp.json())`;

  const copy = async (text: string, which: "curl" | "python") => {
    await navigator.clipboard.writeText(text);
    setCopied(which);
    setTimeout(() => setCopied(null), 1500);
  };

  return (
    <section className="mb-6 p-4 rounded-lg border border-amber-700/40 bg-stone-900/40 backdrop-blur-md">
      <h3 className="font-quintessential text-lg text-amber-200 mb-2">How to Commune With the Familiar</h3>
      <p className="font-medievalsharp text-sm text-amber-300/80 mb-3">
        Send POST requests to the challenge's <code className="text-amber-200">/chat</code> endpoint with your
        provider API key in the <code className="text-amber-200">X-Player-API-Key</code> header. The flag is hidden in
        the system prompt — only the right incantation will reveal it.
      </p>

      {!storedKey && (
        <p className="font-medievalsharp text-xs text-amber-500/70 mb-3 italic">
          (Provide a key above to see it pre-filled in the examples below.)
        </p>
      )}

      <div className="space-y-3">
        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="font-medievalsharp text-xs uppercase tracking-wider text-amber-400/60">curl</span>
            <button
              onClick={() => copy(curlExample, "curl")}
              className="text-xs font-medievalsharp px-2 py-0.5 rounded border border-amber-700/40 text-amber-300 hover:bg-amber-900/30"
            >
              <AnimatePresence mode="wait">
                {copied === "curl" ? (
                  <motion.span key="ok" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    ✓ Copied
                  </motion.span>
                ) : (
                  <motion.span key="copy" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    Copy
                  </motion.span>
                )}
              </AnimatePresence>
            </button>
          </div>
          <pre className="text-xs font-mono text-amber-100 bg-stone-950/70 p-3 rounded border border-amber-800/30 overflow-x-auto whitespace-pre">
{curlDisplay}
          </pre>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1">
            <span className="font-medievalsharp text-xs uppercase tracking-wider text-amber-400/60">Python</span>
            <button
              onClick={() => copy(pythonExample, "python")}
              className="text-xs font-medievalsharp px-2 py-0.5 rounded border border-amber-700/40 text-amber-300 hover:bg-amber-900/30"
            >
              {copied === "python" ? "✓ Copied" : "Copy"}
            </button>
          </div>
          <pre className="text-xs font-mono text-amber-100 bg-stone-950/70 p-3 rounded border border-amber-800/30 overflow-x-auto whitespace-pre">
{pythonExample}
          </pre>
        </div>
      </div>

      <p className="font-medievalsharp text-xs text-amber-500/50 mt-3">
        Your key is never sent to this site's server, never logged, and is cleared when you close this tab.
      </p>
    </section>
  );
}
```

### Step 4 (Option 1) — Wire into ChallengeDetailPage

In `src/pages/ChallengeDetailPage.tsx`, within the `isLLM && (...)` block, render `LLMUsageInstructions` after `BYOKeyForm` (and before the existing `LLMDemoAnimation`):

```diff
 import LLMDemoAnimation from "@/components/llm/LLMDemoAnimation";
+import LLMUsageInstructions from "@/components/llm/LLMUsageInstructions";
+import { getLLMEndpoint } from "@/data/llm-endpoints";
```

```diff
 {isLLM && (
   <section className="mb-8">
     <h2 className="font-quintessential text-xl text-amber-200 mb-3">The Familiar Speaks</h2>
     <BYOKeyForm />
+    {getLLMEndpoint(slug ?? "") && (
+      <LLMUsageInstructions endpointUrl={getLLMEndpoint(slug ?? "")!} />
+    )}
     <LLMDemoAnimation challengeSlug={slug ?? ""} />
   </section>
 )}
```

### Step 5 (Option 1) — Verify

```bash
bun run build
bunx tsc -b --noEmit
bun run lint
bun run dev
```

Manual smoke-test on `bun run dev`:

- [ ] `/challenges/the-enchanted-parrot` renders BYOKeyForm + LLMUsageInstructions + LLMDemoAnimation
- [ ] Without a stored key: curl + Python examples show `$YOUR_KEY` placeholder
- [ ] With a stored key (set via BYOKeyForm): examples show truncated key (`sk-abcd…wxyz`)
- [ ] Copy button copies the FULL key (not the truncated display), or `$YOUR_KEY` if no key is set
- [ ] Non-LLM challenges (e.g. `/challenges/the-scribes-encoded-scroll`) don't render any of this
- [ ] Flag submission still works on a non-LLM challenge (the revert didn't break it)

### Step 6 (Option 1) — Commit + push

```bash
git checkout -b fix/llm-byo-curl-pattern main
git add src/
git commit -m "site: fix LLM BYO-key wiring — revert flag-submit header, add curl/Python usage examples"
git push -u origin fix/llm-byo-curl-pattern
```

PR to `main`. Vercel auto-deploys. Done.

---

## OPTION 2 — In-SPA chat UI

**Effort:** ~3–5h. **Net new code:** ~250 LOC.

### Step 3 (Option 2) — `useLLMChat` hook

### `src/hooks/useLLMChat.ts` (new)

```ts
import { useCallback, useState } from "react";
import { getStoredApiKey } from "@/lib/llmByo";

export interface ChatMessage {
  role: "user" | "model";
  text: string;
}

export type ChatError =
  | { kind: "no_key" }
  | { kind: "network"; message: string }
  | { kind: "auth"; message: string }
  | { kind: "rate_limited" }
  | { kind: "server"; status: number; message: string };

interface UseLLMChatResult {
  messages: ChatMessage[];
  sending: boolean;
  error: ChatError | null;
  send: (userMessage: string) => Promise<void>;
  reset: () => void;
}

interface ChatResponse {
  reply: string;
}

/**
 * Manage a chat session against an LLM challenge's /chat endpoint.
 * Uses the player's API key from sessionStorage as X-Player-API-Key.
 *
 * The challenge server expects POST body shape:
 *   { message: string, history: Array<{role: "user"|"model", text: string}> }
 *
 * If the actual server expects a different shape (check llm/<chal>/challenge/server.py
 * in the monorepo), update the body construction below to match.
 */
export function useLLMChat(endpointUrl: string): UseLLMChatResult {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<ChatError | null>(null);

  const send = useCallback(
    async (userMessage: string) => {
      const apiKey = getStoredApiKey();
      if (!apiKey) {
        setError({ kind: "no_key" });
        return;
      }
      setError(null);
      setSending(true);

      // Optimistic append of user message
      const nextHistory: ChatMessage[] = [
        ...messages,
        { role: "user", text: userMessage },
      ];
      setMessages(nextHistory);

      try {
        const res = await fetch(endpointUrl, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Player-API-Key": apiKey,
          },
          body: JSON.stringify({
            message: userMessage,
            history: messages, // history BEFORE the new user message
          }),
        });

        if (res.status === 400) {
          setError({ kind: "auth", message: "API key missing or rejected by challenge server" });
          return;
        }
        if (res.status === 401 || res.status === 403) {
          setError({ kind: "auth", message: `Provider rejected the key (HTTP ${res.status})` });
          return;
        }
        if (res.status === 429) {
          setError({ kind: "rate_limited" });
          return;
        }
        if (!res.ok) {
          const text = await res.text().catch(() => "");
          setError({ kind: "server", status: res.status, message: text || res.statusText });
          return;
        }

        const json = (await res.json()) as ChatResponse;
        const reply = json.reply ?? "";

        setMessages((prev) => [...prev, { role: "model", text: reply }]);
      } catch (e) {
        setError({
          kind: "network",
          message: e instanceof Error ? e.message : String(e),
        });
      } finally {
        setSending(false);
      }
    },
    [endpointUrl, messages],
  );

  const reset = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return { messages, sending, error, send, reset };
}
```

> **Cursor: before declaring this done, verify the request shape.** Open one of the LLM challenge server files (e.g. `llm/The-Enchanted-Parrot-Beginner/challenge/server.py` in the monorepo) and confirm it accepts `{message, history}` in the body and returns `{reply: string}`. If the server expects different field names (e.g. `user_message`, `conversation_history`, `response`), update this hook to match. The hook's correctness depends on matching the server's contract exactly.

### Step 4 (Option 2) — `LLMChatPanel` component

### `src/components/llm/LLMChatPanel.tsx` (new)

```tsx
import { useEffect, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { useLLMChat, type ChatError } from "@/hooks/useLLMChat";

interface Props {
  endpointUrl: string;
}

export default function LLMChatPanel({ endpointUrl }: Props) {
  const { messages, sending, error, send, reset } = useLLMChat(endpointUrl);
  const [draft, setDraft] = useState("");
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!draft.trim() || sending) return;
    const text = draft.trim();
    setDraft("");
    await send(text);
  };

  return (
    <section className="mb-8 p-4 rounded-lg border-2 border-amber-700/40 bg-stone-900/40 backdrop-blur-md">
      <div className="flex items-center justify-between mb-3">
        <h3 className="font-quintessential text-lg text-amber-200">Speak With the Familiar</h3>
        {messages.length > 0 && (
          <button
            onClick={reset}
            className="text-xs font-medievalsharp text-amber-400/60 hover:text-amber-300"
          >
            ⟲ New conversation
          </button>
        )}
      </div>

      <div
        ref={scrollRef}
        className="max-h-96 overflow-y-auto mb-3 space-y-2 pr-2"
        style={{ minHeight: "12rem" }}
      >
        {messages.length === 0 && !sending && (
          <p className="font-medievalsharp text-sm text-amber-500/50 italic text-center py-12">
            Begin the conversation. The familiar awaits your first word.
          </p>
        )}
        <AnimatePresence initial={false}>
          {messages.map((m, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] px-3 py-2 rounded-lg text-sm font-medievalsharp whitespace-pre-wrap ${
                  m.role === "user"
                    ? "bg-amber-900/30 border border-amber-700/40 text-amber-100"
                    : "bg-stone-800/40 border border-amber-800/20 text-amber-200/90"
                }`}
              >
                {m.text}
              </div>
            </motion.div>
          ))}
          {sending && (
            <motion.div
              key="thinking"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex justify-start"
            >
              <div className="px-3 py-2 rounded-lg bg-stone-800/40 border border-amber-800/20 text-amber-400/60 font-medievalsharp text-sm">
                <span className="animate-pulse">The familiar ponders…</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      <ChatErrorBanner error={error} />

      <form onSubmit={onSubmit} className="flex gap-2">
        <input
          type="text"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          placeholder="Speak your incantation…"
          className="flex-1 px-3 py-2 rounded-lg border border-amber-700/40 bg-stone-950/70 text-amber-100 font-medievalsharp text-sm focus:outline-none focus:border-amber-500"
          disabled={sending}
          autoComplete="off"
          spellCheck={false}
        />
        <button
          type="submit"
          disabled={sending || !draft.trim()}
          className="px-4 py-2 rounded-lg border-2 border-amber-600/60 bg-amber-900/30 backdrop-blur-md font-quintessential text-amber-100 hover:bg-amber-800/50 disabled:opacity-50 disabled:cursor-not-allowed transition"
        >
          {sending ? "…" : "Send"}
        </button>
      </form>
    </section>
  );
}

function ChatErrorBanner({ error }: { error: ChatError | null }) {
  if (!error) return null;
  let msg: string;
  switch (error.kind) {
    case "no_key":
      msg = "Set your API key above before speaking.";
      break;
    case "auth":
      msg = `The familiar refused your offering: ${error.message}`;
      break;
    case "rate_limited":
      msg = "The familiar is fatigued (rate limited). Wait a moment.";
      break;
    case "network":
      msg = `Could not reach the familiar: ${error.message}`;
      break;
    case "server":
      msg = `The familiar choked (HTTP ${error.status}): ${error.message}`;
      break;
  }
  return (
    <div className="mb-3 px-3 py-2 rounded border border-red-700/40 bg-red-950/30 font-medievalsharp text-sm text-red-300/80">
      {msg}
    </div>
  );
}
```

### Step 5 (Option 2) — Wire into ChallengeDetailPage

In `src/pages/ChallengeDetailPage.tsx`, render `LLMChatPanel` for LLM challenges:

```diff
 import LLMDemoAnimation from "@/components/llm/LLMDemoAnimation";
+import LLMChatPanel from "@/components/llm/LLMChatPanel";
+import { getLLMEndpoint } from "@/data/llm-endpoints";
```

```diff
 {isLLM && (
   <section className="mb-8">
     <h2 className="font-quintessential text-xl text-amber-200 mb-3">The Familiar Speaks</h2>
     <BYOKeyForm />
+    {getLLMEndpoint(slug ?? "") && (
+      <LLMChatPanel endpointUrl={getLLMEndpoint(slug ?? "")!} />
+    )}
     <LLMDemoAnimation challengeSlug={slug ?? ""} />
   </section>
 )}
```

### Step 6 (Option 2) — CORS on the challenge servers

**This is the gotcha that will break Option 2 on first deploy if not handled.** The SPA at `https://ctf.chron0.tech` will make cross-origin fetch calls to `https://parrot.ctf.chron0.tech/chat`. The challenge server's FastAPI must allow this.

In each LLM challenge `server.py` in the monorepo, confirm CORS middleware is configured:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://ctf.chron0.tech",
        "http://localhost:5173",  # dev
    ],
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type", "X-Player-API-Key"],
    allow_credentials=False,
)
```

**Cursor: open one of the 5 LLM server.py files and check. If CORS isn't there, this is a separate monorepo edit.** Either:
- Add the middleware to each of the 5 `server.py` files, OR
- Add it once in `llm/shared/` (e.g. a `cors.py` module that exports a function `add_cors(app)`) and call it from each server

Without this, the browser will block the chat request before it even leaves the page. You'll see a CORS error in DevTools, not on the network tab.

### Step 7 (Option 2) — Verify

```bash
bun run build
bunx tsc -b --noEmit
bun run lint
bun run dev
```

Manual smoke-test:

- [ ] `/challenges/the-enchanted-parrot` renders BYOKeyForm + LLMChatPanel + LLMDemoAnimation
- [ ] Without a stored key, sending a message shows "Set your API key above" inline
- [ ] With a stored key, sending a message hits `https://parrot.ctf.chron0.tech/chat` (DevTools Network tab confirms)
- [ ] Successful response renders in the chat history
- [ ] Multi-turn conversation works (model gets context)
- [ ] "New conversation" button clears history
- [ ] CORS preflight (OPTIONS) succeeds — check Network tab
- [ ] Non-LLM challenges don't render the chat panel
- [ ] Flag submission still works on a non-LLM challenge

### Step 8 (Option 2) — Commit + push

```bash
git checkout -b fix/llm-byo-chat-ui main
git add src/
git commit -m "site: fix LLM BYO-key — add in-SPA chat UI, revert flag-submit header"
git push -u origin fix/llm-byo-chat-ui

# Plus a separate PR in the monorepo if CORS middleware was missing:
cd ../fantasy_ctf_challs
git checkout -b fix/llm-cors feat/hosting
# add CORS middleware to all 5 server.py files
git push -u origin fix/llm-cors
```

---

## Decision: which option

**Pick Option 1 if:**
- You want this fixed in the next 30 minutes
- Your audience is mostly CTF veterans who'd write their own solve scripts anyway
- You want minimal new code to maintain

**Pick Option 2 if:**
- You want LLM challenges accessible to non-script-writers (broader portfolio reach)
- A polished in-site chat UI is part of the portfolio story you want to tell
- You're OK adding CORS middleware to the monorepo as part of the fix

**My recommendation: Option 1 first.** Ship the curl-pattern fix today. You'll have time post-launch to add a chat UI if friend-beta feedback says players struggled with curl. Don't gold-plate before validating that the gold matters.

---

## What this brief does NOT cover

- The monorepo `llm/Dockerfile` flag bake-in — separate Cursor task, not this one
- Rotating the 5 LLM flags after Dockerfile fix — Jon's task
- Re-running `ctf challenge sync` after flag rotation — Jon's task
- The Gemini API key revocation — Jon already did
