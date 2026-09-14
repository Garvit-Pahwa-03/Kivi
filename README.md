# Kivi — Semantic Memory for Hey Kivi

**Golden Goose submission — Part 2: Build and Prove It**

## What this is

This is my implementation of semantic memory for Hey Kivi, built on the position I laid
out in Part 1: semantic memory should let Hey Kivi understand what's happened across a
person's work, without ever storing raw clutter, making unstated assumptions, or acting
where it hasn't been asked to.

I built four capabilities on top of that position — find-and-polish, factual recall,
preference teaching, and period recap — plus a fifth, shortcuts, which grew naturally out
of the same preference-memory machinery once I'd built it. The system runs end to end: a
FastAPI backend with a SQLite database, Sarvam's `sarvam-105b` doing all extraction and
generation, deterministic (non-embedding) retrieval, and a React frontend with five
working surfaces.

## Live demo

- **App:** https://kivi-theta.vercel.app
- **API:** https://kivi-kkjd.onrender.com

Sign up with any email/password to get your own isolated account — there is no seeded
demo login, since the corpus is tied to whichever account you create. See RUN.md for the
corpus-import procedure if you want your account populated with the test dataset.


## Product position (recap from Part 1)

- **Two modes, one boundary.** Ordinary dictation stays passive. Hey Kivi is the only
  place memory acts, and even there, it proposes rather than executes without
  confirmation for anything external.
- **Three memory types, three different lifecycles**, not just three labels:
  - **Factual** — durable, definitional facts (roles, acronym meanings, client
    relationships). Sticky by design: a new candidate only replaces an existing fact if
    it's meaningfully more informative, so facts don't churn on every incidental
    restatement.
  - **Episodic** — time-bound events, decisions, status snapshots. Decays 30 days after
    the source dictation; the clock resets if the same topic is re-referenced later.
  - **Preference** — app-scoped formatting/tone rules. Scoped overrides: a new
    preference for the same app+key replaces the old one rather than stacking.
- **Explicit rejection:** no acoustic or emotional inference, anywhere in the pipeline.
  The extraction schema has no slot for sentiment — it's not filtered out after the
  fact, it's structurally absent.
- **Deterministic state, probabilistic generation.** Sarvam proposes candidate
  memories; my own code decides whether to store, merge, override, or reject them.
  Retrieval is deterministic term-overlap scoring, not an opaque embedding model, so
  every match can be explained in plain terms.

## Architecture

- **Backend:** FastAPI + SQLAlchemy + Alembic migrations, SQLite database.
- **LLM:** Sarvam `sarvam-105b`, accessed through its OpenAI-compatible
  `/v1/chat/completions` endpoint. Used for memory extraction during ingestion, for
  routing Hey Kivi requests to tools, and for generating final answers and polished
  text. All storage/decay/override decisions happen in my own code, not the LLM.
- **Retrieval:** I don't use embeddings. Sarvam doesn't currently expose an embeddings
  endpoint, and after building this I think the tradeoff is a good one anyway —
  keyword/IDF-based retrieval keeps every match fully explainable, which matters more
  to me here than marginal recall on paraphrased queries. Matching combines:
  - IDF term weighting (rare terms count more than common ones)
  - A distinctiveness-or-coverage rule (a match needs either one highly distinctive
    term, like an acronym, or broad coverage across the query's significant terms —
    catches both short precise queries and longer ones with no single rare anchor)
  - Length normalization (penalizes long documents that accumulate incidental matches
    over short, precise ones)
  - A stopword list and a minimum-token-length filter (drops fragments like a stray
    possessive "'s")
- **Database schema:** `users`, `dictations` (raw ASR + LLM-formatted + app/time
  metadata), `memories` (unified factual/episodic/preference table with a type
  discriminator), `memory_provenance` (links every memory to its source dictation(s)),
  `memory_events` (append-only log of every create/retrieve/update/reject/decay
  decision, with a reason), `hey_kivi_turns` (every request/response with tools used,
  memories cited, latency, and token counts), `shortcuts` (taught trigger→expansion
  pairs, separate from `memories` since matching is exact-phrase substitution, not
  scored retrieval).
