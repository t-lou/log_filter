import pytest

from buffer import Buffer


def test_init_positive_capacity():
    buf = Buffer(capacity=3, save_first=True)
    assert buf.capacity == 3
    assert buf.save_first is True


def test_init_invalid_capacity():
    with pytest.raises(ValueError):
        Buffer(capacity=0, save_first=True)

    with pytest.raises(ValueError):
        Buffer(capacity=-5, save_first=False)


# -----------------------------
# save_first = True (first N)
# -----------------------------


def test_save_first_collects_first_n():
    buf = Buffer(capacity=3, save_first=True)
    for i in range(10):
        buf.add(i)
    assert buf.get() == [0, 1, 2]  # only first 3 kept
    assert len(buf) == 3


def test_save_first_stops_accepting_after_full():
    buf = Buffer(capacity=2, save_first=True)
    buf.add("a")
    buf.add("b")
    buf.add("c")  # ignored
    assert buf.get() == ["a", "b"]


def test_save_first_exact_capacity():
    buf = Buffer(capacity=3, save_first=True)
    buf.add(1)
    buf.add(2)
    buf.add(3)
    assert buf.get() == [1, 2, 3]


# -----------------------------
# save_first = False (last N)
# -----------------------------


def test_save_last_collects_last_n():
    buf = Buffer(capacity=3, save_first=False)
    for i in range(10):
        buf.add(i)
    assert buf.get() == [7, 8, 9]  # last 3 items
    assert len(buf) == 3


def test_save_last_exact_capacity():
    buf = Buffer(capacity=3, save_first=False)
    buf.add("a")
    buf.add("b")
    buf.add("c")
    buf.add("x")
    buf.add("y")
    buf.add("z")
    assert buf.get() == ["x", "y", "z"]


def test_save_last_overflow_behavior():
    buf = Buffer(capacity=2, save_first=False)
    buf.add(1)
    buf.add(2)
    buf.add(3)  # 1 should be dropped
    assert buf.get() == [2, 3]


# -----------------------------
# repr
# -----------------------------


def test_repr_contains_key_info():
    buf = Buffer(capacity=2, save_first=True)
    buf.add(10)
    r = repr(buf)
    assert "capacity=2" in r
    assert "save_first=True" in r
    assert "10" in r
