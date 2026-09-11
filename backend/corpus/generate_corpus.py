"""
Generates ~500 synthetic transcript-like dictation records + a fixed eval
question set with known gold answers / abstentions.

Deterministic (seeded) and template-based — no LLM calls, so it's free,
instant, and reproducible. Disclosed in README's AI-use section.

Run: python corpus/generate_corpus.py
Outputs: corpus/data/dictations.json, corpus/data/eval_questions.json
"""

import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

from persona import (
    USER_NAME, COMPANY, TEAMMATES, TEAMS, PROJECTS, CLIENTS, APPS,
    KNOWN_FACTS, UNKNOWN_ENTITIES,
)

RNG = random.Random(42)  # fixed seed -> reproducible corpus
OUT_DIR = Path(__file__).parent / "data"
OUT_DIR.mkdir(exist_ok=True)

CORPUS_END = datetime.now(timezone.utc).replace(microsecond=0)
CORPUS_START = CORPUS_END - timedelta(days=45)

FILLERS = ["um", "so", "like", "uh", "you know", "basically"]


def asr_noise(clean: str) -> str:
    """Turn a clean sentence into rough, punctuation-free, filler-laden 'raw ASR'."""
    words = clean.lower().replace(",", "").replace(".", "").split()
    out = []
    for w in words:
        out.append(w)
        if RNG.random() < 0.06:
            out.append(RNG.choice(FILLERS))
    return " ".join(out)


def random_timestamp(days_ago_min=0, days_ago_max=45):
    delta_days = RNG.uniform(days_ago_min, days_ago_max)
    ts = CORPUS_END - timedelta(days=delta_days)
    # business-hours bias
    ts = ts.replace(hour=RNG.randint(8, 19), minute=RNG.randint(0, 59), second=0)
    return ts


def mk_record(record_id, app, clean_text, timestamp, extra_meta=None):
    return {
        "record_id": record_id,
        "app": app,
        "raw_asr": asr_noise(clean_text),
        "llm_formatted": clean_text,
        "timestamp": timestamp.isoformat(),
        "extra_metadata": extra_meta or {},
    }


records = []
counter = 0


def next_id(prefix):
    global counter
    counter += 1
    return f"{prefix}-{counter:04d}"


# ---------- 1. Slack status updates (220) ----------
SLACK_TEMPLATES = [
    "Quick update on {proj}: I finished the wireframe review with {teammate} and we're on track for {client} demo next week.",
    "Blocked on {proj} until {teammate} finishes the API contract, following up with them today.",
    "Standup note: {proj} is at 60 percent, {teammate} is helping unblock the {team} sprint.",
    "Heads up, {teammate} and I are syncing on {proj} tomorrow morning about the {client} rollout.",
    "Wrapped up the {proj} spec review, {teammate} raised a concern about the timeline for {team}.",
]

for i in range(220):
    proj = RNG.choice(PROJECTS)
    teammate = RNG.choice(TEAMMATES)
    team = RNG.choice(TEAMS)
    client = RNG.choice(CLIENTS)
    template = RNG.choice(SLACK_TEMPLATES)
    text = template.format(proj=proj["name"], teammate=teammate["name"], team=team, client=client)
    ts = random_timestamp()
    records.append(mk_record(next_id("slk"), "Slack", text, ts))

# Explicit preference statement + later contradiction (scoped-override test)
pref_early_ts = CORPUS_END - timedelta(days=40)
pref_late_ts = CORPUS_END - timedelta(days=5)
records.append(mk_record(
    next_id("slk"), "Slack",
    "Hey Kivi, from now on format my Slack updates as full paragraphs, not bullet points.",
    pref_early_ts, {"is_preference_statement": True},
))
records.append(mk_record(
    next_id("slk"), "Slack",
    "Hey Kivi, actually change that, format my Slack updates as bullet points from now on.",
    pref_late_ts, {"is_preference_statement": True},
))

# ---------- 2. Google Docs drafts (120) ----------
DOC_TEMPLATES = [
    "Draft section for {proj} ({acr}): the goal of this phase is to reduce onboarding drop-off by "
    "redesigning the signup flow, with {teammate} owning the design system updates and {team} owning rollout.",
    "PRD note for {proj} ({acr}): {client} has asked for a configurable dashboard, {teammate} estimates "
    "two sprints, {team} will need one more engineer.",
    "Meeting notes draft: discussed {proj} ({acr}) timeline with {teammate}, decided to push the {client} "
    "pilot by one week to fix the edge cases {team} found.",
]

for i in range(120):
    proj = RNG.choice(PROJECTS)
    teammate = RNG.choice(TEAMMATES)
    team = RNG.choice(TEAMS)
    client = RNG.choice(CLIENTS)
    template = RNG.choice(DOC_TEMPLATES)
    text = template.format(proj=proj["name"], acr=proj["acronym"], teammate=teammate["name"],
                            team=team, client=client)
    ts = random_timestamp()
    records.append(mk_record(next_id("doc"), "Google Docs", text, ts))

# ---------- 3. Outlook emails (100) ----------
EMAIL_TEMPLATES = [
    "Email to {teammate}: confirming our sync about {proj} is moved to Thursday at 3 PM, "
    "please loop in {team} before then.",
    "Email to {client}: sharing the updated timeline for {proj}, {teammate} will be the point of "
    "contact on our side going forward.",
    "Follow-up email after the {client} call: {teammate} to send the {proj} rollout plan by Friday.",
]