- **Frontend:** React + Vite, five surfaces — Hey Kivi (chat), Dictation Feed (history
  replay), Record (simulated live dictation with shortcut expansion), Shortcuts
  (teach/list/delete), Memory Viewer (browse everything Kivi has learned).

## Use cases (the four I chose to build)

I picked these to exercise all three memory types and both the read and write paths,
without building toward every capability the system could theoretically infer:

1. **Find and polish** — "find my most recent Slack update about Project Falcon and
   polish it for a client email." Episodic retrieval + preference-based formatting.
   This was the assignment's own example, so I made sure it was the strongest case.
2. **Factual recall with abstention** — "what does PRJ-FLC stand for?" / "who's the
   Engineering Lead?" Factual memory retrieval, with an explicit abstention path when
   nothing relevant exists rather than inventing an answer.
3. **Preference teach and override** — "format my Slack updates as bullet points from
   now on." Tests the scoped-override conflict resolution directly.
4. **Period recap** — "what did I work on last week?" Aggregates episodic memory and
   raw dictations across a time window, citing every source.

**Deliberately excluded:** open-ended generative assistance (drafting arbitrary content
beyond polishing something already said), multi-app automation, voice input, and any
form of emotional/sentiment inference. I think building toward these would have diluted
the core memory system this assignment is actually evaluating, and voice input is
explicitly called out in the brief as unnecessary.

## Hey Kivi tools

Six tools, each backing one of the use cases above (shortcuts came after the original
four and needed a sixth):

