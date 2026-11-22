---
name: email-otp-authenticator
description: >
  이메일로 전송되는 2FA/OTP 인증번호(4~8자리) 및 매직 링크를 자동으로 수집·추출하여 브라우저 로그인
  폼에 자동 입력하고, 인증 완료 후 일회용 메일을 자동 정리(휴지통 이동)하며, 성공한 사이트의 세션을
  Session Vault에 기록하여 다른 에이전트들이 재사용할 수 있도록 관리한다.
license: MIT
---

# Email OTP Authenticator & Session Vault

브라우저 자동화 과정에서 발생하는 이메일 2FA / OTP 인증 절차를 무인으로 완결하는 스킬.

## 트리거 조건

- 브라우저에 "이메일로 인증번호를 보냈습니다", "Verification code sent to your email", "Check your inbox" 문구가 표시될 때
- 입력 폼에 `autocomplete="one-time-code"`, `name="otp"`, `id="code"` 등이 존재할 때
- 사용자가 "이메일 인증번호 확인해서 입력해줘", "메일 온 거 확인해서 로그인해"라고 요청할 때

## 핵심 기능

1. **2FA DOM 감지**: Playwright/Puppeteer 페이지에서 OTP 입력창 자동 식별
2. **이메일 본문 정밀 추출 (Regex Engine)**:
   - 한국어 표준: `[123456]`, `인증번호: 123456`, `인증코드: 1234`
   - 글로벌 표준: `Verification code: 123456`, `One-time passcode: 123456`
   - 하이픈/접두사: `G-123456`, `123-456`
   - 매직 로그인 링크: `https://.../confirm?token=...`
3. **수신함 자동 정리 (Inbox Clean-up)**: 인증이 끝나면 1회용 인증 메일을 휴지통으로 이동시켜 사용자 메일함 오염 방지
4. **Session Vault 연동**: 인증된 사이트의 쿠키/세션 스냅샷을 Vault에 등록하여 서브에이전트들이 2FA 없이 즉시 재사용

## 보안 원칙 (Security Principles)

- **비밀번호 비저장**: 사용자의 계정 비밀번호는 절대 저장하거나 평문 로그에 기록하지 않는다.
- **OTP 일회성 폐기**: 인증에 사용된 OTP 코드는 메모리에서 즉시 파기하며 로그에는 마스킹(`73***1`) 처리한다.
- **수신 시점 검증**: 최근 2분 이내에 수신된 최신 메일만 검증 대상으로 삼아 구형 메일 오탐을 방지한다.
- **사용자 격리**: 세션 볼트는 사용자 ID(`user_id`)별로 엄격히 분리하여 타 사용자의 세션을 침범하지 않는다.

## 사용 예시

```python
from email_otp_authenticator import EmailOTPExtractor, SessionVault

# 1. 메일 본문에서 인증 코드 추출
email_body = "안녕하세요. 요청하신 인증번호는 [849201] 입니다."
code = EmailOTPExtractor.extract_code(email_body)  # "849201"

# 2. 브라우저 폼에 자동 타이핑 후 제출
page.fill('input[autocomplete="one-time-code"]', code)
page.click('button[type="submit"]')

# 3. 세션 볼트에 성공 상태 기록
vault = SessionVault()
vault.record_session("github.com", user_id="chani", profile_path="/opt/gateway/profiles/chani")
```
