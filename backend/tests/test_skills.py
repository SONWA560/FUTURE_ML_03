import json

import pytest

from app.skills import SkillExtractor


@pytest.fixture(scope="module")
def extractor(tmp_path_factory):
    taxonomy = [
        {"skill": "Python", "aliases": ["python3"], "category": "programming"},
        {"skill": "JavaScript", "aliases": ["js"], "category": "programming"},
        {"skill": "R", "aliases": [], "category": "programming"},
        {"skill": "Machine Learning", "aliases": [], "category": "programming"},
        {"skill": "Customer Relationship Management", "aliases": ["crm"], "category": "business"},
    ]
    path = tmp_path_factory.mktemp("data") / "taxonomy.json"
    path.write_text(json.dumps(taxonomy))
    return SkillExtractor(path)


def test_exact_match(extractor):
    assert "Python" in extractor.extract("Experienced Python developer")


def test_alias_normalisation(extractor):
    assert "JavaScript" in extractor.extract("Built features using JS")


def test_case_insensitivity(extractor):
    for text in ["PYTHON", "python", "Python"]:
        assert "Python" in extractor.extract(f"Skilled in {text}")


def test_no_false_positive_substring_match(extractor):
    # "R" must not match inside "car" or "for" due to token-boundary matching
    skills = extractor.extract("I drove a car and worked for a great team")
    assert "R" not in skills


def test_multiword_phrase_matched_as_one_skill(extractor):
    skills = extractor.extract("Strong background in machine learning and CRM tools")
    assert "Machine Learning" in skills
    assert "Customer Relationship Management" in skills


def test_empty_text_returns_empty_list(extractor):
    assert extractor.extract("") == []


def test_duplicate_mentions_deduplicated(extractor):
    skills = extractor.extract("Python, Python, and more Python")
    assert skills.count("Python") == 1
