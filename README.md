# Yonsei Stock Report Mailer

매일 5% 이상 상승하거나 하락한 주식을 찾고, 관련 증권사 분석 리포트를 모아 Gmail로 받아보는 프로젝트입니다.

## 프로젝트 목표

- 전일 대비 5% 이상 등락한 종목을 매일 확인합니다.
- 종목별로 참고할 수 있는 증권사 분석 리포트를 찾습니다.
- 찾은 리포트의 제목, 출처, 링크를 Gmail로 보냅니다.
- 팀원별로 증권사/서비스 출처를 나누어 개발합니다.

## 팀 가이드라인

공통 작업 기준은 [Project Guidelines](docs/PROJECT_GUIDELINES.md)를 따릅니다.

핵심 기준은 아래와 같습니다.

- 대상 시장은 국내 KOSPI입니다.
- 등락률 절댓값이 5% 이상인 종목 중 상위 10개를 고릅니다.
- 각 종목은 리서치, 댓글, 뉴스로 나누어 각 3줄씩 요약합니다.
- 결과는 날짜별 마크다운 폴더에 저장합니다.
- 매일 오후 16:00 KST에 Gmail 뉴스레터를 발송합니다.

## 리포트 출처별 작업 브랜치

| 담당 영역 | 브랜치 이름 | 설명 |
| --- | --- | --- |
| 토스증권 | `feature/toss-securities-reports` | 토스증권에서 확인 가능한 분석 리포트 수집 |
| KB증권 | `feature/kb-securities-reports` | KB증권 분석 리포트 수집 |
| 네이버증권 | `feature/naver-securities-reports` | 네이버증권에서 제공되는 종목 정보와 리포트 수집 |

## 예상 동작 흐름

1. 매일 정해진 시간에 주식 등락률 데이터를 확인합니다.
2. 5% 이상 상승 또는 하락한 종목만 골라냅니다.
3. 각 증권사/서비스별 분석 리포트를 찾습니다.
4. 리포트 제목, 증권사, 종목명, 링크를 정리합니다.
5. Gmail로 요약 메일을 보냅니다.

## 협업 규칙

- `main` 브랜치는 최종 안정 버전으로 사용합니다.
- 새 기능은 직접 `main`에 수정하지 않습니다.
- 각자 담당 브랜치에서 작업한 뒤 Pull Request를 만듭니다.
- API 키, 비밀번호, Gmail 앱 비밀번호는 GitHub에 올리지 않습니다.
- 공개 저장소이므로 개인정보와 유료 리포트 원문을 커밋하지 않습니다.

## 앞으로 만들 파일 예시

```text
src/
  stock_scanner.py
  report_sources/
    toss.py
    kb.py
    naver.py
  email_sender.py
  scheduler.py
tests/
  test_stock_scanner.py
  test_report_sources.py
reports/
  YYYY-MM-DD/
    index.md
README.md
requirements.txt
```

## 실행 방법

아직 구현 전입니다. 기능 구현 후 아래 내용을 업데이트할 예정입니다.

```bash
python -m src.scheduler
```

## 테스트 실행 방법

아직 테스트 파일은 없습니다. 테스트를 추가한 뒤 아래 명령으로 실행할 예정입니다.

```bash
pytest
```
