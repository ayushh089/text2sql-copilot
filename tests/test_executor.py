import pytest

from src.database.executor import enforce_row_limit


@pytest.mark.parametrize("sql, expected", [
    ("SELECT a FROM t", "SELECT a FROM t LIMIT 1000"),
    ("SELECT a FROM t LIMIT 5", "SELECT a FROM t LIMIT 5"),
    ("SELECT a FROM t LIMIT 5000", "SELECT a FROM t LIMIT 1000"),
    ("SELECT a FROM t LIMIT 5000 OFFSET 10", "SELECT a FROM t LIMIT 1000 OFFSET 10"),
    ("SELECT a FROM t UNION SELECT a FROM t",
     "SELECT a FROM t UNION SELECT a FROM t LIMIT 1000"),
])
def test_enforce_row_limit(sql, expected):
    assert enforce_row_limit(sql, 1000) == expected


def test_invalid_max_rows():
    with pytest.raises(ValueError):
        enforce_row_limit("SELECT 1", 0)