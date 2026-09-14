# Hey Kivi Eval Report — held_out_questions.json

Run at: 2026-09-13T06:41:27.315245+00:00

**7/9 passed (77.8%)**  
Avg latency: 1681.7 ms  
Total cost: INR 0.4586  
DB size: 1,114,112 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| h1 | find_and_polish_paraphrase | FAIL | 1152 | 0.0292 | Pull up my last note in Google Docs about Project  |
| h2 | find_and_polish_novel_direction | PASS | 2896 | 0.0494 | Find the email I sent about the Project Comet roll |
| h3 | factual_recall_paraphrase | PASS | 1681 | 0.0329 | What's Divya Nair's job title? |
| h4 | factual_recall_paraphrase | PASS | 1402 | 0.0388 | Tell me what PRJ-CMT refers to. |
| h5 | factual_recall_abstain_novel | PASS | 610 | 0.0258 | What's the WBS number for the marketing project? |
| h6 | preference_query_untaught_app | FAIL | 909 | 0.0316 | How should my Notes be formatted right now? |
| h7 | preference_teach_then_query | PASS | 984 | 0.0316 | How should my Notes be formatted right now? |
| h8 | period_recap_paraphrase | PASS | 4482 | 0.1851 | Give me a rundown of what I've been doing this pas |
| h9 | decay_reset_paraphrase | PASS | 1019 | 0.0342 | How much budget did I end up asking for on Falcon? |

## Failures in detail

### h1: Pull up my last note in Google Docs about Project Falcon and tidy it up for a Slack post.
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}

### h6: How should my Notes be formatted right now?
- Response: Your Notes should be formatted as short bullet reminders, not full sentences.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}
