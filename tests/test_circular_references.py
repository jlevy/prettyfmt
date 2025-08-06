from prettyfmt import abbrev_obj


def test_circular_dict():
    d = {"key": "value"}
    d["self"] = d  # pyright: ignore
    result = abbrev_obj(d)
    assert "<circular reference>" in result
    assert "key=value" in result


def test_circular_list():
    lst = ["item1", "item2"]
    lst.append(lst)  # pyright: ignore
    result = abbrev_obj(lst)
    assert "<circular reference>" in result
    assert "item1" in result
    assert "item2" in result


def test_mutual_reference():
    d1 = {"name": "dict1"}
    d2 = {"name": "dict2"}
    d1["other"] = d2  # pyright: ignore
    d2["other"] = d1  # pyright: ignore
    result = abbrev_obj(d1)
    assert "<circular reference>" in result
    assert "name=dict1" in result
    assert "name=dict2" in result


def test_nested_circular():
    d1 = {"level": 1}
    d2 = {"level": 2, "parent": d1}
    d3 = {"level": 3, "parent": d2}
    d1["child"] = d2  # pyright: ignore
    d2["child"] = d3  # pyright: ignore
    d3["root"] = d1  # pyright: ignore
    result = abbrev_obj(d1)
    assert "<circular reference>" in result
    assert "level=1" in result


def test_list_with_circular_dict():
    d1 = {"id": 1}
    d2 = {"id": 2}
    d1["ref"] = d2  # pyright: ignore
    d2["ref"] = d1  # pyright: ignore
    lst = [d1, d2]
    result = abbrev_obj(lst)
    assert "<circular reference>" in result
    assert "id=1" in result
    assert "id=2" in result


def test_deep_nesting_without_circular():
    d1 = {"level": 1}
    d2 = {"level": 2, "parent": d1}
    d3 = {"level": 3, "parent": d2}
    d4 = {"level": 4, "parent": d3}
    result = abbrev_obj(d4)
    assert "<circular reference>" not in result
    assert "level=4" in result
    assert "level=3" in result
    assert "level=2" in result
    assert "level=1" in result


def test_self_referencing_in_nested_structure():
    inner = {"name": "inner"}
    outer = {"name": "outer", "nested": inner}
    inner["parent"] = outer  # pyright: ignore
    result = abbrev_obj(outer)
    assert "<circular reference>" in result
    assert "name=outer" in result
    assert "name=inner" in result


def test_list_containing_self():
    lst = [1, 2, 3]
    container = {"items": lst, "self_list": None}
    container["self_list"] = container  # pyright: ignore
    result = abbrev_obj(container)
    assert "<circular reference>" in result
    assert "[1, 2, 3]" in result


def test_multiple_circular_references():
    d1 = {"id": "d1"}
    d2 = {"id": "d2"}
    d3 = {"id": "d3"}

    d1["refs"] = [d2, d3]  # pyright: ignore
    d2["refs"] = [d1, d3]  # pyright: ignore
    d3["refs"] = [d1, d2]  # pyright: ignore

    result = abbrev_obj(d1)
    assert "<circular reference>" in result
    assert "id=d1" in result
