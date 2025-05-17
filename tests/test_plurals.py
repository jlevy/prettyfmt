from prettyfmt.plurals import fmt_count_items, plural


def test_plural():
    assert plural("banana", 2) == "bananas"
    assert plural("banana", 1) == "banana"
    assert plural("banana", 0) == "bananas"
    assert plural("banana", None) == "bananas"
    assert plural("child", 2) == "children"
    assert plural("person", 2) == "people"
    assert plural("fish", 2) == "fish"
    assert plural("", 2) == ""


def test_fmt_count_items():
    assert fmt_count_items(2, "banana") == "2 bananas"
    assert fmt_count_items(1, "banana") == "1 banana"
    assert fmt_count_items(0, "banana") == "0 bananas"
    assert fmt_count_items(2, "") == "2"
