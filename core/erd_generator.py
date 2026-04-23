import os
import urllib.request
import webbrowser
from pathlib import Path

MERMAID_CDN = "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"
ASSETS_DIR = Path(__file__).parent / "assets"
MERMAID_LOCAL = ASSETS_DIR / "mermaid.min.js"


def _ensure_mermaid_js() -> str:
    """mermaid.min.js 로컬 캐시 확보 후 내용 반환."""
    ASSETS_DIR.mkdir(exist_ok=True)
    if not MERMAID_LOCAL.exists():
        urllib.request.urlretrieve(MERMAID_CDN, MERMAID_LOCAL)
    return MERMAID_LOCAL.read_text(encoding="utf-8")


# ── Mermaid ERD 코드 생성 ──────────────────────────────────────────────────

def _mermaid_type(col_type: str) -> str:
    """Mermaid ERD에서 허용하는 타입명으로 정규화."""
    t = col_type.upper().replace(" ", "_")
    # 괄호/숫자 제거 (VARCHAR2(20) → VARCHAR2)
    paren = t.find("(")
    if paren != -1:
        t = t[:paren]
    return t or "VARCHAR"


def generate_mermaid(tables: dict) -> str:
    """테이블 dict → Mermaid erDiagram 코드."""
    lines = ["erDiagram"]

    for tid, t in tables.items():
        lines.append(f"    {tid} {{")
        for col in t["columns"]:
            col_type = _mermaid_type(col["type"])
            pk_marker = " PK" if col["pk"] else ""
            safe_name = col["name"].replace("-", "_")
            lines.append(f'        {col_type} {safe_name}{pk_marker}')
        lines.append("    }")

    # 관계선
    for tid, t in tables.items():
        for rel in t["relations"]:
            if rel["type"] == "FK" and rel["ref_table"]:
                ref = rel["ref_table"]
                if ref in tables:
                    lines.append(f"    {ref} ||--o{{ {tid} : FK")
            elif rel["type"] == "FK_INFERRED" and rel["ref_table"]:
                ref = rel["ref_table"]
                if ref in tables:
                    lines.append(f"    {ref} ||--o{{ {tid} : inferred")

    return "\n".join(lines)


# ── HTML 생성 ─────────────────────────────────────────────────────────────

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>ERD</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: sans-serif; background: #1e1e2e; color: #cdd6f4; }}
  #toolbar {{
    display: flex; align-items: center; gap: 12px;
    padding: 10px 16px; background: #181825; border-bottom: 1px solid #313244;
  }}
  #toolbar h1 {{ font-size: 15px; font-weight: 600; margin-right: auto; }}
  #toolbar button {{
    padding: 5px 12px; border: 1px solid #45475a; border-radius: 6px;
    background: #313244; color: #cdd6f4; cursor: pointer; font-size: 13px;
  }}
  #toolbar button:hover {{ background: #45475a; }}
  #search {{
    padding: 5px 10px; border: 1px solid #45475a; border-radius: 6px;
    background: #313244; color: #cdd6f4; font-size: 13px; width: 200px;
  }}
  #container {{
    width: 100vw; height: calc(100vh - 45px);
    overflow: auto; padding: 24px;
  }}
  #diagram svg {{ max-width: none !important; }}
  .highlight-node rect {{ stroke: #f38ba8 !important; stroke-width: 3px !important; }}
</style>
</head>
<body>
<div id="toolbar">
  <h1>ERD Viewer</h1>
  <input id="search" type="text" placeholder="테이블 검색...">
  <button onclick="zoomIn()">＋</button>
  <button onclick="zoomOut()">－</button>
  <button onclick="resetZoom()">리셋</button>
  <button onclick="exportSvg()">SVG 저장</button>
</div>
<div id="container">
  <div id="diagram" class="mermaid">
{mermaid_code}
  </div>
</div>

<script>
{mermaid_js}
</script>
<script>
mermaid.initialize({{ startOnLoad: true, theme: 'dark', er: {{ diagramPadding: 40 }} }});

let scale = 1;
const diagramEl = document.getElementById('diagram');

function zoomIn()    {{ scale = Math.min(scale + 0.1, 3);   applyZoom(); }}
function zoomOut()   {{ scale = Math.max(scale - 0.1, 0.2); applyZoom(); }}
function resetZoom() {{ scale = 1; applyZoom(); }}
function applyZoom() {{ diagramEl.style.transform = `scale(${{scale}})`; diagramEl.style.transformOrigin = 'top left'; }}

document.getElementById('search').addEventListener('input', function() {{
  const q = this.value.trim().toLowerCase();
  document.querySelectorAll('.er.entityBox, .entityLabel').forEach(el => {{
    const label = el.textContent.trim().toLowerCase();
    el.closest('g') && (el.closest('g').style.opacity = (!q || label.includes(q)) ? '1' : '0.2');
  }});
}});

function exportSvg() {{
  const svg = document.querySelector('#diagram svg');
  if (!svg) return;
  const blob = new Blob([svg.outerHTML], {{ type: 'image/svg+xml' }});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'erd.svg';
  a.click();
}}
</script>
</body>
</html>
"""


def generate_html(tables: dict, output_path: str | None = None) -> str:
    """테이블 dict → 자체 포함 ERD HTML 파일 생성, 경로 반환."""
    mermaid_code = generate_mermaid(tables)
    mermaid_js = _ensure_mermaid_js()

    html = _HTML_TEMPLATE.format(
        mermaid_code=mermaid_code,
        mermaid_js=mermaid_js,
    )

    if output_path is None:
        import tempfile
        fd, output_path = tempfile.mkstemp(suffix=".html", prefix="erd_")
        os.close(fd)

    Path(output_path).write_text(html, encoding="utf-8")
    return output_path


def open_erd(tables: dict, output_path: str | None = None) -> str:
    """ERD HTML 생성 후 기본 브라우저로 오픈. 파일 경로 반환."""
    path = generate_html(tables, output_path)
    webbrowser.open(f"file:///{Path(path).as_posix()}")
    return path
