# Hey Kivi Eval Report — held_out_questions.json

Run at: 2026-09-12T15:54:01.789471+00:00

**8/9 passed (88.9%)**  
Avg latency: 881.4 ms  
Total cost: INR 0.4282  
DB size: 811,008 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| h1 | find_and_polish_paraphrase | FAIL | 678 | 0.0272 | Pull up my last note in Google Docs about Project  |
| h2 | find_and_polish_novel_direction | PASS | 1238 | 0.0432 | Find the email I sent about the Project Comet roll |
| h3 | factual_recall_paraphrase | PASS | 539 | 0.0312 | What's Divya Nair's job title? |
| h4 | factual_recall_paraphrase | PASS | 778 | 0.0358 | Tell me what PRJ-CMT refers to. |
| h5 | factual_recall_abstain_novel | PASS | 379 | 0.0238 | What's the WBS number for the marketing project? |
| h6 | preference_query_untaught_app | PASS | 300 | 0.0238 | How should my Notes be formatted right now? |
| h7 | preference_teach_then_query | PASS | 612 | 0.0294 | How should my Notes be formatted right now? |
| h8 | period_recap_paraphrase | PASS | 2551 | 0.1818 | Give me a rundown of what I've been doing this pas |
| h9 | decay_reset_paraphrase | PASS | 858 | 0.032 | How much budget did I end up asking for on Falcon? |

## Failures in detail

### h1: Pull up my last note in Google Docs about Project Falcon and tidy it up for a Slack post.
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}
