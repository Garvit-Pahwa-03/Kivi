import json
import re
import time
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app import models, tools
from app.llm_client import chat

ROUTER_SYSTEM_PROMPT = """You are Hey Kivi's request router. Given a user's spoken request, decide \
which single tool best serves it, and extract the parameters that tool needs.

Today's date/time (UTC) is: {now}

Available tools:

1. "find_and_polish" — user wants to locate a specific past dictation and reformat/polish it.
   params: {{"keywords": short search phrase describing the dictation's topic, "app": one of \
["Slack","Google Docs","Outlook","Notes"] or null if unspecified, "start": ISO datetime or null, \
"end": ISO datetime or null (resolve relative time phrases like "yesterday 5pm" into an actual \
UTC range around today's date above), "target_app": one of ["Slack","Google Docs","Outlook","Notes"] \
— infer from context (e.g. "for a client email" -> "Outlook"; if unclear, use the same as "app")}}

2. "factual_recall" — user is asking about anything they've noted or told Kivi before: a durable \
fact (a role, an acronym, a client), OR a specific thing they previously noted/decided (a figure, \
a decision, a reminder). Covers both permanent facts and specific remembered notes.
   params: {{"query": the question, restated as a short search phrase, preserving the user's own \
distinctive nouns/terms verbatim rather than paraphrasing them away}}

3. "preference_query" — user is asking what a current formatting/tone rule is.
   params: {{"app_scope": one of ["Slack","Google Docs","Outlook","Notes"]}}

4. "preference_teach" — user is explicitly stating a NEW formatting/tone rule to remember.
   params: {{"app_scope": one of [...], "key": short identifier like "formatting_style", \
"value": the rule, stated plainly}}

5. "period_recap" - user wants a summary of what they worked on over a time period.
   params: {{"start": ISO datetime, "end": ISO datetime, "keywords": optional topic filter or null, "app": one of "Slack", "Google Docs", "Outlook", "Notes" if the user names a specific app, else null. If the user names an app that is not one of those four (for example Teams or Zoom), set app to "UNKNOWN_APP".}}

Respond with ONLY JSON: {{"tool": "...", "params": {{...}}}}
"""

ANSWER_SYSTEM_PROMPT = """You are Hey Kivi, answering the user using ONLY the memory/dictation \
evidence provided below. Rules:
- Never state anything not supported by the evidence.
- If the evidence is empty or insufficient to answer, say plainly that you don't have that in the \
user's history — do not guess or invent an answer.
- Keep the answer concise and natural, as if speaking to the user.
"""


def _parse_json(text: str) -> dict:
    text = re.sub(r"^```(json)?", "", text.strip()).strip()
    text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            pass

    return {}


def _dt(s):
    if not s:
        return None
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def handle_request(db: Session, user: models.User, request_text: str) -> dict:
    t0 = time.time()
    now = datetime.now(timezone.utc)
    total_prompt_tokens = 0
    total_completion_tokens = 0

    router_result = chat([
        {"role": "system", "content": ROUTER_SYSTEM_PROMPT.format(now=now.isoformat())},
        {"role": "user", "content": request_text},
    ], temperature=0.0)
    total_prompt_tokens += router_result["prompt_tokens"] or 0
    total_completion_tokens += router_result["completion_tokens"] or 0

    routed = _parse_json(router_result["content"] or "{}")
    tool_name = routed.get("tool")
    params = routed.get("params", {})

    evidence = None
    memories_used = []
    tool_output = {}

    if tool_name == "find_and_polish":
        search_query = f"{params.get('keywords', '')} {request_text}".strip()
        search = tools.tool_search_episodic(
            db, user.id, keywords=search_query, app=params.get("app"),
            start=_dt(params.get("start")), end=_dt(params.get("end")), top_k=1,
        )
        if search["found"]:
            top = search["results"][0]
            polish = tools.tool_polish_text(db, user.id, top["text"], params.get("target_app") or top["app"])
            total_prompt_tokens += polish["usage"]["prompt_tokens"] or 0
            total_completion_tokens += polish["usage"]["completion_tokens"] or 0
            evidence = f"Found dictation ({top['app']}, {top['timestamp']}): \"{top['text']}\"\n\nPolished:\n{polish['polished_text']}"
            memories_used = [top["dictation_id"]] + [p.get("memory_id") for p in polish["preferences_applied"]]
            tool_output = {"search": search, "polish": polish}
        else:
            tool_output = {"search": search}

    elif tool_name == "factual_recall":
        result = tools.tool_recall_fact(db, user.id, params.get("query", request_text))
        if result["found"]:
            evidence = "\n".join(f"- {r['content']}" for r in result["results"])
            memories_used = [r["memory_id"] for r in result["results"]]
        tool_output = {"recall_fact": result}

    elif tool_name == "preference_query":
        result = tools.tool_recall_preference(db, user.id, params.get("app_scope", "Slack"))
        if result["found"]:
            evidence = "\n".join(f"- {r['content']}" for r in result["results"])
            memories_used = [r["memory_id"] for r in result["results"]]
        tool_output = {"recall_preference": result}

    elif tool_name == "preference_teach":
        result = tools.tool_upsert_preference(
            db, user.id, params.get("app_scope", "Slack"),
            params.get("key", "formatting_style"), params.get("value", ""),
        )
        evidence = f"Stored new preference for {result['scope']}: {result['content']}"
        memories_used = [result["memory_id"]]
        tool_output = {"upsert_preference": result}

    elif tool_name == "period_recap":
        result = tools.tool_summarize_period(
            db, user.id, _dt(params.get("start")), _dt(params.get("end")), params.get("keywords"),
            app=params.get("app") if params.get("app") != "UNKNOWN_APP" else "__no_such_app__",
        )
        if result["found"]:
            lines = [f"- ({d['app']}, {d['timestamp']}): {d['text']}" for d in result["dictations"]]
            lines += [f"- {e['content']}" for e in result["episodic_memories"]]
            evidence = "\n".join(lines)
            memories_used = [e["memory_id"] for e in result["episodic_memories"]] + \
                             [d["dictation_id"] for d in result["dictations"]]
        tool_output = {"summarize_period": result}

    else:
        tool_output = {"error": f"unrecognized tool: {tool_name}"}

    abstained = evidence is None
    if abstained:
        response_text = "I don't have anything in your history that answers that — I don't want to guess."
    else:
        answer_result = chat([
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": f"User request: {request_text}\n\nEvidence:\n{evidence}"},
        ], temperature=0.2)
        total_prompt_tokens += answer_result["prompt_tokens"] or 0
        total_completion_tokens += answer_result["completion_tokens"] or 0
        response_text = (answer_result["content"] or "").strip()

    latency_ms = int((time.time() - t0) * 1000)

    turn = models.HeyKiviTurn(
        user_id=user.id, request_text=request_text,
        tools_called=[tool_name], memories_used=memories_used,
        response_text=response_text, abstained=int(abstained),
        latency_ms=latency_ms, prompt_tokens=total_prompt_tokens, completion_tokens=total_completion_tokens,
    )
    db.add(turn)
    db.commit()
    db.refresh(turn)

    return {
        "turn_id": turn.id, "response": response_text, "abstained": abstained,
        "tool": tool_name, "params": params, "memories_used": memories_used,
        "tool_output": tool_output, "latency_ms": latency_ms,
        "prompt_tokens": total_prompt_tokens, "completion_tokens": total_completion_tokens,
    }