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
