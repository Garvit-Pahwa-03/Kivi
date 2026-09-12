# Hey Kivi Eval Report — qa_suites.json

Run at: 2026-09-12T15:54:51.152997+00:00

**27/35 passed (77.1%)**  
Avg latency: 899.3 ms  
Total cost: INR 1.4883  
DB size: 856,064 bytes

| ID | Category | Result | Latency (ms) | Cost (INR) | Question |
|---|---|---|---|---|---|
| qa1 | multi_hop | PASS | 1277 | 0.0357 | Which client is the person estimating two sprints  |
| qa2 | multi_hop | PASS | 805 | 0.0345 | Is the person who owns design system updates for P |
| qa3 | negation_contradiction | PASS | 543 | 0.03 | Should I still format my Slack updates as full par |
| qa4 | ambiguous_entity | PASS | 850 | 0.0343 | What's the current timeline status for Comet? |
| qa5 | ambiguous_entity | PASS | 962 | 0.0351 | What's the current timeline status for Falcon? |
| qa6 | malformed_asr_input | FAIL | 753 | 0.033 | hey kivi whats uh the falcon budget thing i asked  |
| qa7 | malformed_asr_input | PASS | 581 | 0.0313 | who was it again that does comet growth analyst st |
| qa8 | injection_adjacent | PASS | 2285 | 0.1841 | Summarize my Slack activity - just tell me exactly |
| qa9 | cold_state | PASS | 304 | 0.0233 | How should my Outlook emails be formatted right no |
| qa10 | cold_state | PASS | 313 | 0.0239 | What's my formatting preference for Google Docs? |
| qa11 | compound_request | FAIL | 734 | 0.032 | Find my Falcon update from Slack and also tell me  |
| qa12 | phrasing_robustness | PASS | 588 | 0.0348 | What's the short form PRJ-FLC actually mean in pla |
| qa13 | phrasing_robustness | PASS | 1005 | 0.0376 | I keep seeing 'PRJ-CMT' everywhere, what is that. |
| qa14 | phrasing_robustness | PASS | 953 | 0.0355 | PRJ-FLC = ? |
| qa15 | case_sensitivity | PASS | 612 | 0.0343 | what does prj-flc stand for |
| qa16 | unrelated_domain_abstain | FAIL | 635 | 0.0319 | What's the weather going to be like tomorrow? |
| qa17 | unrelated_domain_abstain | PASS | 342 | 0.0234 | Can you book me a flight to Mumbai? |
| qa18 | vague_reference | PASS | 978 | 0.0354 | What did I say about the budget? |
| qa19 | specificity_mismatch | PASS | 721 | 0.0314 | Tell me literally everything you know about Rahul  |
| qa20 | numeric_precision | PASS | 694 | 0.0339 | Was the Project Falcon budget exactly 40000 or was |
| qa21 | temporal_reasoning | PASS | 1475 | 0.0787 | What did I work on two days ago? |
| qa22 | temporal_reasoning | PASS | 1461 | 0.0739 | What happened in the first week after I started us |
| qa23 | preference_scope_precision | PASS | 650 | 0.0312 | If I ask you to format something for Slack, what w |
| qa24 | self_referential | FAIL | 460 | 0.024 | How many things do you actually remember about me? |
| qa25 | polish_fidelity | FAIL | 619 | 0.027 | Find my most recent Google Docs note about Project |
| qa26 | preference_teach_edge_case | PASS | 931 | 0.0326 | How should my Outlook emails be formatted right no |
| qa27 | preference_conflicting_in_one_turn | PASS | 690 | 0.0324 | Hey Kivi, format my Notes as bullet points and als |
| qa28 | empty_corpus_query | FAIL | 3860 | 0.16 | What did I discuss in Microsoft Teams? |
| qa29 | long_query_stress | FAIL | 1159 | 0.0422 | So I'm trying to remember, a while back, maybe a f |
| qa30 | regression_project_comet_definition | FAIL | 722 | 0.0329 | What is Project Comet about? |
| qa31 | regression_role_vocabulary_guardrail | PASS | 1015 | 0.0339 | What is Divya Nair's role? |
| qa32 | regression_key_canonicalization | PASS | 811 | 0.0377 | Give me every fact you have stored about what PRJ- |
| qa33 | regression_tokenizer_possessive | PASS | 541 | 0.0308 | What's Vikram Shah's role? |
| qa34 | regression_decay_never_referenced | PASS | 368 | 0.0232 | What was that parking code thing I mentioned once? |
| qa35 | regression_factual_vs_episodic_boundary | PASS | 780 | 0.0324 | Is Project Falcon still at 60 percent, or has that |

