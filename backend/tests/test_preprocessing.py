from app.preprocessing import clean_text, strip_boilerplate_headers


def test_stopwords_removed():
    cleaned = clean_text("This is a test of the system")
    assert "is" not in cleaned.split()
    assert "the" not in cleaned.split()


def test_lemmatisation():
    # WordNetLemmatizer defaults to noun mode (no POS tagging in this
    # pipeline), so plural nouns are reduced to their singular form.
    cleaned = clean_text("managing databases and systems")
    tokens = cleaned.split()
    assert "database" in tokens
    assert "system" in tokens


def test_boilerplate_headers_stripped():
    text = "Summary Highlights Experience Education Skills Python developer"
    result = strip_boilerplate_headers(text)
    for header in ["Summary", "Highlights", "Experience", "Education", "Skills"]:
        assert header not in result


def test_empty_text():
    assert clean_text("") == ""
    assert clean_text(None) == ""
