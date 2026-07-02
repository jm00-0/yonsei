# Yonsei Stock Report Mailer

국내 KOSPI 종목을 대상으로 매일 장마감 후 등락률이 큰 종목을 고르고, 리서치/댓글 반응/뉴스를 날짜별 Markdown 뉴스레터로 정리하는 프로젝트입니다.

## 프로젝트 목표

- 대상 시장은 국내 KOSPI입니다.
- 매일 장마감 후 등락률 절댓값이 5% 이상인 종목 중 상위 10개를 선정합니다.
- KB증권 공식 사이트(`https://www.kbsec.com`)를 우선 참고합니다.
- 각 종목별로 아래 3개 섹션을 3줄씩 작성합니다.
  - 리서치 요약
  - 댓글/투자자 반응 요약
  - 뉴스 요약
- 결과는 `reports/YYYY-MM-DD/newsletter.md` 형식으로 저장합니다.
- 메일 초안은 `reports/YYYY-MM-DD/gmail_draft.eml`로 저장합니다.
- `gmail_draft.eml`에는 일반 텍스트와 HTML 뉴스레터 본문이 함께 들어갑니다.

## 파일 구조

```text
src/
  market_data.py       # KOSPI 등락률 데이터 로드와 상위 종목 선정
  kb_research.py       # KB증권 리서치 자료 수집 보조 함수
  news.py              # 뉴스 자료 수집 보조 함수
  comments.py          # 댓글/투자자 반응 자료 수집 보조 함수
  summarizer.py        # 3줄 요약과 실패 처리
  markdown_writer.py   # 날짜별 Markdown 뉴스레터 생성
  gmail_sender.py      # Gmail 발송 전 검토용 HTML 뉴스레터 초안 생성
  scheduler.py         # 매일 16:00 KST 실행 스케줄러
  main.py              # 전체 실행 진입점
tests/
  test_core_logic.py
```

## 안전 규칙

- 실제 API 키, Gmail 비밀번호, OAuth 토큰은 코드에 넣지 않습니다.
- 환경변수로만 인증 정보를 읽습니다.
- 수업 안전 규칙에 따라 자동 메일 발송 대신 `gmail_draft.eml` 초안 파일을 만듭니다.
- 사용자가 초안을 확인한 뒤 직접 발송해야 합니다.
- 웹 수집 시 robots.txt와 사이트 이용약관을 고려합니다.
- 데이터 수집 실패 시 해당 섹션은 `수집 실패`로 표시하고 전체 작업은 계속 진행합니다.

## 환경변수 설정

`.env` 파일 또는 실행 환경에 아래 값을 설정합니다.

```text
GMAIL_SENDER=ssou56@gmail.com
GMAIL_RECIPIENT=recipient@example.com
GOOGLE_APPLICATION_CREDENTIALS=credentials.json
TIMEZONE=Asia/Seoul
KOSPI_MOVERS_CSV=data/kospi_movers.csv
KB_RESEARCH_CSV=data/kb_research.csv
NEWS_CSV=data/news.csv
COMMENTS_CSV=data/comments.csv
```

CSV 파일은 수업용 또는 사용 허가를 받은 데이터만 사용합니다.

### KOSPI_MOVERS_CSV 예시

```csv
symbol,name,market,change_rate
005930,삼성전자,KOSPI,5.25
000660,SK하이닉스,KOSPI,-6.10
```

### KB_RESEARCH_CSV 예시

```csv
symbol,title,url,summary
005930,삼성전자 실적 점검,https://www.kbsec.com,실적 전망을 점검했습니다.
```

### NEWS_CSV 예시

```csv
symbol,title,url,summary,source
005930,삼성전자 관련 뉴스,https://example.com/news,주요 뉴스를 정리했습니다,example
```

### COMMENTS_CSV 예시

```csv
symbol,text,source
005930,투자자들은 실적 회복 여부를 주목하고 있습니다,example
```

## 설치 방법

```bash
pip install -r requirements.txt
```

## 한 번 실행하기

```bash
python -m src.main
```

실행 후 아래 파일이 생성됩니다.

```text
reports/YYYY-MM-DD/newsletter.md
reports/YYYY-MM-DD/gmail_draft.eml
```

`gmail_draft.eml` 파일을 메일 앱에서 열면 뉴스레터처럼 꾸며진 HTML 본문을 확인할 수 있습니다. 같은 파일 안에는 일반 텍스트 본문도 함께 들어 있어 HTML을 지원하지 않는 환경에서도 읽을 수 있습니다.

## 스케줄러 실행 방법

매일 오후 16:00 KST에 뉴스레터 생성 작업을 실행하려면 아래 명령을 사용합니다.

```bash
python -m src.main --schedule
```

이 스케줄러는 계속 실행되는 동안에만 동작합니다. Codex app 실습에서는 실행 상태를 확인하면서 사용하세요.

## 테스트 실행 방법

```bash
pytest
```

## 협업 규칙

- `main` 브랜치는 최종 안정 버전으로 사용합니다.
- 새 기능은 직접 `main`에 수정하지 않습니다.
- 각자 담당 브랜치에서 작업한 뒤 Pull Request를 만듭니다.
- 공개 저장소이므로 개인정보와 유료 리포트 원문을 커밋하지 않습니다.
