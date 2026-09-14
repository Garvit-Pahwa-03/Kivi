"""
Runs a given eval question set through Hey Kivi and scores each answer.

Usage:
    python eval/run_eval.py [questions_file] [report_name]
    python eval/run_eval.py                                   # defaults to the original fixed set
    python eval/run_eval.py corpus/data/held_out_questions.json held_out

Each question is either:
    {"id", "category", "question", "expects": {...}}
  or a multi-turn setup + scored probe:
    {"id", "category", "turns": ["setup message", ..., "final scored question"], "expects": {...}}
"""
import sys
import json
import time
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db import SessionLocal
from app.memory_service import get_or_create_user
from app.orchestrator import handle_request

CORPUS_PATH = Path(__file__).parent.parent / "corpus" / "data" / "dictations.json"
DEFAULT_QUESTIONS_PATH = Path(__file__).parent.parent / "corpus" / "data" / "eval_questions.json"
RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

INR_PER_1M_INPUT = 36.6
INR_PER_1M_OUTPUT = 91.5


def cost_inr(prompt_tokens, completion_tokens):
    return (prompt_tokens / 1_000_000) * INR_PER_1M_INPUT + \
           (completion_tokens / 1_000_000) * INR_PER_1M_OUTPUT


def _evidence_text(result: dict) -> str:
    parts = [result.get("response") or ""]
    for v in result.get("tool_output", {}).values():
        if isinstance(v, dict):
            for r in v.get("results", []):
                parts.append(r.get("text") or r.get("content") or "")
            if "polish" in v:
                parts.append(v["polish"].get("polished_text") or "")
    return " ".join(parts).lower()


def score_result(question: dict, result: dict) -> dict:
    expects = question["expects"]
    exp_type = expects["type"]
    response_lower = (result["response"] or "").lower()

    checks = {}
    if exp_type == "abstain":
        checks["abstained_correctly"] = result["abstained"] is True
        checks["no_memories_cited"] = len(result["memories_used"]) == 0
        passed = checks["abstained_correctly"] and checks["no_memories_cited"]

    elif exp_type == "answerable":
        checks["did_not_abstain"] = result["abstained"] is False
        passed = checks["did_not_abstain"]

        if "gold_answer_contains" in expects:
            hits = [g for g in expects["gold_answer_contains"] if g.lower() in response_lower]
            checks["gold_answer_contains"] = f"{len(hits)}/{len(expects['gold_answer_contains'])} matched: {hits}"
            passed = passed and len(hits) > 0

        if "must_reference" in expects:
            evidence_lower = _evidence_text(result)
            hits = [g for g in expects["must_reference"] if g.lower() in evidence_lower]
            checks["must_reference"] = f"{len(hits)}/{len(expects['must_reference'])} matched: {hits}"
            passed = passed and len(hits) == len(expects["must_reference"])

        if expects.get("must_cite_sources"):
            checks["must_cite_sources"] = len(result["memories_used"]) > 0
            passed = passed and checks["must_cite_sources"]

    else:
        passed = False
        checks["error"] = f"unknown expects.type: {exp_type}"

    return {"passed": passed, "checks": checks}


def run_question(db, user, q: dict) -> dict:
    """Runs a single question, handling both plain 'question' and multi-turn 'turns'."""
    if "turns" in q:
        setup_turns = q["turns"][:-1]
        final_question = q["turns"][-1]
        setup_results = []
        for turn_text in setup_turns:
            r = handle_request(db, user, turn_text)
            setup_results.append({"turn": turn_text, "response": r["response"]})
        t0 = time.time()
        result = handle_request(db, user, final_question)
        wall_ms = int((time.time() - t0) * 1000)
        result["_setup_turns"] = setup_results
        result["_asked_question"] = final_question
    else:
        t0 = time.time()
        result = handle_request(db, user, q["question"])
        wall_ms = int((time.time() - t0) * 1000)
        result["_setup_turns"] = []
        result["_asked_question"] = q["question"]
    result["_wall_ms"] = wall_ms
    return result


