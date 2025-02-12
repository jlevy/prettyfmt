import re
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from textwrap import indent
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, TypeVar

from humanize import naturalsize, precisedelta

from strif import abbrev_str, quote_if_needed


def is_not_none(value: Any) -> bool:
    """Not none value filter."""
    return value is not None


KeyFilter = Callable[[Any], int | None] | Dict[Any, int | None]
"""
A dict or callable that returns the max allowed length of each key,
or 0 to allow any length, or None to omit the key. The dict form of
a key filter can also implicitly indicate a sorting order for the keys.
"""


T = TypeVar("T")


def custom_key_sort(priority_keys: List[T]) -> Callable[[T], Any]:
    """
    Custom sort function that prioritizes the specific keys in a certain order,
    followed by all the other keys in natural order.
    """

    def sort_func(key: T) -> Tuple[float, T]:
        try:
            i = priority_keys.index(key)
            return (float(i), key)
        except ValueError:
            return (float("inf"), key)

    return sort_func


minute = 60
hour = 3600
day = 86400
month = 86400 * 30
year = 86400 * 365


def _format_kvs(
    items: Iterable[Tuple[Any, Any]],
    field_max_len: int,
    key_filter: Optional[KeyFilter] = None,
    value_filter: Optional[Callable[[Any], bool]] = None,
) -> str:
    filtered_items: List[Tuple[Any, Any]] = []
    for k, v in items:
        if key_filter is not None:
            if callable(key_filter):
                max_len = key_filter(k)
            else:
                max_len = key_filter.get(k, None)
            if max_len is None:
                continue
            field_max_len = max_len
        if not value_filter or value_filter(v):
            filtered_items.append(
                (
                    k,
                    abbrev_obj(
                        v,
                        field_max_len,
                        key_filter=key_filter,
                        value_filter=value_filter,
                    ),
                )
            )

    # Sort the filtered items to match key_filter, if it is a dict.
    if isinstance(key_filter, dict):
        prioritize_keys = custom_key_sort(list(key_filter.keys()))
        filtered_items.sort(key=lambda x: prioritize_keys(x[0]))

    return ", ".join(f"{k}={v}" for k, v in filtered_items)


def abbrev_obj(
    value: Any,
    field_max_len: int = 64,
    list_max_len: int = 32,
    key_filter: Optional[KeyFilter] = None,
    value_filter: Optional[Callable[[Any], bool]] = is_not_none,
    visited: Optional[Set[Any]] = None,
) -> str:
    """
    Helper to print an abbreviated string version of an object, with options to
    omit specific fields and truncate long strings or lists, adding an ellipsis
    when truncated.

    Truncation length can be set per field with the `key_filter` parameter.
    Also offers control over the ordering of the fields in the output, by
    using a dict for the `key_filter`.

    Not a parsable format. Useful for abbreviating dicts or for __str__() on
    dataclasses. By default the `value_filter` omits None values, and
    omit quotes when possible.

    Example usage:
    ```
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
                    "file_path": 0,
                    "url": 128,
                },
            )
    ```
    """
    if visited is None:
        visited = set()
    if id(value) in visited:
        return "<circular reference>"
    visited.add(id(value))

    if isinstance(value, list):
        truncated_list = value[:list_max_len] + (
            ["…"] if len(value) > list_max_len else []
        )
        return (
            "["
            + ", ".join(
                abbrev_obj(
                    item, field_max_len, list_max_len, key_filter, value_filter, visited
                )
                for item in truncated_list
            )
            + "]"
        )

    if is_dataclass(value) and not isinstance(value, type):
        name = type(value).__name__
        value_dict = asdict(value)
        return (
            f"{name}("
            + _format_kvs(value_dict.items(), field_max_len, key_filter, value_filter)
            + ")"
        )

    if isinstance(value, dict):
        return (
            "{"
            + _format_kvs(value.items(), field_max_len, key_filter, value_filter)
            + "}"
        )

    if isinstance(value, Enum):
        return value.name

    return quote_if_needed(abbrev_str(str(value), field_max_len))


def _trim_trailing_punctuation(text: str) -> str:
    return re.sub(r"[.,;:!?]+$", "", text)


def abbrev_on_words(text: str, max_len: int = 64, indicator: str = "…") -> str:
    """
    Abbreviate text to a maximum character length, breaking on whole words
    (unless the first word is too long). For aesthetics, removes trailing
    punctuation from the last word.
    """
    if len(text) <= max_len:
        return text
    words = text.split()

    if words and max_len and len(words[0]) > max_len:
        return abbrev_str(words[0], max_len, indicator)

    while (
        words
        and len(_trim_trailing_punctuation(" ".join(words))) + len(indicator) > max_len
    ):
        words.pop()

    return _trim_trailing_punctuation(" ".join(words)) + indicator


