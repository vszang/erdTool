# ERD Tool

엑셀 테이블 정의서(XLS/XLSX)를 파싱하여 인터랙티브 ERD를 생성하는 도구입니다.  
Flask + Vue3 기반의 Standalone 웹 앱과 Claude Desktop 연동용 MCP 서버, 두 가지 인터페이스를 제공합니다.

---

## 요구 사항

| 항목 | 버전 |
|------|------|
| Python | 3.12 이상 |
| Node.js | 20.19.0 이상 또는 22.12.0 이상 |
| npm | Node.js 설치 시 포함 |

---

## 설치

### 1. 저장소 클론

```bash
git clone <repository-url>
cd erdTool
```

### 2. Python 가상환경 생성 및 패키지 설치

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. 프론트엔드 의존성 설치 및 빌드

```bash
cd standalone/frontend
npm install
npm run build
cd ../..
```

---

## 실행

### Standalone 웹 앱 (Flask + Vue3)

```bash
python standalone/app.py
```

기본 포트는 `5000`입니다. 포트를 변경하려면 `--port`(`-p`) 옵션을 사용합니다.

```bash
python standalone/app.py --port 8080
```

실행 후 브라우저가 자동으로 열립니다. 브라우저 탭을 닫으면 서버가 15초 내에 자동 종료됩니다.

### MCP 서버 (Claude Desktop 연동)

`claude_desktop_config.json`에 아래 내용을 추가합니다.

```json
{
  "mcpServers": {
    "erd-tool": {
      "command": "python",
      "args": ["<절대경로>/erdTool/mcp/mcp_server.py"]
    }
  }
}
```

---

## EXE 패키징 (Windows)

프론트엔드 빌드가 완료된 상태에서 아래 명령을 실행합니다.

```bash
cd standalone
python build_standalone.py
```

빌드 완료 후 `standalone/dist/ERD_Tool.exe` 파일이 생성됩니다.  
해당 EXE 파일 하나만 복사하여 다른 PC에서도 실행할 수 있습니다.

---

## 주요 기능

- **XLS/XLSX/JSON 업로드**: 테이블 정의서 파싱 및 ERD 자동 생성
- **인터랙티브 ERD**: Vue Flow 기반 드래그, 줌, 컬럼 토글
- **테마 커스터마이징**: 캔버스 배경, 그리드, 노드 요소별 색상 지정 (설정은 브라우저에 저장)
- **Export**: SVG / PNG 이미지, Excel(원본 양식 역재생성)

---

## 프로젝트 구조

```
erdTool/
├── core/
│   ├── parser.py           # XLS/XLSX 파싱 → 테이블 객체
│   ├── erd_generator.py    # 테이블 객체 → ERD HTML
│   └── template.py         # 빈 양식 XLS 생성
├── standalone/
│   ├── app.py              # Flask 서버 진입점
│   ├── build_standalone.py # PyInstaller 빌드 스크립트
│   └── frontend/           # Vue3 프로젝트
├── mcp/
│   └── mcp_server.py       # MCP stdio 서버
├── tests/
├── requirements.txt
└── README.md
```

---

## 개발 모드 (프론트엔드 핫 리로드)

백엔드와 프론트엔드를 별도 터미널에서 각각 실행합니다.

```bash
# 터미널 1 — Flask 백엔드
python standalone/app.py

# 터미널 2 — Vite 개발 서버
cd standalone/frontend
npm run dev
```

---

## 라이선스

내부 도구용. 별도 라이선스 미정.
