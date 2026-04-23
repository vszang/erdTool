import shutil
from pathlib import Path

BUNDLED_TEMPLATE = Path(__file__).parent / "assets" / "template.xlsx"


def download_template(save_path: str) -> str:
    """번들 빈 양식 xlsx를 지정 경로에 복사. 저장된 경로 반환."""
    if not BUNDLED_TEMPLATE.exists():
        raise FileNotFoundError(
            f"번들 템플릿을 찾을 수 없습니다: {BUNDLED_TEMPLATE}\n"
            "core/assets/template.xlsx 파일을 배치해 주세요."
        )
    dest = Path(save_path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(BUNDLED_TEMPLATE, dest)
    return str(dest)