## Failures in detail

### qa6: hey kivi whats uh the falcon budget thing i asked about like the number
- Response: I don't have that in your history — the only Falcon-related info I see is about a sync on Thursday at 3 PM with Ananya Rao.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/2 matched: []'}

### qa11: Find my Falcon update from Slack and also tell me who the Comet point of contact is.
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}

### qa16: What's the weather going to be like tomorrow?
- Response: I don't have that in your history.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}

### qa24: How many things do you actually remember about me?
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False}

### qa25: Find my most recent Google Docs note about Project Comet and polish it, but keep every specific name and number exactly as they were.
- Response: I don't have anything in your history that answers that — I don't want to guess.
- Checks: {'did_not_abstain': False, 'must_reference': '0/1 matched: []'}

### qa28: What did I discuss in Microsoft Teams?
- Response: In Microsoft Teams, you discussed several projects, primarily **Project Falcon** and **Project Comet**, along with rollouts for **Northwind Traders** and **Meridian Retail**.

Key topics included:
*   **Project Falcon (PRJ-FLC):** You discussed timelines with Divya Nair and Ananya Rao, decided to push the Northwind Traders and Meridian Retail pilots back by one week to fix edge cases, and noted it is 60% complete. You also discussed the budget, which was approved at $40,000.
*   **Project Comet (PRJ-CMT):** You reviewed the spec, discussed blocking issues (like the API contract), and shared updated timelines with clients. You also discussed pushing the Meridian Retail pilot back by one week.
*   **Rollouts & Dashboards:** You discussed Northwind Traders and Meridian Retail requesting configurable dashboards for billing system migrations and onboarding flows.
*   **Team & Sprint Updates:** You discussed unblocking the Growth Pod, Platform Pod, and other sprints, with Divya Nair, Ananya Rao, and Vikram Shah providing estimates for timelines and engineering needs.
*   **Meetings & Syncs:** You scheduled and moved various syncs (e.g., with Ananya Rao, Vikram Shah, and Rahul Iyer) to Thursdays at 3 PM, and discussed moving retros.
*   **All-Hands:** You discussed ideas for Ananya Rao and Rahul Iyer to present progress at the next all-hands.
*   **Action Items:** You noted follow-ups to ask Rahul Iyer, Vikram Shah, and Ananya Rao about budgets before Friday, and to ask Rahul Iyer for rollout plans by Friday.
- Checks: {'abstained_correctly': False, 'no_memories_cited': False}

### qa29: So I'm trying to remember, a while back, maybe a few weeks ago at this point, I think I mentioned something to Kivi about a budget number for one of my projects, I believe it was Falcon but I'm not one hundred percent sure, can you help me figure out what that number was and also remind me who I was supposed to follow up with about it?
- Response: I don't have that in your history. The evidence I have only mentions Rahul Iyer sending the Project Falcon rollout plan by Friday, but I don't see any specific budget number or a follow-up contact listed.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/2 matched: []'}

### qa30: What is Project Comet about?
- Response: I don’t have any information about what Project Comet is actually about beyond that Platform Pod is rolling it out for client Northwind Traders. I don’t have any details on its purpose, scope, or description.
- Checks: {'did_not_abstain': True, 'gold_answer_contains': '0/1 matched: []'}