def abbrev_phrase_in_middle(
    phrase: str, max_len: int = 64, ellipsis="…", max_trailing_len: int = 0
) -> str:
    """
    Abbreviate a phrase to a maximum character length, preserving the first and last
    few words of the phrase whenever possible. The ellipsis is inserted in the middle
    of the phrase.
    """
    if not max_trailing_len:
        max_trailing_len = min(int(max_len / 2), max(16, int(max_len / 4)))

    phrase = " ".join(phrase.split())

    if len(phrase) <= max_len:
        return phrase

    if max_len <= len(ellipsis):
        return ellipsis

    words = phrase.split()
    prefix_tally = 0
    prefix_end_index = 0

    # Walk through the split words, and tally total number of chars as we go.
    for i in range(len(words)):
        words[i] = abbrev_str(words[i], max_len, ellipsis)
        if (
            prefix_tally + len(words[i]) + len(ellipsis) + max_trailing_len >= max_len
            and i > 0
        ):
            prefix_end_index = i
            break
        prefix_tally += len(words[i]) + 1

    prefix_end_index = max(1, prefix_end_index)

    # Calculate the start index for the trailing part.
    suffix_start_index = len(words) - 1
    suffix_tally = 0
    for i in range(len(words) - 1, prefix_end_index - 1, -1):
        if suffix_tally + len(words[i]) + len(ellipsis) + prefix_tally > max_len:
            suffix_start_index = i + 1
            break
        suffix_tally += len(words[i]) + 1

    # Replace the middle part with ellipsis.
    words = words[:prefix_end_index] + [ellipsis] + words[suffix_start_index:]

    result = " ".join(word for word in words if word)

    return result


## Some generic formatters that can safely be used for any paths, phrases, timestamps, etc.


def fmt_age(since_time: float | timedelta, brief: bool = False) -> str:
    """
    Format a time delta as a simple age with a single unit, e.g. "2d ago" (brief)
    or "2 days ago" (not brief).

    Unlike `humanize.naturaldelta()`, we use only a single unit (seconds, minutes, hours,
    days, months, years). We don't use decimals. Conform with typical human usage, and
    say "33 days" instead of "1 month and 3 days", i.e. use seconds for less than 90 seconds,
    minutes for less than 90 minutes, hours for less than 2 days, days for less than 2 months,
    months for less than 2 years.
    """
    if isinstance(since_time, timedelta):
        seconds = int(since_time.total_seconds())
    else:
        seconds = int(since_time)

    if seconds <= 90:
        suppress = ["minutes"]
        min_unit = "seconds"
    elif seconds <= 90 * minute:
        suppress = ["hours"]
        min_unit = "minutes"
    elif seconds < 2 * day:
        suppress = ["days"]
        min_unit = "hours"
    elif seconds < 2 * month:
        suppress = ["months"]
        min_unit = "days"
    elif seconds < 2 * year:
        suppress = ["years"]
        min_unit = "months"
    else:
        suppress = []
        min_unit = "years"

    age = precisedelta(
        seconds, minimum_unit=min_unit, suppress=suppress, format="%0.0f"
    )
    if brief:
        age = (
            age.replace(" seconds", "s")
            .replace(" second", "s")
            .replace(" minutes", "m")
            .replace(" minute", "m")
            .replace(" hours", "h")
            .replace(" hour", "h")
            .replace(" days", "d")
            .replace(" day", "d")
            .replace(" weeks", "w")
            .replace(" week", "w")
            .replace(" months", "mo")
            .replace(" month", "mo")
            .replace(" years", "y")
            .replace(" year", "y")
            .replace("a ", "1")  # Convert "a minute" to "1m" etc.
            .replace(".0", "")  # Remove trailing ".0" (corner case bug in humanize)
        )

    return age + " ago"


def fmt_time(
    dt: datetime,
    iso_time: bool = True,
    friendly: bool = False,
    brief: bool = False,
    now: Optional[datetime] = None,
) -> str:
    """
    Format a datetime for display in various formats:
    - ISO timestamp (e.g. "2024-03-15T17:23:45Z")
    - Age (e.g. "2d ago")
    - Friendly format (e.g. "March 15, 2024 17:23 UTC")
    """
    if friendly:
        # Format timezone name, handling UTC specially
        tzname = dt.tzname() or "UTC" if dt.tzinfo else "UTC"
        return dt.strftime("%B %d, %Y %H:%M ") + tzname
    if iso_time:
        return dt.isoformat().split(".", 1)[0] + "Z"
    else:
        if not now:
            now = datetime.now(timezone.utc)
        return fmt_age(now.timestamp() - dt.timestamp(), brief=brief)


