# wtool-erd

## 프로젝트 개요

엑셀 테이블 정의서(XLS)를 파싱하여 인터랙티브 ERD를 생성하는 도구.
코어 로직을 공유하고 Standalone(Flask + Vue3)과 MCP 두 가지 인터페이스를 제공한다.

## 기술 스택

| 역할 | 기술 |
|------|------|
| 코어 | Python 3.12 |
| XLS 파싱 | xlrd |
| 양식 생성 | openpyxl |
| ERD 렌더링 | Mermaid.js (정적) / Vue Flow (인터랙티브) |
| Standalone 백엔드 | Python Flask |
| Standalone 프론트 | Vue3 (빌드 후 Flask static) |
| 패키징 | PyInstaller (exe) |
| MCP 서버 | Python MCP (stdio) |

## 아키텍처 구조

```
wtool-erd/
├── core/
│   ├── parser.py           # XLS 파싱 → 테이블 객체
│   ├── erd_generator.py    # 테이블 객체 → Mermaid / HTML
│   └── template.py         # 빈 양식 XLS 생성
├── standalone/
│   ├── app.py              # Flask 서버
│   └── frontend/           # Vue3 프로젝트 (빌드 후 dist/)
├── mcp/
│   └── mcp_server.py       # MCP stdio 서버
└── requirements.txt
```

```
[Standalone]              [MCP]
Flask + Vue3              Claude Desktop
     │                         │
     └──────────┬──────────────┘
                ▼
           [core/]
     parser.py / erd_generator.py / template.py
```

## 핵심 개발 규칙

1. 코어 로직은 Flask, MCP 어느 쪽에도 의존하지 않는다
2. 테이블 파싱 결과는 항상 Python dict (JSON 직렬화 가능) 형태로 반환
3. XLS 포맷 변경에 대비해 파싱 로직은 parser.py 한 곳에만 집중
4. CDN 의존 금지 — 프론트 빌드 시 모든 의존성 번들에 포함
5. 환경변수는 .env 사용, 경로 하드코딩 금지
6. FK 추론은 컬럼명 패턴 기반 (명시적 INDEX/KEY 섹션 우선)

## XLS 양식 구조

```
row 0     : (빈 행)
row 1     : "Table 기술서"
row 2     : Table ID  (col 2)
row 3     : Table Space (col 2)
row 4     : Table명   (col 2)
row 5     : 헤더 (번호 / 필드ID / Field Description / PK / Data Type / Null / Default Value / 비고)
row 6     : (빈 행)
row 7~    : 컬럼 데이터 (번호가 숫자인 동안 계속)
row 38    : INDEX\nKEY 섹션 (FK 명시 예정)
```

시트 구성:
- `T_00` : 빈 템플릿 (스킵)
- `목록`  : 테이블 인덱스 (스킵)
- 나머지  : 테이블별 시트

## 테이블 객체 구조 (core 출력 형식)

```python
{
  "IBMS000": {
    "table_id": "IBMS000",
    "table_name": "공통코드",
    "table_space": "IBMS_DB",
    "columns": [
      {
        "name": "CODE_DVN",
        "description": "코드분류",
        "type": "VARCHAR2(20)",
        "pk": True,
        "null": "N",
        "default": "기본값 없음"
      },
      ...
    ],
    "relations": [
      {
        "type": "FK",
        "column": "PLANT_CD",
        "ref_table": "IBMS110",
        "ref_column": "PLANT_CD"
      }
    ]
  },
  ...
}
```

## MCP 툴 설계

```python
download_template(save_path: str)   # 지정 경로에 빈 양식 XLS 저장
generate_erd(file_path: str)        # 로컬 XLS 경로 → ERD HTML 생성 → 브라우저 오픈
```

## Standalone 기능 세부 사양

- **XLS/XLSX/JSON 업로드**: 대용량 테이블 정의서 파싱 지원
- **인터랙티브 ERD**: Vue Flow 기반 드래그, 줌, 컬럼 토글
- **고급 테마 커스텀**: 캔버스 배경, 그리드 표시, 요소별(ID/이름/속성) 색상 지정
- **하트비트 시스템**: 브라우저 종료 시 서버 프로세스 자동 종료 (ADR-006)
- **포트 지정**: `--port`(-p) 인자를 통한 실행 포트 변경 지원
- **Export**:
    - 이미지: SVG / PNG (커스텀 배경색 포함)
    - 엑셀: openpyxl 기반 원본 양식 역기록 (관계선 보정 포함)

## Export 방식

| 포맷 | 방법 |
|------|------|
| SVG | 캔버스 SVG 직접 추출 |
| Excel | openpyxl — 테이블 정의서 역방향 재생성 |
| PPT | python-pptx — 테이블별 슬라이드 생성 |

## 세션 시작 시 반드시 할 것

1. @.claude/progress.md 읽기 (현재 진행 상황 파악)
2. @.claude/decisions.md 읽기 (아키텍처 결정 사항 파악)
3. @.claude/context.md 읽기 (직전 작업 컨텍스트 파악)
4. 파악한 내용 요약 후 작업 시작

## 세션 종료 또는 주요 작업 완료 시 반드시 할 것

1. @.claude/progress.md 업데이트
   - 완료한 작업 체크
   - 다음 작업 목록 갱신
   - 미해결 이슈 기록
2. 아키텍처/기술 결정이 있었다면 @.claude/decisions.md에 이유와 함께 기록
3. 다음 세션에서 알아야 할 것 @.claude/context.md에 기록

## 상세 가이드 (필요 시 참조)

- 파싱 규칙: @docs/skills/parser.md
- ERD 생성 규칙: @docs/skills/erd.md
- Standalone 규칙: @docs/skills/standalone.md
- MCP 규칙: @docs/skills/mcp.md