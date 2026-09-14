# Hey Kivi Eval Report — eval_questions.json

Run at: 2026-09-13T06:39:50.124765+00:00

**7/10 passed (70.0%)**  
Avg latency: 1513.9 ms  
Total cost: INR 0.4921  
DB size: 1,060,864 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| q1 | find_and_polish | PASS | 3153 | 0.0503 | Hey Kivi, find my most recent Slack update about P |
| q2 | find_and_polish | FAIL | 966 | 0.0296 | Find the dictation I did in Google Docs about Proj |
| q3 | factual_recall | PASS | 1183 | 0.0368 | What does PRJ-FLC stand for? |
| q4 | factual_recall | PASS | 974 | 0.033 | Who is the Engineering Lead I work with? |
| q5 | factual_recall_abstain | FAIL | 940 | 0.0324 | What is the status of Project Nimbus? |
| q6 | factual_recall_abstain | FAIL | 1626 | 0.0354 | What's Karan Bose's role on my team? |
| q7 | preference | PASS | 907 | 0.0314 | How should my Slack updates be formatted right now |
| q8 | period_recap | PASS | 3779 | 0.1822 | What did I work on in the last week? |
| q9 | decay | PASS | 507 | 0.0259 | What was that parking validation code I noted a wh |
| q10 | decay_reset | PASS | 1104 | 0.0351 | What was the Project Falcon budget ask I noted? |

## Failures in detail

### q2: Find the dictation I did in Google Docs about Project Comet's timeline and clean it up.
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}

### q5: What is the status of Project Nimbus?
- Response: I don't have any information about Project Nimbus in your history.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}

### q6: What's Karan Bose's role on my team?
- Response: I don't have that in your history — there's no information about Karan Bose's role on your team.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}