def main():
    questions_path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_QUESTIONS_PATH
    report_name = sys.argv[2] if len(sys.argv) > 2 else "report"

    with open(questions_path, encoding="utf-8") as f:
        questions = json.load(f)
    with open(CORPUS_PATH, encoding="utf-8") as f:
        corpus_meta = json.load(f)

    db = SessionLocal()
    user = get_or_create_user(db, corpus_meta["user_name"])

    db_path = Path(__file__).parent.parent / "kivi.db"
    size_before = db_path.stat().st_size if db_path.exists() else 0

    results = []
    print(f"Running {len(questions)} eval questions from {questions_path.name} against Hey Kivi...\n")
    for q in questions:
        result = run_question(db, user, q)
        score = score_result(q, result)

        row = {
            "id": q["id"], "category": q.get("category", "uncategorized"),
            "question": result["_asked_question"],
            "setup_turns": result["_setup_turns"],
            "expects": q["expects"], "response": result["response"],
            "abstained": result["abstained"], "tool": result["tool"],
            "params": result["params"], "tool_output": result["tool_output"],
            "memories_used": result["memories_used"], "latency_ms": result["latency_ms"],
            "wall_clock_ms": result["_wall_ms"],
            "prompt_tokens": result["prompt_tokens"], "completion_tokens": result["completion_tokens"],
            "cost_inr": round(cost_inr(result["prompt_tokens"], result["completion_tokens"]), 4),
            "passed": score["passed"], "checks": score["checks"],
        }
        results.append(row)
        status = "PASS" if row["passed"] else "FAIL"
        print(f"  [{status}] {q['id']} ({q.get('category', 'uncategorized')}): {result['_asked_question'][:60]}...")

    size_after = db_path.stat().st_size if db_path.exists() else 0
    passed_count = sum(1 for r in results if r["passed"])
    total_latency = sum(r["latency_ms"] for r in results)
    total_cost = sum(r["cost_inr"] for r in results)

    report = {
        "questions_file": str(questions_path), "run_at": datetime.now(timezone.utc).isoformat(),
        "total_questions": len(results), "passed": passed_count, "failed": len(results) - passed_count,
        "pass_rate": round(passed_count / len(results), 3),
        "avg_latency_ms": round(total_latency / len(results), 1),
        "total_cost_inr": round(total_cost, 4),
        "db_size_bytes": size_after, "db_growth_bytes_this_run": size_after - size_before,
        "results": results,
    }

    with open(RESULTS_DIR / f"{report_name}.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    lines = [
        f"# Hey Kivi Eval Report — {questions_path.name}", "",
        f"Run at: {report['run_at']}", "",
        f"**{passed_count}/{len(results)} passed ({report['pass_rate']*100:.1f}%)**  ",
        f"Avg latency: {report['avg_latency_ms']} ms  ",
        f"Total cost: INR {report['total_cost_inr']}  ",
        f"DB size: {report['db_size_bytes']:,} bytes", "",
        "| ID | Category | Result | Latency (ms) | Cost (INR) | Question |",
        "|---|---|---|---|---|---|",
    ]
    for r in results:
        status = "PASS" if r["passed"] else "FAIL"
        lines.append(f"| {r['id']} | {r['category']} | {status} | {r['latency_ms']} | {r['cost_inr']} | {r['question'][:50]} |")

    lines.append("\n## Failures in detail\n")
    for r in results:
        if not r["passed"]:
            lines.append(f"### {r['id']}: {r['question']}")
            lines.append(f"- Response: {r['response']}")
            lines.append(f"- Checks: {r['checks']}")
            lines.append("")

    with open(RESULTS_DIR / f"{report_name}.md", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n{passed_count}/{len(results)} passed ({report['pass_rate']*100:.1f}%)")
    print(f"Avg latency: {report['avg_latency_ms']} ms | Total cost: INR {report['total_cost_inr']}")
    print(f"Reports written to eval/results/{report_name}.json and eval/results/{report_name}.md")

    db.close()


if __name__ == "__main__":
    main()