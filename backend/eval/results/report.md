# Hey Kivi Eval Report — eval_questions.json

Run at: 2026-09-12T15:53:38.289860+00:00

**7/10 passed (70.0%)**  
Avg latency: 1024.1 ms  
Total cost: INR 0.4727  
DB size: 798,720 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| q1 | find_and_polish | PASS | 1810 | 0.0467 | Hey Kivi, find my most recent Slack update about P |
| q2 | find_and_polish | FAIL | 601 | 0.0275 | Find the dictation I did in Google Docs about Proj |
| q3 | factual_recall | PASS | 784 | 0.0331 | What does PRJ-FLC stand for? |
| q4 | factual_recall | PASS | 848 | 0.0327 | Who is the Engineering Lead I work with? |
| q5 | factual_recall_abstain | FAIL | 794 | 0.0304 | What is the status of Project Nimbus? |
| q6 | factual_recall_abstain | FAIL | 897 | 0.0328 | What's Karan Bose's role on my team? |
| q7 | preference | PASS | 524 | 0.0289 | How should my Slack updates be formatted right now |
| q8 | period_recap | PASS | 2954 | 0.1851 | What did I work on in the last week? |
| q9 | decay | PASS | 313 | 0.0234 | What was that parking validation code I noted a wh |
| q10 | decay_reset | PASS | 716 | 0.0321 | What was the Project Falcon budget ask I noted? |

## Failures in detail

### q2: Find the dictation I did in Google Docs about Project Comet's timeline and clean it up.
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}

### q5: What is the status of Project Nimbus?
- Response: I don't have any information in your history about Project Nimbus.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}

### q6: What's Karan Bose's role on my team?
- Response: I don't have that in your history.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}
