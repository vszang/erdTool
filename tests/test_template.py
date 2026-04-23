import pytest
from pathlib import Path
from core.template import download_template, BUNDLED_TEMPLATE


def test_download_template_missing(tmp_path):
    """번들 파일 없을 때 명확한 오류 발생."""
    if BUNDLED_TEMPLATE.exists():
        pytest.skip("번들 템플릿이 이미 존재함")
    with pytest.raises(FileNotFoundError, match="template.xlsx"):
        download_template(str(tmp_path / "out.xlsx"))


def test_download_template_copies(tmp_path):
    """번들 파일 있을 때 지정 경로로 복사."""
    if not BUNDLED_TEMPLATE.exists():
        pytest.skip("번들 템플릿 없음 — core/assets/template.xlsx 배치 후 실행")
    dest = tmp_path / "sub" / "my_template.xlsx"
    result = download_template(str(dest))
    assert Path(result).exists()
    assert Path(result).stat().st_size > 0
