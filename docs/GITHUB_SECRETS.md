# GitHub Secrets 설정 가이드

이 문서는 Gmail 뉴스레터를 자동 발송할 때 필요한 GitHub Secrets 설정 방법을 설명합니다.

## 필요한 Secrets

GitHub 저장소의 Actions Secrets에 아래 3개 값을 추가해야 합니다.

| Secret 이름 | 설명 | 예시 |
| --- | --- | --- |
| `GMAIL_SENDER` | 뉴스레터를 보내는 Gmail 주소입니다. | `yourname@gmail.com` |
| `GMAIL_APP_PASSWORD` | Gmail 앱 비밀번호입니다. 일반 Gmail 로그인 비밀번호가 아닙니다. | `abcd efgh ijkl mnop` |
| `NEWSLETTER_RECIPIENTS` | 뉴스레터를 받을 이메일 목록입니다. 여러 명이면 쉼표로 구분합니다. | `a@example.com,b@example.com` |

## GitHub에서 Secrets 추가하는 방법

1. GitHub에서 `jm00-0/yonsei` 저장소로 이동합니다.
2. 상단 메뉴에서 `Settings`를 클릭합니다.
3. 왼쪽 메뉴에서 `Secrets and variables`를 클릭합니다.
4. 하위 메뉴에서 `Actions`를 클릭합니다.
5. `New repository secret` 버튼을 클릭합니다.
6. `Name`에 Secret 이름을 입력합니다.
7. `Secret`에 실제 값을 입력합니다.
8. `Add secret` 버튼을 클릭합니다.
9. 위 과정을 반복해서 `GMAIL_SENDER`, `GMAIL_APP_PASSWORD`, `NEWSLETTER_RECIPIENTS`를 모두 추가합니다.

## Gmail 앱 비밀번호 준비

`GMAIL_APP_PASSWORD`에는 Gmail 계정의 일반 비밀번호를 넣으면 안 됩니다.

Google 계정에서 2단계 인증을 켠 뒤, 앱 비밀번호를 새로 만들어 사용합니다. 생성된 앱 비밀번호는 GitHub Secrets에만 저장합니다.

## 공개 저장소 주의사항

이 저장소는 공개 저장소입니다.

절대로 Gmail 비밀번호, 앱 비밀번호, 수신자 목록 같은 민감한 값을 코드나 문서에 직접 커밋하지 마세요.

다음 위치에도 실제 비밀번호를 쓰면 안 됩니다.

- `README.md`
- Python 코드 파일
- 테스트 파일
- GitHub Actions workflow 파일
- `.env` 파일을 커밋한 경우

민감한 값은 항상 GitHub Secrets에만 저장해야 합니다. 만약 실수로 비밀번호를 커밋했다면 즉시 비밀번호를 폐기하고 새 앱 비밀번호를 발급받으세요.
