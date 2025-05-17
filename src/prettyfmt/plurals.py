from functools import cache


@cache
def get_pluralizer():
    """
    Faster lazy import for pluralizer.
    `pluralizer` is just a few hundred lines of code and fine for common English usage.
    In contrast, packages like `inflect` are much larger and take over 1s to import.
    """

    from pluralizer import Pluralizer

    return Pluralizer()


def plural(word: str, count: int | None = None) -> str:
    """
    Pluralize or singularize a word based on the count.
    """
    return get_pluralizer().pluralize(word, count=count)  # pyright: ignore


def fmt_count_items(count: int, name: str | None = "item") -> str:
    """
    Format a count and a name as a pluralized phrase, e.g. "1 item" or "2 items".
    If name is empty or whitespace, just return the count.
    """
    if not name or not name.strip():
        return str(count)
    return f"{count} {plural(name, count)}"  # pyright: ignore
