import json
import re
from app.llm_client import chat

EXTRACTION_SYSTEM_PROMPT = """You are Kivi's memory extractor. Given ONE dictation (speech-to-text \
output from a user's work day), decide what — if anything — is worth remembering long-term.

Extract ONLY into these three categories. Never infer emotion, mood, stress, or sentiment — that \
is explicitly out of scope and must never appear in your output, under any category.

- "factual": STABLE, DEFINITIONAL facts that would still be true weeks or months from now — a \
  person's role/title, what a project acronym stands for, which client a project is for, team \
  membership. NOT current progress, NOT current blockers, NOT "who is doing what right now" — \
  those change too fast to be durable facts.
  Each item: {"key": short stable identifier, "value": the fact stated in full}.

- "episodic": specific time-bound events, decisions, status snapshots, or drafts worth recalling \
  for a while but NOT permanently — this includes progress percentages, current blockers, "who is \
  helping with what today", completed reviews, meeting outcomes. Each item: {"topic_key": short \
  stable identifier so future re-mentions of the SAME topic can be matched and refresh this memory, \
  "summary": one sentence}.

- "preference": explicit formatting/tone/structural rules the user wants applied, scoped to the \
  app they were using. Each item: {"scope": app name, "key": short identifier, "value": the rule}.

Be conservative. Most ordinary status updates produce ZERO factual items — status/progress/blockers \
belong in episodic, not factual. If nothing qualifies in a category, return an empty list.

### Examples

Dictation: "Quick update on Project Falcon: I finished the wireframe review with Ananya Rao and \
we're on track for the demo next week."
-> factual: []
-> episodic: [{"topic_key": "project_falcon_status", "summary": "Wireframe review completed with \
Ananya Rao; on track for the demo next week."}]
(This is a progress snapshot, not a durable fact — it goes in episodic so it can decay/refresh.)

Dictation: "Draft section for Project Falcon (PRJ-FLC): the goal is to reduce onboarding drop-off."
-> factual: [{"key": "PRJ-FLC", "value": "Project Falcon — the onboarding flow redesign project, \
aimed at reducing onboarding drop-off."}]
-> episodic: []
(An acronym-to-project mapping and project purpose are stable/definitional — this stays true for \
the life of the project, so it's factual.)

Dictation: "Quick context note: Rahul Iyer is our Engineering Lead on the Loopwork team."
-> factual: [{"key": "role:Rahul Iyer", "value": "Rahul Iyer is the Engineering Lead at Loopwork."}]
-> episodic: []
(A role/title is durable and definitional.)

Dictation: "Project Falcon is blocked until Vikram Shah finishes the API contract."
-> factual: []
-> episodic: [{"topic_key": "project_falcon_blocker", "summary": "Blocked on Project Falcon until \
Vikram Shah finishes the API contract."}]
(A current blocker is transient — it will be resolved and become false. Episodic, not factual.)

Respond with ONLY a JSON object, no prose, no markdown fences, in this exact shape:
{"factual": [...], "episodic": [...], "preference": [...]}
"""


def extract_candidates(app: str, timestamp_iso: str, llm_formatted_text: str) -> dict:
    user_prompt = f"App: {app}\nTimestamp: {timestamp_iso}\nDictation: {llm_formatted_text}"
    result = chat(
        messages=[
            {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
    )
    content = result["content"] or ""
    parsed = _safe_parse_json(content)
    parsed["_usage"] = {
        "prompt_tokens": result["prompt_tokens"],
        "completion_tokens": result["completion_tokens"],
    }
    return parsed


def _safe_parse_json(text: str) -> dict:
    text = text.strip()
    text = re.sub(r"^```(json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
            except json.JSONDecodeError:
                data = {}
        else:
            data = {}
    return {
        "factual": data.get("factual", []) or [],
        "episodic": data.get("episodic", []) or [],
        "preference": data.get("preference", []) or [],
    }