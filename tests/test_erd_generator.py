from core.erd_generator import generate_mermaid, generate_html
import os

SAMPLE_TABLES = {
    "IBMS000": {
        "table_id": "IBMS000",
        "table_name": "공통코드",
        "table_space": "IBMS_DB",
        "columns": [
            {"name": "CODE_DVN", "description": "코드분류", "type": "VARCHAR2(20)", "pk": True,  "null": "N", "default": ""},
            {"name": "CODE_CD",  "description": "코드",    "type": "VARCHAR2(10)", "pk": True,  "null": "N", "default": ""},
            {"name": "CODE_NM",  "description": "코드명",  "type": "VARCHAR2(100)","pk": False, "null": "Y", "default": ""},
        ],
        "relations": [],
    },
    "IBMS110": {
        "table_id": "IBMS110",
        "table_name": "공장",
        "table_space": "IBMS_DB",
        "columns": [
            {"name": "PLANT_CD", "description": "공장코드", "type": "VARCHAR2(10)", "pk": True,  "null": "N", "default": ""},
            {"name": "PLANT_NM", "description": "공장명",   "type": "VARCHAR2(100)","pk": False, "null": "Y", "default": ""},
        ],
        "relations": [],
    },
    "IBMS200": {
        "table_id": "IBMS200",
        "table_name": "직원",
        "table_space": "IBMS_DB",
        "columns": [
            {"name": "EMP_ID",   "description": "직원ID",   "type": "VARCHAR2(20)", "pk": True,  "null": "N", "default": ""},
            {"name": "PLANT_CD", "description": "공장코드", "type": "VARCHAR2(10)", "pk": False, "null": "N", "default": ""},
        ],
        "relations": [
            {"type": "FK", "column": "PLANT_CD", "ref_table": "IBMS110", "ref_column": "PLANT_CD"},
        ],
    },
}


def test_mermaid_starts_with_erdiagram():
    code = generate_mermaid(SAMPLE_TABLES)
    assert code.startswith("erDiagram")


def test_mermaid_contains_tables():
    code = generate_mermaid(SAMPLE_TABLES)
    assert "IBMS000" in code
    assert "IBMS110" in code
    assert "IBMS200" in code


def test_mermaid_pk_marker():
    code = generate_mermaid(SAMPLE_TABLES)
    assert "CODE_DVN PK" in code
    assert "CODE_NM" in code
    assert "CODE_NM PK" not in code


def test_mermaid_fk_relation():
    code = generate_mermaid(SAMPLE_TABLES)
    assert "IBMS110" in code and "IBMS200" in code
    assert "FK" in code


def test_mermaid_type_normalization():
    code = generate_mermaid(SAMPLE_TABLES)
    assert "VARCHAR2" in code
    assert "(" not in code.split("erDiagram")[1].split("{")[1]


def test_generate_html_creates_file(tmp_path):
    out = str(tmp_path / "test_erd.html")
    result = generate_html(SAMPLE_TABLES, output_path=out)
    assert result == out
    assert os.path.exists(out)
    content = open(out, encoding="utf-8").read()
    assert "erDiagram" in content
    assert "mermaid" in content.lower()
    assert "IBMS000" in content


def test_generate_html_no_cdn(tmp_path):
    out = str(tmp_path / "test_erd.html")
    generate_html(SAMPLE_TABLES, output_path=out)
    content = open(out, encoding="utf-8").read()
    assert "cdn.jsdelivr.net" not in content
    assert "unpkg.com" not in content
