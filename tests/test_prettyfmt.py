from prettyfmt import (
    abbrev_on_words,
    abbrev_phrase_in_middle,
    fmt_words,
    sanitize_title,
)


def test_abbreviate_on_words():
    assert abbrev_on_words("Hello, World!", 5) == "Hell…"
    assert abbrev_on_words("Hello, World!", 6) == "Hello…"
    assert abbrev_on_words("Hello, World!", 13) == "Hello, World!"
    assert abbrev_on_words("Hello, World!", 12) == "Hello…"
    assert abbrev_on_words("", 2) == ""
    assert abbrev_on_words("Hello, World!", 0) == "…"
    assert abbrev_on_words("", 5) == ""
    assert (
        abbrev_on_words("Supercalifragilisticexpialidocious is a long word", 20)
        == "Supercalifragilisti…"
    )


def test_abbreviate_phrase_in_middle():
    assert abbrev_phrase_in_middle("Hello, World! This is a test.", 16) == "Hello, … a test."
    assert (
        abbrev_phrase_in_middle("Hello, World! This is a test.", 23) == "Hello, … This is a test."
    )
    assert (
        abbrev_phrase_in_middle("Hello, World! This is a test.", 27) == "Hello, … This is a test."
    )
    assert (
        abbrev_phrase_in_middle("Hello, World! This is a test.", 40)
        == "Hello, World! This is a test."
    )
    assert abbrev_phrase_in_middle("Hello, World! This is a test.", 10) == "Hello, …"
    assert (
        abbrev_phrase_in_middle("Supercalifragilisticexpialidocious is a long word", 24)
        == "Supercalifragilisticexp… …"
    )

    assert (
        abbrev_phrase_in_middle(
            "Your Mindset Matters (transcription) (clean text) (in paragraphs) (with timestamps) (add_description)",
            64,
        )
        == "Your Mindset Matters (transcription) (clean … (add_description)"
    )


def test_fmt_words():
    # Basic cases.
    assert fmt_words("Hello", "world!") == "Hello world!"
    assert fmt_words("Hello ", "world!") == "Hello world!"
    assert fmt_words("Hello", " world!") == "Hello world!"
    assert fmt_words("Hello", None, "world!") == "Hello world!"
    assert fmt_words("Hello", "", "world!") == "Hello world!"
    # More complex cases.
    assert fmt_words("\nHello\n", "world!\n") == "\nHello\n world!\n"
    assert fmt_words("Hello", " ", "world!") == "Hello world!"
    assert fmt_words("Hello", " John and", "world!") == "Hello John and world!"
    assert fmt_words("Hello", " ", "world!", sep="|") == "Hello| |world!"
    assert fmt_words("Hello", "John", "world!", sep=", ") == "Hello, John, world!"
    # Edge cases.
    assert fmt_words() == ""
    assert fmt_words(None, "x", "   ") == "x"
    assert fmt_words("   ") == "   "
    assert fmt_words("Hello\t", "World", sep=" ") == "Hello\t World"
    assert fmt_words("Hello", "\nWorld", sep=" ") == "Hello \nWorld"
    assert fmt_words("Hello", "   ", "World", sep="---") == "Hello---   ---World"
    assert fmt_words("Hello", "World", sep=" | ") == "Hello | World"
    assert fmt_words(" Hello ", " ", " World ") == " Hello World "


def test_sanitize_title():
    assert sanitize_title("Hello, World!") == "Hello, World!"
    assert sanitize_title("Hej, Världen!") == "Hej, Världen!"
    assert sanitize_title("你好 世界") == "你好 世界"
    assert sanitize_title("こんにちは、世界") == "こんにちは 世界"
    assert sanitize_title(" *Hello,*  \n\tWorld!  --123@:': ") == "Hello, World! --123@:':"
    assert sanitize_title("<script foo='blah'><p>") == "script foo 'blah' p"
