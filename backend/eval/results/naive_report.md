# Hey Kivi Eval Report — naive_user_queries.json

Run at: 2026-09-13T09:37:10.583669+00:00

**8/15 passed (53.3%)**  
Avg latency: 851.7 ms  
Total cost: INR 0.5135  
DB size: 1,146,880 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| nu1 | uncategorized | PASS | 1144 | 0.0364 | hey so what's going on with falcon these days |
| nu2 | uncategorized | PASS | 937 | 0.0357 | can u remind me who's doing what on comet |
| nu3 | uncategorized | FAIL | 282 | 0.0255 | did we ever figure out the money situation for fal |
| nu4 | uncategorized | PASS | 1424 | 0.0434 | i need to send something to karan about the meridi |
| nu5 | uncategorized | FAIL | 575 | 0.0268 | whats rahuls deal |
| nu6 | uncategorized | PASS | 1401 | 0.0374 | is there anything i'm forgetting about this week |
| nu7 | uncategorized | PASS | 1352 | 0.0455 | can you clean this up for slack: finished the falc |
| nu8 | uncategorized | PASS | 940 | 0.038 | not sure if i already told you this but divya is t |
| nu9 | uncategorized | PASS | 806 | 0.0349 | quick one - comet or falcon, which one has the nor |
| nu10 | uncategorized | FAIL | 769 | 0.0346 | ugh i forgot the acronym thing for the billing pro |
| nu11 | uncategorized | FAIL | 368 | 0.0259 | sorry me again, when's the falcon sync supposed to |
| nu12 | uncategorized | FAIL | 365 | 0.0258 | what do you know about me so far |
| nu13 | uncategorized | PASS | 559 | 0.0317 | just checking - are my slack messages still doing  |
| nu14 | uncategorized | FAIL | 978 | 0.0361 | how do i get you to remember stuff automatically |
| nu15 | uncategorized | FAIL | 875 | 0.0358 | whats up with that vikram guy, what does he even d |

## Failures in detail

### nu3: did we ever figure out the money situation for falcon
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'gold_answer_contains': '0/2 matched: []'}

### nu5: whats rahuls deal
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'gold_answer_contains': '0/1 matched: []'}

### nu10: ugh i forgot the acronym thing for the billing project again
- Response: I don't have that in your history.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/2 matched: []'}

### nu11: sorry me again, when's the falcon sync supposed to happen
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False}

### nu12: what do you know about me so far
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False}

### nu14: how do i get you to remember stuff automatically
- Response: I already have a preference set to automatically remember all notes and facts without needing explicit confirmation. So, going forward, I’ll retain things from our conversations on my own.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}

### nu15: whats up with that vikram guy, what does he even do here
- Response: Vikram Shah is helping unblock the Platform Pod and Growth Pod sprints. You also need to ask him about the Project Comet budget before Friday.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/1 matched: []'}
