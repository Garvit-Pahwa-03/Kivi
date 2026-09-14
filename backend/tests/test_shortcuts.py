from app import shortcuts as shortcuts_svc


def test_create_shortcut(db_session, user):
    sc = shortcuts_svc.create_or_update_shortcut(db_session, user.id, "my sign-off", "Warm regards,\nTest")
    assert sc.trigger_phrase == "my sign-off"
    assert sc.active == 1


def test_create_or_update_is_idempotent_on_same_trigger(db_session, user):
    shortcuts_svc.create_or_update_shortcut(db_session, user.id, "my sign-off", "First version")
    shortcuts_svc.create_or_update_shortcut(db_session, user.id, "my sign-off", "Second version")

    all_shortcuts = shortcuts_svc.list_shortcuts(db_session, user.id)
    assert len(all_shortcuts) == 1
    assert all_shortcuts[0].expansion_text == "Second version"


def test_delete_shortcut_marks_inactive_not_removed(db_session, user):
    sc = shortcuts_svc.create_or_update_shortcut(db_session, user.id, "my sign-off", "Text")
    ok = shortcuts_svc.delete_shortcut(db_session, user.id, sc.id)
    assert ok is True

    active = shortcuts_svc.list_shortcuts(db_session, user.id)
    assert len(active) == 0


def test_expand_shortcuts_applies_case_insensitive_match(db_session, user):
    shortcuts_svc.create_or_update_shortcut(db_session, user.id, "my sign-off", "Warm regards,\nTest")
    result, applied = shortcuts_svc.expand_shortcuts(db_session, user.id, "See you soon. MY SIGN-OFF")
    assert "Warm regards" in result
    assert len(applied) == 1


def test_expand_shortcuts_leaves_text_unchanged_when_no_trigger_present(db_session, user):
    shortcuts_svc.create_or_update_shortcut(db_session, user.id, "my sign-off", "Warm regards")
    result, applied = shortcuts_svc.expand_shortcuts(db_session, user.id, "Nothing relevant here")
    assert result == "Nothing relevant here"
    assert applied == []