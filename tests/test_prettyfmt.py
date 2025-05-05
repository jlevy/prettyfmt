from dataclasses import dataclass
from pathlib import Path

from prettyfmt import (
    abbrev_obj,
    abbrev_on_words,
    abbrev_phrase_in_middle,
    day,
    fmt_age,
    fmt_path,
    fmt_words,
    hour,
    minute,
    month,
    sanitize_str,
    sanitize_title,
    slugify_kebab,
    slugify_snake,
    unicode_to_ascii,
    year,
)
from prettyfmt.prettyfmt import fmt_timedelta


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


def test_fmt_timedelta() -> None:
    assert fmt_timedelta(0.001, brief=False) == "1 millisecond"
    assert fmt_timedelta(0.01, brief=False) == "10 milliseconds"
    assert fmt_timedelta(0.1, brief=False) == "100 milliseconds"
    assert fmt_timedelta(0.002, brief=False) == "2 milliseconds"
    assert fmt_timedelta(0.0021111) == "2.11ms"
    assert fmt_timedelta(0.0021111, sub_seconds=False) == "0s"
    assert fmt_timedelta(0.0456) == "45.60ms"
    assert fmt_timedelta(0.12345) == "123ms"
    assert fmt_timedelta(55.55555) == "56s"
    assert fmt_timedelta(55.55555, sub_seconds=False) == "56s"
    assert fmt_timedelta(3333333) == "39d"


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

        def __str__(self) -> str:  # pyright: ignore[reportImplicitOverride]
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


def test_fmt_path() -> None:
    # Basic case - no spaces in path
    assert fmt_path("path.txt", resolve=False) == "path.txt"

    # Path with spaces
    assert fmt_path("my long path.txt", resolve=False) == "'my long path.txt'"

    # Test with resolve=False
    assert fmt_path("/some/path/file.txt", resolve=False) == "/some/path/file.txt"

    # Get actual cwd and home directory
    cwd = Path.cwd()
    home = Path.home()

    # Test absolute path gets quoted properly
    abs_path_with_spaces = Path("/tmp/my test file.txt")
    assert fmt_path(abs_path_with_spaces, resolve=False) == "'/tmp/my test file.txt'"

    # Test rel_to_cwd parameter
    # Create a path that's within the current directory
    rel_file = "test_file.txt"
    abs_file = cwd / rel_file

    # When rel_to_cwd is True, should show as relative
    assert fmt_path(abs_file, rel_to_cwd=True, use_tilde=False) == rel_file

    # When rel_to_cwd is False and use_tilde=False, should show as absolute
    absolute_path = fmt_path(abs_file, rel_to_cwd=False, use_tilde=False)
    assert rel_file in absolute_path
    assert absolute_path.startswith("/")  # Should be absolute path

    # Test use_tilde parameter
    # Create a path within the home directory
    home_rel_path = "Documents/test_file.txt"
    home_abs_path = home / home_rel_path

    # When use_tilde is True, should use ~
    tilde_path = fmt_path(home_abs_path, use_tilde=True, rel_to_cwd=False)
    assert tilde_path.startswith("~/")
    assert home_rel_path in tilde_path

    # When use_tilde is False, should show as absolute
    home_path_str = fmt_path(home_abs_path, use_tilde=False, rel_to_cwd=False)
    assert home_path_str.startswith("/")
    assert not home_path_str.startswith("~")
    assert str(home.name) in home_path_str

    # Test path with spaces in home directory
    home_path_spaces = home / "Documents/my test file.txt"
    tilde_path = fmt_path(home_path_spaces, use_tilde=True, rel_to_cwd=False)
    assert "~/Documents/my test file.txt" in tilde_path

    # Test priority - rel_to_cwd should take precedence over use_tilde
    # First, make sure we're testing a path within the current directory
    test_in_cwd = cwd / "priority_test_cwd.txt"

    # rel_to_cwd=True should override use_tilde=True
    rel_path = fmt_path(test_in_cwd, rel_to_cwd=True, use_tilde=True)
    assert rel_path == "priority_test_cwd.txt"

    # If the current directory happens to be inside the home directory, we can do additional tests
    if str(cwd).startswith(str(home)):
        # CWD is within home directory
        test_in_home = cwd / "priority_test_home.txt"

        # When rel_to_cwd=False, use_tilde=True, should use tilde notation
        home_tilde_path = fmt_path(test_in_home, rel_to_cwd=False, use_tilde=True)
        assert home_tilde_path.startswith("~/")

        # When both flags are False, should be absolute path
        abs_path = fmt_path(test_in_home, rel_to_cwd=False, use_tilde=False)
        assert abs_path.startswith("/")
        assert not abs_path.startswith("~")


def test_sanitize_str():
    assert sanitize_str("Hello, World!") == "Hello World"
    assert sanitize_str("test@example.com") == "test example com"
    assert sanitize_str("  spaces  ") == "spaces"
    assert sanitize_str("über café") == "über café"
    assert sanitize_str("你好世界") == "你好世界"
    assert sanitize_str("$#@!%^&*()") == ""
    assert sanitize_str("mixed_-symbols&&chars") == "mixed symbols chars"
    assert sanitize_str("mixed___symbols---chars--") == "mixed symbols chars"
    assert sanitize_str("under_score_names") == "under score names"
    assert sanitize_str("under_score_names", space_replacement="-") == "under-score-names"
    assert sanitize_str("under_score_names", space_replacement="") == "underscorenames"
    assert sanitize_str("under_score_names", allowed_chars="_") == "under_score_names"