for i in range(100):
    proj = RNG.choice(PROJECTS)
    teammate = RNG.choice(TEAMMATES)
    team = RNG.choice(TEAMS)
    client = RNG.choice(CLIENTS)
    template = RNG.choice(EMAIL_TEMPLATES)
    text = template.format(proj=proj["name"], teammate=teammate["name"], team=team, client=client)
    ts = random_timestamp()
    records.append(mk_record(next_id("mail"), "Outlook", text, ts))

# ---------- 4. Notes (short episodic, 60) ----------
NOTE_TEMPLATES = [
    "Note to self: ask {teammate} about the {proj} budget before Friday.",
    "Reminder: {team} retro moved to next Monday because of {proj}.",
    "Idea: maybe {teammate} should present {proj} progress at the next all-hands.",
]

for i in range(60):
    proj = RNG.choice(PROJECTS)
    teammate = RNG.choice(TEAMMATES)
    team = RNG.choice(TEAMS)
    template = RNG.choice(NOTE_TEMPLATES)
    text = template.format(proj=proj["name"], teammate=teammate["name"], team=team)
    # bias notes towards being OLD, to exercise 30-day decay
    ts = random_timestamp(days_ago_min=25, days_ago_max=45)
    records.append(mk_record(next_id("note"), "Notes", text, ts))

# A specific note that gets RE-REFERENCED later (decay-reset test):
# old note about a budget number, then a later dictation that re-surfaces it.
old_note_ts = CORPUS_END - timedelta(days=38)
reref_ts = CORPUS_END - timedelta(days=10)
records.append(mk_record(
    next_id("note"), "Notes",
    "Note to self: the Project Falcon budget ask is 40,000 dollars for this quarter.",
    old_note_ts,
))
records.append(mk_record(
    next_id("slk"), "Slack",
    "Following up on the Project Falcon budget ask of 40,000 dollars I noted earlier, finance approved it.",
    reref_ts,
))

# A specific OLD, never-re-referenced fact, meant to have fully decayed by ingestion time
stale_ts = CORPUS_END - timedelta(days=44)
records.append(mk_record(
    next_id("note"), "Notes",
    "Quick reminder: parking validation code for today's office visit is 7734.",
    stale_ts,
))

records.sort(key=lambda r: r["timestamp"])

with open(OUT_DIR / "dictations.json", "w") as f:
    json.dump({"user_name": USER_NAME, "company": COMPANY, "records": records}, f, indent=2)

print(f"Generated {len(records)} dictation records -> {OUT_DIR/'dictations.json'}")

# ---------- Eval question set ----------
eval_questions = [
    # Use case 1: find & polish
    {"id": "q1", "category": "find_and_polish",
     "question": "Hey Kivi, find my most recent Slack update about Project Falcon and polish it for a client email.",
     "expects": {"type": "answerable", "must_reference": ["Project Falcon"], "app_context": "Slack"}},
    {"id": "q2", "category": "find_and_polish",
     "question": "Find the dictation I did in Google Docs about Project Comet's timeline and clean it up.",
     "expects": {"type": "answerable", "must_reference": ["Project Comet"], "app_context": "Google Docs"}},

    # Use case 2: factual recall + abstention
    {"id": "q3", "category": "factual_recall",
     "question": "What does PRJ-FLC stand for?",
     "expects": {"type": "answerable", "gold_answer_contains": ["Project Falcon", "onboarding"]}},
    {"id": "q4", "category": "factual_recall",
     "question": "Who is the Engineering Lead I work with?",
     "expects": {"type": "answerable", "gold_answer_contains": ["Rahul Iyer"]}},
    {"id": "q5", "category": "factual_recall_abstain",
     "question": "What is the status of Project Nimbus?",
     "expects": {"type": "abstain", "reason": "Project Nimbus never mentioned in corpus"}},
    {"id": "q6", "category": "factual_recall_abstain",
     "question": "What's Karan Bose's role on my team?",
     "expects": {"type": "abstain", "reason": "Karan Bose never mentioned in corpus"}},

    # Use case 3: preference teach/override
    {"id": "q7", "category": "preference",
     "question": "How should my Slack updates be formatted right now?",
     "expects": {"type": "answerable", "gold_answer_contains": ["bullet points"],
                 "note": "must reflect the LATER override, not the earlier paragraph preference"}},

    # Use case 4: period recap
    {"id": "q8", "category": "period_recap",
     "question": "What did I work on in the last week?",
     "expects": {"type": "answerable", "must_cite_sources": True}},

    # Decay behaviour
    {"id": "q9", "category": "decay",
     "question": "What was that parking validation code I noted a while back?",
     "expects": {"type": "abstain", "reason": "episodic note is >30 days old and never re-referenced, should have decayed"}},
    {"id": "q10", "category": "decay_reset",
     "question": "What was the Project Falcon budget ask I noted?",
     "expects": {"type": "answerable", "gold_answer_contains": ["40,000", "40000"],
                 "note": "originally noted 38 days ago but re-referenced 10 days ago, so decay clock should have reset"}},
]

with open(OUT_DIR / "eval_questions.json", "w") as f:
    json.dump(eval_questions, f, indent=2)

print(f"Generated {len(eval_questions)} eval questions -> {OUT_DIR/'eval_questions.json'}")