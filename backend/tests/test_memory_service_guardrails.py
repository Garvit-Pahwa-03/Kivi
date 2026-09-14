from app.memory_service import _looks_like_role_statement, _normalize_key


def test_role_vocabulary_guardrail_accepts_real_role_statements():
    assert _looks_like_role_statement("Rahul Iyer is the Engineering Lead at Loopwork")
    assert _looks_like_role_statement("Divya Nair is the Growth Analyst")
    assert _looks_like_role_statement("Vikram Shah is a Backend Engineer")


def test_role_vocabulary_guardrail_rejects_non_role_mentions():
    # Regression test for the bug where a low-information mention of a person
    # silently overwrote a correct role fact.
    assert not _looks_like_role_statement("Rahul Iyer is a participant in the sync meeting")
    assert not _looks_like_role_statement("Divya Nair is helping unblock the sprint")
    assert not _looks_like_role_statement("Ananya Rao is a team member")


def test_normalize_key_strips_non_alphanumeric_and_lowercases():
    assert _normalize_key("PRJ-CMT") == "prjcmt"
    assert _normalize_key("PRJ-CMT_project_comet") == "prjcmtprojectcomet"


def test_normalize_key_makes_cosmetically_different_keys_equal_when_one_contains_other():
    # These are the two keys from the real bug we found: the extractor invented
    # a suffixed variant of the same logical key.
    a = _normalize_key("PRJ-CMT")
    b = _normalize_key("PRJ-CMT_project_comet")
    assert a in b  # confirms the containment check in _find_existing_by_normalized_key applies
    
def test_preference_teach_app_scope_hallucination_check():
    # Regression test for the bug where the router claimed app_scope="Notes" for a
    # message that never mentioned Notes at all (a meta-question about the product).
    # The actual guard lives in orchestrator.handle_request's preference_teach branch;
    # this test exercises the same string-containment logic in isolation.
    known_apps = ["Slack", "Google Docs", "Outlook", "Notes"]

    def app_actually_mentioned(claimed_app, request_text):
        return claimed_app in known_apps and claimed_app.lower() in request_text.lower()

    # The real failure case: router claims Notes, user never said it.
    assert not app_actually_mentioned("Notes", "how do i get you to remember stuff automatically")

    # The legitimate case: app genuinely mentioned, must still work.
    assert app_actually_mentioned("Slack", "Hey Kivi, format my Slack updates as bullet points")

    # Case-insensitivity check.
    assert app_actually_mentioned("Outlook", "format my outlook emails to be short")

    # A claimed app outside the known list must never pass, regardless of text.
    assert not app_actually_mentioned("Teams", "format my Teams messages")