def test_slugify_snake():
    assert slugify_snake("Hello World!") == "hello_world"
    assert slugify_snake("Test-Case") == "test_case"
    assert slugify_snake("  Multiple   Spaces  ") == "multiple_spaces"
    assert slugify_snake("über café") == "über_café"
    assert slugify_snake("你好世界") == "你好世界"
    assert slugify_snake("email@domain.com") == "email_domain_com"
    assert slugify_snake("$price = 99.99") == "price_99_99"
    assert (
        slugify_snake("Topics in I//O and  Audio Streams: A Technical Overview   (with examples)")
        == "topics_in_i_o_and_audio_streams_a_technical_overview_with_examples"
    )
    assert (
        slugify_snake("~/Downloads/Post-Quantum Cryptography_ In-Depth Overview_.docx")
        == "downloads_post_quantum_cryptography_in_depth_overview_docx"
    )


def test_slugify_kebab():
    assert slugify_kebab("Hello World!") == "hello-world"
    assert slugify_kebab("Test_Case") == "test-case"
    assert slugify_kebab("  Multiple   Spaces  ") == "multiple-spaces"
    assert slugify_kebab("über café") == "über-café"
    assert slugify_kebab("你好世界") == "你好世界"
    assert slugify_kebab("email@domain.com") == "email-domain-com"
    assert slugify_kebab("$price = 99.99") == "price-99-99"


def test_unicode_to_ascii():
    assert unicode_to_ascii("Héllø") == "Hello"
    assert unicode_to_ascii("你好世界") == "Ni Hao Shi Jie "
    assert unicode_to_ascii("Σὲ γνωρίζω") == "Se gnorizo"

    assert unicode_to_ascii("über café") == "uber cafe"
    assert unicode_to_ascii("Crème Brûlée") == "Creme Brulee"
    assert unicode_to_ascii("Erdős-Rényi") == "Erdos-Renyi"
    assert unicode_to_ascii("ąćęłńóśźż ĄĆĘŁŃÓŚŹŻ") == "acelnoszz ACELNOSZZ"


def test_slugify_snake_with_ascii():
    # Test existing behavior is preserved
    assert slugify_snake("Hello World!") == "hello_world"
    assert slugify_snake("Test-Case") == "test_case"
    assert slugify_snake("  Multiple   Spaces  ") == "multiple_spaces"

    # Test unicode handling with ascii=False (default)
    assert slugify_snake("über café") == "über_café"
    assert slugify_snake("你好世界") == "你好世界"

    # Test with ascii=True
    assert slugify_snake("über café", ascii=True) == "uber_cafe"
    assert slugify_snake("你好世界", ascii=True) == "ni_hao_shi_jie"
    assert slugify_snake("Crème Brûlée", ascii=True) == "creme_brulee"
    assert slugify_snake("Hello World!", ascii=True) == "hello_world"
    assert slugify_snake("Test-Case", ascii=True) == "test_case"


def test_slugify_kebab_with_ascii():
    # Test existing behavior is preserved
    assert slugify_kebab("Hello World!") == "hello-world"
    assert slugify_kebab("Test_Case") == "test-case"
    assert slugify_kebab("  Multiple   Spaces  ") == "multiple-spaces"

    # Test unicode handling with ascii=False (default)
    assert slugify_kebab("über café") == "über-café"
    assert slugify_kebab("你好世界") == "你好世界"

    # Test with ascii=True
    assert slugify_kebab("über café", ascii=True) == "uber-cafe"
    assert slugify_kebab("你好世界", ascii=True) == "ni-hao-shi-jie"
    assert slugify_kebab("Crème Brûlée", ascii=True) == "creme-brulee"
    assert slugify_kebab("Hello World!", ascii=True) == "hello-world"
    assert slugify_kebab("Test_Case", ascii=True) == "test-case"


def test_readme_examples():
    # Test the examples from the README
    ugly_title = (
        "A  Very\tVery Very Needlessly Long  {Strange} Document Title [final edited draft23]"
    )
    sanitized = sanitize_title(ugly_title)
    assert (
        sanitized == "A Very Very Very Needlessly Long Strange Document Title final edited draft23"
    )

    abbreviated = abbrev_phrase_in_middle(sanitize_title(ugly_title))
    assert abbreviated == "A Very Very Very Needlessly Long Strange … final edited draft23"

    # Test the slugified version with our new functions
    snake_slug = slugify_snake(abbreviated, ascii=True)
    assert snake_slug == "a_very_very_very_needlessly_long_strange_final_edited_draft23"

    kebab_slug = slugify_kebab(abbreviated, ascii=True)
    assert kebab_slug == "a-very-very-very-needlessly-long-strange-final-edited-draft23"