1. `search_episodic` — time/app-filtered + keyword-ranked dictation search
2. `polish_text` — reformats found text using retrieved preference memory
3. `recall_fact` — searches factual **and** episodic memory together (a user asking
   "what did I note about X" shouldn't need to know my internal type taxonomy)
4. `upsert_preference` — creates or overrides a scoped preference
5. `summarize_period` — aggregates dictations + episodic memory over a time range,
   with an optional app filter
6. `recall_shortcut` — searches taught shortcuts; also folded into `recall_fact` so a
   shortcut-flavored question gets answered even if the router picks the more general
   tool

Every tool call logs which memories it touched and why, via `memory_events` and the
`reason` field on every retrieval result — this is what makes it possible to inspect,
for any Hey Kivi answer, exactly which memory produced it and why nothing else matched.

## Shortcuts

Real Kivi has a "shortcuts" feature (taught phrase → fixed expansion text) that I
noticed, once I'd built preference memory, was architecturally almost the same thing —
a scoped key→value mapping the user explicitly teaches. I built it as its own table
rather than overloading `memories`, since shortcut matching is exact-phrase
substitution, not scored retrieval, and I wanted that distinction to be clear rather
than papered over.

- **Teaching** happens only through the dedicated Shortcuts UI (matching how the real
  product does it) — never inferred from casual chat, to keep dictation-time behavior
  predictable.
- **Application** happens at dictation time (the Record tab, or corpus ingestion): any
  taught trigger phrase is expanded before the text is remembered.
- **Recall** happens through Hey Kivi, read-only: a bare or near-bare shortcut lookup
  (e.g. "my sign-off") is answered directly without an LLM routing call at all, for
  speed and determinism; a question-shaped lookup ("what does my sign-off shortcut
  do?") goes through the normal router, which also checks shortcuts inside
  `recall_fact` as a fallback.
- **What it doesn't do:** shortcuts aren't taught via chat, and a single message mixing
  multiple shortcuts with free-form generation (e.g. "draft an email using my sign-off
  and mentioning Project X") isn't reliably composed — see Known Limitations.

## Memory lifecycle in detail

- **Decay:** episodic memories get a 30-day `expires_at` set from their source
  dictation's timestamp. If the same topic is mentioned again before expiry, the clock
  resets and the content updates. A background pass on every ingestion run marks
  expired memories as `expired` (not deleted — they stay inspectable, just excluded
  from retrieval).
- **Stickiness:** factual memories only get replaced by a candidate that's at least
  ~30% longer than the existing value — otherwise it's treated as reinforcement, not an
  update. This exists because I found, while testing, that without it the extractor's
  natural variation in how it restates the same fact caused constant unnecessary
  churn — one acronym ended up with 50+ near-duplicate factual memories before I added
  this rule.
- **Key canonicalization:** the extractor doesn't always use the exact same key string
  for the same entity across mentions (e.g. `PRJ-CMT` vs `PRJ-CMT_project_comet`).
  Before treating two candidates as different slots, I normalize both keys (strip
  non-alphanumerics, lowercase) and also check containment, so cosmetically different
  keys referring to the same thing don't silently fork into duplicate memories.
- **Role-vocabulary guardrail:** a `role:` factual slot can only be created or
  overridden by a candidate that actually contains role/title vocabulary (Lead,
  Engineer, Manager, etc.) — a low-information mention of someone's name in an
  unrelated context can't silently overwrite a correct role fact.
- **App-scope hallucination guardrail:** `preference_teach` only writes a preference if
  the app it claims is literally present in the user's own message. I added this after
  finding, during naive-user testing, that a meta-question like "how do I get you to
  remember things automatically" could get misrouted into fabricating and storing a
  preference the user never actually stated — a real bug, not a hypothetical one.

## User control

The Memory Viewer surfaces every factual, episodic, and preference memory Kivi holds,
including decay countdowns on episodic entries. Shortcuts have their own dedicated
teach/list/delete UI. Nothing requires a developer console or explanation of the
underlying system to use.

## Corpus

I generated a synthetic corpus for one persona — Priya Menon, a PM at a fictional
startup called Loopwork — spanning 45 days, four apps (Slack, Google Docs, Outlook,
Notes), two projects (Falcon and Comet), a small recurring cast of teammates and
clients, and deliberately injected test cases: a preference stated and then overridden,
an episodic memory re-referenced before its 30-day decay and one left to decay
untouched, and roster/project-definition statements to guarantee certain facts are
actually stated somewhere in the corpus. Generation is template-based and seeded (fixed
random seed, fixed anchor date), so it's fully reproducible — no LLM calls involved in
generating the corpus itself, which is disclosed here since the assignment asks about
AI use in every part of the build.

`corpus/generate_corpus.py` produces `corpus/data/dictations.json` (~500+ records) and
a paired `eval_questions.json` (10 fixed questions with known gold answers/abstentions).

## Evaluation

I built four separate test sets over the course of development, each serving a
different purpose:

| Set | Size | Purpose |
|---|---|---|
| `eval_questions.json` | 10 | Fixed core questions, one per use case + abstention/decay cases |
| `held_out_questions.json` | 9 | Different phrasings of the same use cases, designed after the core set was passing, to check the fixes generalized rather than overfit |
| `qa_suites.json` | 35 | Broader stress test — multi-hop questions, malformed/ASR-style input, injection-adjacent phrasing, cold-state checks, regression tests for specific bugs found during development |
| `naive_user_queries.json` | 15 | Written last, deliberately without knowledge of my own tool names or routing logic — casual, vague, slang-heavy phrasing meant to simulate how someone who's never seen the architecture would actually talk to it |

**Results** (run via `python eval/run_eval.py [questions_file] [report_name]`):

- Core set: **7/10** — reproducible: identical pass/fail pattern across 3
  consecutive runs against the same database state, confirming that the variance I saw
  earlier in development was caused by changing database state between test runs, not
  genuine LLM nondeterminism at temperature 0 against fixed input.
- Held-out set: **7/9** — same reproducibility check, same result.
- QA stress suite: **27/35**, last measured before the final round of bug
  fixes (app-scope guardrail, shortcuts recall improvements) — see Known Limitations
  for what's understood about the remaining failures.
- Naive-user set: **10/15** — meaningfully lower than the other three, and
  I think that's the most honest number in this table. It found a real bug (see below)
  and points at genuine, disclosed architectural tradeoffs rather than implementation
  mistakes.

Every eval run produces `eval/results/<name>.json` (full machine-readable detail: input,
retrieved evidence with scores and reasons, tool called, response, pass/fail, latency,
tokens, cost) and `<name>.md` (human-readable summary table + failure detail).

### Unit tests

24 fast unit tests in `backend/tests/`, no LLM calls, full suite runs in under 2 seconds
(`python -m pytest tests/ -v`). These cover the deterministic core specifically: the
tokenizer, IDF weighting, the distinctiveness/coverage ranking rule, decay logic, the
role-vocabulary guardrail, key canonicalization (including a direct regression test for
the PRJ-CMT key-fork bug I found and fixed), the app-scope hallucination guardrail, and
shortcut creation/expansion. These exist specifically so the deterministic parts of the
system have a fast, checked-in regression net that doesn't depend on LLM availability
or cost anything to run repeatedly.

## Known limitations

I'd rather name these precisely than leave them to be discovered:

- **Generic/verbose query degradation.** Retrieval ranks by term rarity, not semantic
  meaning. A query whose only significant word is common in the corpus (e.g. "tomorrow"
  appearing in many scheduling mentions) can occasionally clear the relevance bar on
  that word alone; conversely, a query about a common entity with no second distinctive
  term (e.g. "what is Project Comet about?") can lose to a more recent but less
  definitional mention on a recency tiebreak. This is a direct, disclosed consequence
  of choosing inspectable keyword retrieval over embeddings.
- **Vocabulary mismatch.** Because there's no semantic layer, a query that describes
  something in different words than the corpus uses (e.g. "the money situation" instead
  of "budget") can fail to retrieve, even though a human would immediately understand
  the connection. This is the most direct cost of the embeddings-vs-keyword tradeoff.
- **Length-normalization can work against short definitional facts.** The same
  normalization that stops long documents from winning on incidental keyword overlap
  can, in the opposite direction, make a short but highly informative factual record
  (like a role definition) score lower than several shorter episodic mentions of the
  same name. Found via naive-user testing (e.g. "what's up with that vikram guy" failed
  to surface the role fact).
- **Raw dictation transcripts are not searchable directly** — only what extraction
  captured into structured memory. This is a deliberate "no clutter" choice from my
  Part 1 position, but it means a detail present in a dictation that extraction didn't
  turn into a memory is effectively unreachable, even though the text exists in the
  `dictations` table.
- **Compound requests** (asking for two things in one message, e.g. "find my Falcon
  update and also tell me who the Comet contact is," or a message mixing two taught
  shortcuts with free-form generation) resolve at most one part of the request. The
  router picks a single tool per turn by design; I chose not to build multi-intent
  decomposition given the scope of this assignment.
- **No "what do you know about me" capability.** An open-ended request to summarize
  everything Kivi has learned isn't one of the four designed use cases, so it currently
  abstains rather than attempting a full memory dump. This came up in naive-user
  testing as a very natural first question a real user might ask, and I'd consider it
  a legitimate scope gap rather than a bug.
- **LLM routing has a small amount of inherent variance** across different database
  states, even at temperature 0 — this is a known property of hosted LLM inference
  generally (batching, floating-point non-associativity across hardware), not specific
  to Sarvam. In testing, results were bit-identical across repeated runs against a
  *fixed* database state, so this mainly matters when comparing runs taken at different
  points during development, not for a single reviewer's evaluation run.

## AI use disclosure

**Part 1** (positioning statement and vision document) is entirely my own thinking, per
the assignment's explicit instruction — I did not use generative AI to arrive at the
position or write either document.

**Part 2** (build) was done with Claude as an AI pair-programmer throughout:
architecture decisions were my own, code for the backend/frontend/tests, debugging, and the design
of the eval question sets were all done in collaboration with Claude, with me directing
priorities, testing every change against the running system, and making the final calls
on tradeoffs (e.g. keyword retrieval over embeddings, which use cases to build, what to
treat as a real bug versus a disclosed limitation). The synthetic corpus was generated
by a deterministic Python script (no LLM calls); memory extraction and Hey Kivi's
responses at runtime use Sarvam's `sarvam-105b`.