# 진행 상황

## 현재 단계
독립 실행형 패키징(Standalone EXE) 및 고급 커스터마이징 기능 구현 완료. 
다음 단계로 배포 가이드 작성 및 MCP 서버 연동 테스트 진행 가능.

## 완료된 작업
- [x] 프로젝트 방향 확정 (Standalone + MCP 이중 인터페이스)
- [x] XLS 양식 구조 분석 (row 구조, INDEX/KEY 섹션 확인)
- [x] 테이블 객체 구조 설계
- [x] 아키텍처 결정 문서화 (ADR-001 ~ ADR-005)
- [x] CLAUDE.md 작성
- [x] 프로젝트 디렉토리 초기화 (core/, standalone/, mcp/, tests/)
- [x] requirements.txt 작성
- [x] .venv 환경 구성 (.venv/Scripts/python 사용)
- [x] core/parser.py 구현
  - [x] xlsx 지원 추가 (xlrd/openpyxl 어댑터 분기, parse_file() API)
- [x] core/erd_generator.py 구현
- [x] Standalone 구현
  - [x] Flask 앱 (`standalone/app.py`) 개발
  - [x] Vue3 + Vue Flow 프론트엔드 개발
  - [x] 하트비트(Heartbeat) 기반 자동 종료 시스템 구현
  - [x] 커맨드라인 포트(--port, -p) 지정 기능 구현
- [x] PyInstaller exe 패키징 완료
  - [x] xlrd 등 누락 모듈 명시적 임포트 및 빌드 옵션 추가
  - [x] 단일 파일(one-file), 콘솔 숨김(no-console) 적용
- [x] 고급 커스터마이징 기능
  - [x] 캔버스 배경 및 그리드 점 색상 제어
  - [x] 그리드 표시 토글(Show/Hide) 기능
  - [x] 테이블 ID, 명칭, 컬럼속성별 개별 색상 지정
  - [x] 노드 테두리 및 헤더 색상 커스텀
- [x] Export 기능
  - [x] SVG / PNG 이미지 추출 (커스텀 배경색 유지)
  - [x] Excel (openpyxl 역방향 재생성, 관계점 보정 로직 포함)
- [x] 브랜딩 및 UX 개선
  - [x] 브라우저 탭 이름 "ERD Tool" 변경
  - [x] 실행 시 자동 브라우저 오픈

## 다음 작업 목록
- [ ] MCP 서버 최종 구현 및 테스트 (`mcp/mcp_server.py`)
- [ ] Export 기능 추가 (PPT / python-pptx)
- [ ] 다국어 지원 (선택 사항)

## 미해결 이슈
- 현재 로컬 테스트 결과 모든 핵심 기능 정상 작동 확인됨.
- 대규모 ERD에서 자동 종료(Heartbeat) 안정성 추가 모니터링 필요.
