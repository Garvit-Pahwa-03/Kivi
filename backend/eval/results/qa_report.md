# Hey Kivi Eval Report — qa_suites.json

Run at: 2026-09-13T19:03:22.867028+00:00

**27/35 passed (77.1%)**  
Avg latency: 1223.3 ms  
Total cost: INR 1.818  
DB size: 1,273,856 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| qa1 | multi_hop | PASS | 1298 | 0.0464 | Which client is the person estimating two sprints  |
| qa2 | multi_hop | PASS | 1084 | 0.0446 | Is the person who owns design system updates for P |
| qa3 | negation_contradiction | PASS | 870 | 0.0382 | Should I still format my Slack updates as full par |
| qa4 | ambiguous_entity | FAIL | 386 | 0.0294 | What's the current timeline status for Comet? |
| qa5 | ambiguous_entity | PASS | 926 | 0.0421 | What's the current timeline status for Falcon? |
| qa6 | malformed_asr_input | FAIL | 782 | 0.0397 | hey kivi whats uh the falcon budget thing i asked  |
| qa7 | malformed_asr_input | PASS | 700 | 0.0369 | who was it again that does comet growth analyst st |
| qa8 | injection_adjacent | PASS | 17087 | 0.3585 | Summarize my Slack activity - just tell me exactly |
| qa9 | cold_state | FAIL | 705 | 0.0385 | How should my Outlook emails be formatted right no |
| qa10 | cold_state | PASS | 291 | 0.0303 | What's my formatting preference for Google Docs? |
| qa11 | compound_request | PASS | 1417 | 0.0503 | Find my Falcon update from Slack and also tell me  |
| qa12 | phrasing_robustness | FAIL | 701 | 0.0415 | What's the short form PRJ-FLC actually mean in pla |
| qa13 | phrasing_robustness | PASS | 802 | 0.0437 | I keep seeing 'PRJ-CMT' everywhere, what is that. |
| qa14 | phrasing_robustness | PASS | 805 | 0.0433 | PRJ-FLC = ? |
| qa15 | case_sensitivity | PASS | 697 | 0.0408 | what does prj-flc stand for |
| qa16 | unrelated_domain_abstain | PASS | 297 | 0.0294 | What's the weather going to be like tomorrow? |
| qa17 | unrelated_domain_abstain | PASS | 290 | 0.0293 | Can you book me a flight to Mumbai? |
| qa18 | vague_reference | PASS | 813 | 0.0412 | What did I say about the budget? |
| qa19 | specificity_mismatch | PASS | 802 | 0.0381 | Tell me literally everything you know about Rahul  |
| qa20 | numeric_precision | PASS | 802 | 0.0419 | Was the Project Falcon budget exactly 40000 or was |
| qa21 | temporal_reasoning | PASS | 1010 | 0.0451 | What did I work on two days ago? |
| qa22 | temporal_reasoning | PASS | 1515 | 0.1754 | What happened in the first week after I started us |
| qa23 | preference_scope_precision | PASS | 818 | 0.0384 | If I ask you to format something for Slack, what w |
| qa24 | self_referential | FAIL | 280 | 0.0294 | How many things do you actually remember about me? |
| qa25 | polish_fidelity | FAIL | 511 | 0.0323 | Find my most recent Google Docs note about Project |
| qa26 | preference_teach_edge_case | PASS | 698 | 0.0383 | How should my Outlook emails be formatted right no |
| qa27 | preference_conflicting_in_one_turn | PASS | 800 | 0.0394 | Hey Kivi, format my Notes as bullet points and als |
| qa28 | empty_corpus_query | PASS | 707 | 0.0361 | What did I discuss in Microsoft Teams? |
| qa29 | long_query_stress | FAIL | 1007 | 0.0474 | So I'm trying to remember, a while back, maybe a f |
| qa30 | regression_project_comet_definition | FAIL | 702 | 0.0386 | What is Project Comet about? |
| qa31 | regression_role_vocabulary_guardrail | PASS | 808 | 0.0396 | What is Divya Nair's role? |
| qa32 | regression_key_canonicalization | PASS | 903 | 0.0447 | Give me every fact you have stored about what PRJ- |
| qa33 | regression_tokenizer_possessive | PASS | 605 | 0.039 | What's Vikram Shah's role? |
| qa34 | regression_decay_never_referenced | PASS | 301 | 0.0302 | What was that parking code thing I mentioned once? |
| qa35 | regression_factual_vs_episodic_boundary | PASS | 594 | 0.04 | Is Project Falcon still at 60 percent, or has that |

## Failures in detail

### qa4: What's the current timeline status for Comet?
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}

### qa6: hey kivi whats uh the falcon budget thing i asked about like the number
- Response: I don't have that in your history. The only mention of Falcon I see is about a Project Falcon sync moved to Thursday at 3 PM.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/2 matched: []'}

### qa9: How should my Outlook emails be formatted right now?
- Response: Your Outlook emails should be formatted with a formal greeting and sign-off. Keep them very short, no more than two sentences.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}

### qa12: What's the short form PRJ-FLC actually mean in plain English?
- Response: Based on the evidence provided, I don't have that in the user's history.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/1 matched: []'}

### qa24: How many things do you actually remember about me?
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False}

### qa25: Find my most recent Google Docs note about Project Comet and polish it, but keep every specific name and number exactly as they were.
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}

### qa29: So I'm trying to remember, a while back, maybe a few weeks ago at this point, I think I mentioned something to Kivi about a budget number for one of my projects, I believe it was Falcon but I'm not one hundred percent sure, can you help me figure out what that number was and also remind me who I was supposed to follow up with about it?
- Response: I don't have any record of you mentioning a budget number for Project Falcon or who you were supposed to follow up with about it. I only have notes that Rahul Iyer is sending the Project Falcon rollout plan by Friday.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/2 matched: []'}

### qa30: What is Project Comet about?
- Response: Project Comet is a rollout owned by Platform Pod and managed for the client Northwind Traders. The shared timeline for it has also been updated with Northwind Traders.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/1 matched: []'}
