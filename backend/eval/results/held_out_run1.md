# Hey Kivi Eval Report — held_out_questions.json

Run at: 2026-09-13T06:40:22.134094+00:00

**7/9 passed (77.8%)**  
Avg latency: 1515.3 ms  
Total cost: INR 0.4511  
DB size: 1,081,344 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| h1 | find_and_polish_paraphrase | FAIL | 1075 | 0.0288 | Pull up my last note in Google Docs about Project  |
| h2 | find_and_polish_novel_direction | PASS | 2410 | 0.0453 | Find the email I sent about the Project Comet roll |
| h3 | factual_recall_paraphrase | PASS | 1247 | 0.0329 | What's Divya Nair's job title? |
| h4 | factual_recall_paraphrase | PASS | 1144 | 0.036 | Tell me what PRJ-CMT refers to. |
| h5 | factual_recall_abstain_novel | PASS | 550 | 0.0258 | What's the WBS number for the marketing project? |
| h6 | preference_query_untaught_app | FAIL | 1036 | 0.0321 | How should my Notes be formatted right now? |
| h7 | preference_teach_then_query | PASS | 928 | 0.0321 | How should my Notes be formatted right now? |
| h8 | period_recap_paraphrase | PASS | 4002 | 0.1822 | Give me a rundown of what I've been doing this pas |
| h9 | decay_reset_paraphrase | PASS | 1246 | 0.0359 | How much budget did I end up asking for on Falcon? |

## Failures in detail

### h1: Pull up my last note in Google Docs about Project Falcon and tidy it up for a Slack post.
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}

### h6: How should my Notes be formatted right now?
- Response: Your Notes should be formatted as bullet points and also as full paragraphs.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}
