import os
import pytest
from core.parser import parse_file, _is_numeric, _infer_fk_from_columns

SAMPLE_XLS  = os.environ.get("SAMPLE_XLS", "")
SAMPLE_XLSX = os.environ.get("SAMPLE_XLSX", "")


def test_is_numeric():
    assert _is_numeric(1) is True
    assert _is_numeric("3") is True
    assert _is_numeric(1.5) is True
    assert _is_numeric("") is False
    assert _is_numeric(None) is False
    assert _is_numeric("abc") is False


def test_infer_fk_suffixes():
    columns = [
        {"name": "PLANT_CD", "pk": False},
        {"name": "USER_ID",  "pk": False},
        {"name": "CODE_DVN", "pk": True},
        {"name": "REMARK",   "pk": False},
    ]
    result = _infer_fk_from_columns(columns)
    names = [r["column"] for r in result]
    assert "PLANT_CD" in names
    assert "USER_ID" in names
    assert "CODE_DVN" not in names
    assert "REMARK" not in names


def test_unsupported_extension(tmp_path):
    f = tmp_path / "test.csv"
    f.write_text("dummy")
    with pytest.raises(ValueError, match="지원하지 않는 파일 형식"):
        parse_file(str(f))


def _assert_table_structure(tables: dict):
    assert isinstance(tables, dict)
    assert len(tables) > 0
    for tid, t in tables.items():
        assert t["table_id"] == tid
        assert "columns" in t and "relations" in t
        assert isinstance(t["columns"], list)
        for col in t["columns"]:
            assert "name" in col
            assert isinstance(col["pk"], bool)


@pytest.mark.skipif(not SAMPLE_XLS, reason="SAMPLE_XLS 환경변수 미설정")
def test_parse_xls_structure():
    _assert_table_structure(parse_file(SAMPLE_XLS))


@pytest.mark.skipif(not SAMPLE_XLSX, reason="SAMPLE_XLSX 환경변수 미설정")
def test_parse_xlsx_structure():
    _assert_table_structure(parse_file(SAMPLE_XLSX))
