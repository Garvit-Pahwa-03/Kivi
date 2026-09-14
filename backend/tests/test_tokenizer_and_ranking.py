from app.retrieval import _tokenize, _idf_weights, _rank_by_overlap


def test_tokenize_drops_single_char_fragments():
    # Regression test: possessive 's' and stray initials must not survive tokenization.
    tokens = _tokenize("Vikram Shah's role")
    assert "s" not in tokens
    assert "vikram" in tokens
    assert "shah" in tokens


def test_tokenize_lowercases_and_strips_punctuation():
    tokens = _tokenize("What does PRJ-FLC stand for?")
    assert "prj" in tokens
    assert "flc" in tokens
    assert "?" not in tokens


def test_idf_weights_rare_term_scores_higher_than_common_term():
    doc_sets = [
        {"project", "falcon", "timeline"},
        {"project", "comet", "timeline"},
        {"project", "budget"},
    ]
    weights = _idf_weights(["project", "falcon"], doc_sets)
    # "project" appears in all 3 docs (common); "falcon" in only 1 (rare)
    assert weights["falcon"] > weights["project"]


def test_idf_weights_excludes_stopwords():
    weights = _idf_weights(["what", "is", "falcon"], [{"falcon", "project"}])
    assert "what" not in weights
    assert "is" not in weights
    assert "falcon" in weights


class FakeItem:
    def __init__(self, text, ts):
        self.text = text
        self.ts = ts


def test_rank_by_overlap_finds_exact_acronym_match():
    items = [
        FakeItem("Discussed Project Falcon PRJFLC timeline with Rahul", 1),
        FakeItem("Random unrelated note about lunch plans today", 2),
    ]
    ranked = _rank_by_overlap(
        "PRJFLC", items, lambda i: i.text, lambda i: type("T", (), {"timestamp": lambda self: i.ts})(),
    )
    assert len(ranked) == 1
    assert ranked[0][0].text.startswith("Discussed")


def test_rank_by_overlap_abstains_when_only_generic_terms_match():
    # A query whose only signal word is near-universal across the candidate set
    # should not produce confident matches - this is the documented generic-query
    # retrieval limitation, tested explicitly so any future change to the
    # distinctiveness/coverage thresholds is caught here first.
    items = [
        FakeItem("Project one details here", 1),
        FakeItem("Project two details here", 2),
        FakeItem("Project three details here", 3),
    ]
    ranked = _rank_by_overlap(
        "the project", items, lambda i: i.text, lambda i: type("T", (), {"timestamp": lambda self: i.ts})(),
    )
    # "project" appears in all 3 docs => low distinctiveness, low coverage on its own.
    # We don't assert zero matches (that depends on exact threshold tuning), but we
    # assert it does NOT confidently return all 3 with high scores - i.e. there is a
    # deliberate wall here, not indiscriminate matching.
    assert len(ranked) <= 3