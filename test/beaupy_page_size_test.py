import numbers
import pytest
from yakh.key import Keys

from beaupy import _beaupy as b
from beaupy._beaupy import select, select_multiple


@pytest.fixture(autouse=True)
def stub_keypress(monkeypatch):
    """Never block on real keypresses: answer ENTER if a prompt is displayed."""
    monkeypatch.setattr(b, "get_key", lambda: Keys.ENTER)


@pytest.mark.parametrize("page_size", [0, -1, -100])
def test_select_with_non_positive_page_size_raises_value_error(page_size):
    with pytest.raises(ValueError) as e:
        select(options=["a", "b"], page_size=page_size)
    assert "`page_size` must be a positive integer" in str(e.value)


@pytest.mark.parametrize("page_size", [0, -1, -100])
def test_select_multiple_with_non_positive_page_size_raises_value_error(page_size):
    with pytest.raises(ValueError) as e:
        select_multiple(options=["a", "b"], page_size=page_size)
    assert "`page_size` must be a positive integer" in str(e.value)


def test_select_with_non_integer_page_size_raises_value_error():
    with pytest.raises(ValueError) as e:
        select(options=["a", "b"], page_size="3")
    assert "`page_size` must be a positive integer" in str(e.value)


def test_integral_page_size_is_accepted():
    class IntLike(numbers.Integral):  # stands in for numpy integers
        def __init__(self, v):
            self.v = v

        def __int__(self):
            return self.v

        def __lt__(self, other):
            return self.v < other

        def __getattr__(self, name):  # remaining abstract methods are never used here
            raise NotImplementedError(name)

    IntLike.__abstractmethods__ = frozenset()
    b._validate_page_size(IntLike(3))


def test_bool_page_size_raises_value_error():
    with pytest.raises(ValueError):
        b._validate_page_size(True)
