# Hey Kivi Eval Report — naive_user_queries.json

Run at: 2026-09-13T19:04:54.820745+00:00

**10/15 passed (66.7%)**  
Avg latency: 892.0 ms  
Total cost: INR 0.7232  
DB size: 1,290,240 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| nu1 | uncategorized | PASS | 1200 | 0.0392 | hey so what's going on with falcon these days |
| nu2 | uncategorized | PASS | 812 | 0.0402 | can u remind me who's doing what on comet |
| nu3 | uncategorized | FAIL | 361 | 0.0303 | did we ever figure out the money situation for fal |
| nu4 | uncategorized | PASS | 1436 | 0.0477 | i need to send something to karan about the meridi |
| nu5 | uncategorized | PASS | 599 | 0.0382 | whats rahuls deal |
| nu6 | uncategorized | PASS | 2648 | 0.1908 | is there anything i'm forgetting about this week |
| nu7 | uncategorized | PASS | 1322 | 0.0501 | can you clean this up for slack: finished the falc |
| nu8 | uncategorized | PASS | 803 | 0.0408 | not sure if i already told you this but divya is t |
| nu9 | uncategorized | PASS | 592 | 0.0387 | quick one - comet or falcon, which one has the nor |
| nu10 | uncategorized | FAIL | 523 | 0.0386 | ugh i forgot the acronym thing for the billing pro |
| nu11 | uncategorized | FAIL | 998 | 0.0307 | sorry me again, when's the falcon sync supposed to |
| nu12 | uncategorized | FAIL | 294 | 0.0306 | what do you know about me so far |
| nu13 | uncategorized | PASS | 698 | 0.0385 | just checking - are my slack messages still doing  |
| nu14 | uncategorized | PASS | 287 | 0.0293 | how do i get you to remember stuff automatically |
| nu15 | uncategorized | FAIL | 807 | 0.0395 | whats up with that vikram guy, what does he even d |

## Failures in detail

### nu3: did we ever figure out the money situation for falcon
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'gold_answer_contains': '0/2 matched: []'}

### nu10: ugh i forgot the acronym thing for the billing project again
- Response: I don't have that in the user's history.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/2 matched: []'}

### nu11: sorry me again, when's the falcon sync supposed to happen
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False}

### nu12: what do you know about me so far
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False}

### nu15: whats up with that vikram guy, what does he even do here
- Response: Vikram Shah is helping unblock the Platform and Growth Pod sprints, and we need to ask him about the Project Comet budget before Friday.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/1 matched: []'}
