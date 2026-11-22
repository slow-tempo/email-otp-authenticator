# Email OTP Authenticator & Universal Session Vault

A vendor-agnostic, multi-agent skill & CLI tool designed for autonomous AI agents (Claude Code, Cursor, Codex, Gemini CLI, Antigravity, and custom background workers).

It enables agents to:
1. **Accurately extract OTP / 2FA codes (4~8 digits)** and magic confirmation links from incoming verification emails.
2. **Handle modern browser OTP forms** (including split 6-box PIN inputs and JavaScript auto-advance).
3. **Persist and reuse authenticated sessions** in a thread-safe `SessionVault` so subagents do not need to re-authenticate every time.
4. **Auto-clean verification emails** to keep inboxes clean and secure.

---

## 🚀 Universal Compatibility (어떤 에이전트든 사용 가능)

This tool is **not tied to any single AI agent or platform**:
- **Claude Code**: invoke via terminal / bash tool: `python3 cli.py extract --text "$EMAIL_BODY"`
- **Cursor / Windsurf**: call directly from Composer or tasks.
- **Antigravity / Gemini CLI**: load `SKILL.md` or invoke `cli.py`.
- **Autonomous Subagents / Daemons**: run completely headless in LXC containers or background services without human or parent agent intervention.

---

## 🛠️ Installation & Quick Start

```bash
git clone https://github.com/chani-wtrmax/email-otp-authenticator.git
cd email-otp-authenticator
chmod +x cli.py
```

### 1. Extract OTP Code or Magic Link
```bash
# From raw text
python3 cli.py extract --text "인증번호는 [849201] 입니다."
# Output: OTP_CODE: 849201

# JSON output for AI Agent integration
python3 cli.py extract --text "Your verification code is 482910" --json
```
```json
{
  "code": "482910",
  "masked_code": "48**10",
  "magic_link": null,
  "found": true
}
```

### 2. Check & Record Authenticated Sessions (Session Vault)
```bash
# Check if a session already exists
python3 cli.py check-session --domain "github.com" --user "chani"

# Record a newly authenticated session
python3 cli.py record-session --domain "github.com" --user "chani" --profile "/opt/gateway/profiles/chani"

# List all sessions
python3 cli.py list-sessions
```

---

## 🛡️ Security & Privacy
- **Zero Credential Storage**: Passwords and raw secret keys are never recorded.
- **Safe Masked Logging**: OTP codes are automatically masked (`48**10`) in persistent logs.
- **Immediate Invalidation**: OTP codes are single-use and discarded after submission.
- **User Isolation**: Vault keys are separated per `user_id` to prevent cross-account contamination.

---

## 📄 License
MIT License
