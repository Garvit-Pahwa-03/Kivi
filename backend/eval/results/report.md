# Hey Kivi Eval Report — eval_questions.json

Run at: 2026-09-13T18:42:26.739248+00:00

**7/10 passed (70.0%)**  
Avg latency: 1024.0 ms  
Total cost: INR 0.5276  
DB size: 1,167,360 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| q1 | find_and_polish | PASS | 1630 | 0.0524 | Hey Kivi, find my most recent Slack update about P |
| q2 | find_and_polish | FAIL | 1421 | 0.0333 | Find the dictation I did in Google Docs about Proj |
| q3 | factual_recall | PASS | 1010 | 0.04 | What does PRJ-FLC stand for? |
| q4 | factual_recall | PASS | 880 | 0.0372 | Who is the Engineering Lead I work with? |
| q5 | factual_recall_abstain | FAIL | 713 | 0.0372 | What is the status of Project Nimbus? |
| q6 | factual_recall_abstain | FAIL | 1072 | 0.0427 | What's Karan Bose's role on my team? |
| q7 | preference | PASS | 720 | 0.036 | How should my Slack updates be formatted right now |
| q8 | period_recap | PASS | 1700 | 0.1803 | What did I work on in the last week? |
| q9 | decay | PASS | 308 | 0.0302 | What was that parking validation code I noted a wh |
| q10 | decay_reset | PASS | 786 | 0.0383 | What was the Project Falcon budget ask I noted? |

## Failures in detail

### q2: Find the dictation I did in Google Docs about Project Comet's timeline and clean it up.
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}

### q5: What is the status of Project Nimbus?
- Response: I don't have any information about Project Nimbus in your history.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}

### q6: What's Karan Bose's role on my team?
- Response: I don't have that in your history. The evidence only mentions Karan in the context of presenting the Nexus project to Prof Ashwin on September 13, 2026, but it doesn't specify his role on your team.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}
