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

IMPORTANT: "preference_teach" applies ONLY when the user gives an explicit, actionable
formatting/tone/structure instruction tied to a named app (e.g. "format my Slack updates
as bullet points"). Questions ABOUT the product itself - how it works, what it can do, how
to make it do something automatically - are never preference instructions, even if they
mention words like "remember" or "format". If no tool clearly fits a request, do not guess;
respond with {{"tool": null, "params": {{}}}} so the system abstains rather than inventing
a stored preference the user never actually stated.

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

6. "recall_shortcut" - user is asking what a shortcut does, or what phrase triggers a
   given piece of text they have taught Kivi to expand.
   params: {{"query": the question, restated as a short search phrase}}
   
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
    
    from app import shortcuts as shortcuts_svc
    existing_shortcuts = shortcuts_svc.list_shortcuts(db, user.id)
    normalized_input = request_text.strip().lower().rstrip("?.!")
    matched_shortcut = None
    for sc in existing_shortcuts:
        trig = sc.trigger_phrase.strip().lower()
        # Only fast-path when the ENTIRE message is essentially just the trigger phrase
        # (allowing a few extra words like "what does X do") - never when the trigger is
        # embedded inside a longer, unrelated request. That case falls through to the
        # normal router instead of being silently hijacked.
        is_bare_trigger = normalized_input == trig
        is_short_lookup = trig in normalized_input and len(normalized_input) <= len(trig) + 20
        if is_bare_trigger or is_short_lookup:
            matched_shortcut = sc
            break

    if matched_shortcut:
        evidence = "saying \"" + matched_shortcut.trigger_phrase + "\" expands to: " + matched_shortcut.expansion_text
        answer_result = chat([
            {"role": "system", "content": ANSWER_SYSTEM_PROMPT},
            {"role": "user", "content": "User request: " + request_text + "\n\nEvidence:\n" + evidence},
        ], temperature=0.2)
        response_text = (answer_result["content"] or "").strip()
        latency_ms = int((time.time() - t0) * 1000)

        turn = models.HeyKiviTurn(
            user_id=user.id, request_text=request_text,
            tools_called=["recall_shortcut"], memories_used=[matched_shortcut.id],
            response_text=response_text, abstained=0,
            latency_ms=latency_ms,
            prompt_tokens=answer_result["prompt_tokens"], completion_tokens=answer_result["completion_tokens"],
        )
        db.add(turn)
        db.commit()
        db.refresh(turn)

        return {
            "turn_id": turn.id, "response": response_text, "abstained": False,
            "tool": "recall_shortcut", "params": {"matched_trigger": matched_shortcut.trigger_phrase},
            "memories_used": [matched_shortcut.id],
            "tool_output": {"recall_shortcut": {"found": True, "results": [{
                "shortcut_id": matched_shortcut.id, "trigger_phrase": matched_shortcut.trigger_phrase,
                "expansion_text": matched_shortcut.expansion_text, "score": None,
                "reason": "direct match: input text matches a taught shortcut trigger phrase",
            }]}},
            "latency_ms": latency_ms,
            "prompt_tokens": answer_result["prompt_tokens"], "completion_tokens": answer_result["completion_tokens"],
        }
    
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
    elif tool_name == "recall_shortcut":
        search_query = params.get("query", "") + " " + request_text
        result = tools.tool_recall_shortcut(db, user.id, search_query)
        if result["found"]:
            evidence = "\n".join(
                "- saying \"" + r["trigger_phrase"] + "\" expands to: " + r["expansion_text"]
                for r in result["results"]
            )
            memories_used = [r["shortcut_id"] for r in result["results"]]
        tool_output = {"recall_shortcut": result}
        
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