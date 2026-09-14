# Hey Kivi Eval Report — eval_questions.json

Run at: 2026-09-13T06:39:29.754798+00:00

**7/10 passed (70.0%)**  
Avg latency: 1367.8 ms  
Total cost: INR 0.4833  
DB size: 1,048,576 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| q1 | find_and_polish | PASS | 2931 | 0.0485 | Hey Kivi, find my most recent Slack update about P |
| q2 | find_and_polish | FAIL | 895 | 0.0296 | Find the dictation I did in Google Docs about Proj |
| q3 | factual_recall | PASS | 949 | 0.0347 | What does PRJ-FLC stand for? |
| q4 | factual_recall | PASS | 1140 | 0.0332 | Who is the Engineering Lead I work with? |
| q5 | factual_recall_abstain | FAIL | 1100 | 0.0333 | What is the status of Project Nimbus? |
| q6 | factual_recall_abstain | FAIL | 1212 | 0.0371 | What's Karan Bose's role on my team? |
| q7 | preference | PASS | 799 | 0.0312 | How should my Slack updates be formatted right now |
| q8 | period_recap | PASS | 3218 | 0.1765 | What did I work on in the last week? |
| q9 | decay | PASS | 536 | 0.0259 | What was that parking validation code I noted a wh |
| q10 | decay_reset | PASS | 898 | 0.0333 | What was the Project Falcon budget ask I noted? |

## Failures in detail

### q2: Find the dictation I did in Google Docs about Project Comet's timeline and clean it up.
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}

### q5: What is the status of Project Nimbus?
- Response: I don't have that in the user's history.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}

### q6: What's Karan Bose's role on my team?
- Response: Karan is scheduled to present the Nexus project presentation to Prof Ashwin on September 13, 2026. I don't have his specific role on your team in the provided history.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}