def fmt_size_human(size: int) -> str:
    """
    Format a size (typically a file size) in bytes as a human-readable string,
    e.g. "1.2MB".
    """
    # gnu is briefer, uses B instead of Bytes.
    return naturalsize(size, gnu=True)


def fmt_size_dual(size: int, human_min: int = 10000) -> str:
    """
    Format a size in bytes in both human-readable and exact formats, e.g.
    "1.2MB (1200000 bytes)". The human-readable format is included if the size is
    at least `human_min`.
    """
    if size >= human_min:
        return f"{fmt_size_human(size)} ({size} bytes)"
    else:
        return f"{size} bytes"


def fmt_words(*words: str | None, sep: str = " ") -> str:
    """
    Format a list of words or phrases into a single string, with no leading or trailing
    whitespace. Empty or None values are ignored. Other whitespace including \n and \t are
    preserved. Spaces are trimmed only when they would yield a double space due to
    a separator.

    Example usage:
    ```
    fmt_words("Hello", "world!") == "Hello world!"
    fmt_words("Hello ", "world!") == "Hello world!"
    fmt_words("Hello", " world!") == "Hello world!"
    fmt_words("Hello", None, "world!") == "Hello world!"
    fmt_words("Hello", "", "world!") == "Hello world!"
    fmt_words("Hello", " ", "world!") == "Hello world!"
    fmt_words("\nHello\n", "world!\n") == "\nHello\n world!\n"
    fmt_words("Hello", " ", "world!", sep="|") == "Hello| |world!"
    fmt_words("Hello", "John ", "world!", sep=", ") == "Hello, John, world!"
    ```
    """
    # Filter out Nones and empty strings.
    word_list = [word for word in words if word]

    if not word_list:
        return ""

    processed_words = []

    sep_starts_with_space = sep.startswith(" ")
    sep_ends_with_space = sep.endswith(" ")

    for i, word in enumerate(word_list):
        # Avoid double spaces caused by the separator.
        if i > 0 and sep_ends_with_space:
            word = word.lstrip(" ")
        if i < len(word_list) - 1 and sep_starts_with_space:
            word = word.rstrip(" ")
        # If word is now empty, we can skip it.
        if not word:
            continue

        processed_words.append(word)

    return sep.join(processed_words)


def fmt_paras(*paras: str | None, sep: str = "\n\n") -> str:
    """
    Format text as a list of paragraphs, omitting None or empty paragraphs.
    """
    filtered_paras = [para.strip() for para in paras if para is not None]
    return sep.join(para for para in filtered_paras if para)


def fmt_lines(
    values: Iterable[Any], prefix: str = "    ", line_break: str = "\n", max: int = 0
) -> str:
    """
    Simple of values one per line, optionally prefixed or indented. If `max` is set,
    cap at that number of items and indicate how many more were omitted.
    """
    values = list(values)
    if max > 0 and max < len(values):
        remaining = len(values) - max
        values = values[:max]
        values.append(f"… ({remaining} more items)")
    return indent(line_break.join(str(value) for value in values), prefix).rstrip()


def fmt_path(path: str | Path, resolve: bool = True) -> str:
    """
    Format a path or filename for display. This quotes it if it contains whitespace,
    using Python conventions: `my long path.txt` is formatted as `'my long path.txt'`.

    :param resolve: If true paths are resolved. If they are within the current working
    directory, they are formatted as relative. Otherwise, they are formatted as absolute.
    """

    # TODO: Add a max_len parameter and tools to abbreviate the path in the middle
    # (preserving outer quotes and any extension).

    if resolve:
        path = Path(path).resolve()
        cwd = Path.cwd().resolve()
        if path.is_relative_to(cwd):
            path = path.relative_to(cwd)
    else:
        path = Path(path)

    return quote_if_needed(str(path))


DEFAULT_PUNCTUATION = ",./:;'!?/@%&()+" "''…–—-"


def sanitize_title(text: str, allowed_chars: str = DEFAULT_PUNCTUATION) -> str:
    """
    Simple sanitization for arbitrary text to make it suitable for a title or filename.
    Convert all whitespace to spaces. By default allows the most common punctuation,
    letters, and numbers, but not Markdown chars like `*` or `[]`, code characters, etc.
    """
    # Note \w and \d should now be pretty good for common Unicode letters and digits.
    # If we had the regex package on hand we could use \p{L}\p{N} instead of \w\d
    # but probably not worth the import.
    escaped_chars = re.escape(allowed_chars)
    return re.sub(r"[^\w\d" + escaped_chars + "]+", " ", text).strip()
