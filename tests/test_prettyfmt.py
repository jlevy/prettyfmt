from dataclasses import dataclass
from pathlib import Path

from prettyfmt import (
    abbrev_obj,
    abbrev_on_words,
    abbrev_phrase_in_middle,
    day,
    fmt_age,
    fmt_words,
    hour,
    minute,
    month,
    sanitize_title,
    year,
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


def test_fmt_words() -> None:
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


def test_fmt_age() -> None:
    assert fmt_age(1) == "1 second ago"
    assert fmt_age(10) == "10 seconds ago"
    assert fmt_age(100) == "2 minutes ago"
    assert fmt_age(1000) == "17 minutes ago"
    assert fmt_age(10000) == "3 hours ago"
    assert fmt_age(100000) == "28 hours ago"
    assert fmt_age(1000000) == "12 days ago"
    assert fmt_age(10000000) == "4 months ago"
    assert fmt_age(100000000) == "3 years ago"
    assert fmt_age(1000000000) == "32 years ago"

    assert fmt_age(1, brief=True) == "1s ago"
    assert fmt_age(10, brief=True) == "10s ago"
    assert fmt_age(100, brief=True) == "2m ago"
    assert fmt_age(1000, brief=True) == "17m ago"
    assert fmt_age(10000, brief=True) == "3h ago"
    assert fmt_age(100000, brief=True) == "28h ago"
    assert fmt_age(1000000, brief=True) == "12d ago"
    assert fmt_age(10000000, brief=True) == "4mo ago"
    assert fmt_age(100000000, brief=True) == "3y ago"
    assert fmt_age(1000000000, brief=True) == "32y ago"

    assert fmt_age(1 * minute, brief=True) == "60s ago"
    assert fmt_age(2 * minute, brief=True) == "2m ago"
    assert fmt_age(1 * hour, brief=True) == "60m ago"
    assert fmt_age(90 * minute, brief=True) == "90m ago"
    assert fmt_age(26 * hour, brief=True) == "26h ago"
    assert fmt_age(2 * day, brief=True) == "2d ago"
    assert fmt_age(45 * day, brief=True) == "45d ago"
    assert fmt_age(2 * month, brief=True) == "2mo ago"
    assert fmt_age(2 * year, brief=True) == "2y ago"


def test_sanitize_title() -> None:
    assert sanitize_title("Hello, World!") == "Hello, World!"
    assert sanitize_title("Hej, Världen!") == "Hej, Världen!"
    assert sanitize_title("你好 世界") == "你好 世界"
    assert sanitize_title("こんにちは、世界") == "こんにちは 世界"
    assert sanitize_title(" *Hello,*  \n\tWorld!  --123@:': ") == "Hello, World! --123@:':"
    assert sanitize_title("<script foo='blah'><p>") == "script foo 'blah' p"


def test_dataclass() -> None:
    @dataclass
    class MyThing:
        file_path: Path
        title: str
        url: str
        body: str

        def __str__(self) -> str:
            return abbrev_obj(
                self,
                # Put an abbreviated title first, then the file path, then the url.
                key_filter={
                    "title": 64,
                    "file_path": 10,
                    "url": 128,
                },
            )

    s = str(
        MyThing(
            Path("~/1234567890/abc"),
            "Hello, World!",
            "https://example.com",
            "This should be skipped.",
        )
    )
    expected = "MyThing(title='Hello, World!', file_path='~/1234567…', url=https://example.com)"
    assert s == expected
