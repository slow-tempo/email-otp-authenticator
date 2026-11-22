#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cli.py: Universal CLI Interface for Email OTP Authenticator & Session Vault
Any agent (Claude Code, Cursor, Codex, Gemini CLI, Antigravity, or Shell scripts) can run this tool.
"""

import sys
import argparse
import json
from core import EmailOTPExtractor, SessionVault


def main():
    parser = argparse.ArgumentParser(description="Universal Email OTP Extractor & Session Vault CLI for AI Agents")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 1. extract
    extract_p = subparsers.add_parser("extract", help="Extract OTP code or magic link from email text")
    extract_p.add_argument("--text", "-t", type=str, help="Raw email text / body")
    extract_p.add_argument("--file", "-f", type=str, help="Path to text/html file to read")
    extract_p.add_argument("--json", action="store_true", help="Output result as JSON")

    # 2. check-session
    check_p = subparsers.add_parser("check-session", help="Check if an authenticated session exists in the vault")
    check_p.add_argument("--domain", "-d", required=True, help="Target domain (e.g. github.com)")
    check_p.add_argument("--user", "-u", default="default", help="User identifier")
    check_p.add_argument("--vault", type=str, default=None, help="Custom vault path")

    # 3. record-session
    record_p = subparsers.add_parser("record-session", help="Record a verified session in the vault")
    record_p.add_argument("--domain", "-d", required=True, help="Target domain (e.g. github.com)")
    record_p.add_argument("--user", "-u", default="default", help="User identifier")
    record_p.add_argument("--profile", "-p", required=True, help="Browser profile directory or session path")
    record_p.add_argument("--notes", default="", help="Optional notes")
    record_p.add_argument("--vault", type=str, default=None, help="Custom vault path")

    # 4. list-sessions
    list_p = subparsers.add_parser("list-sessions", help="List all authenticated sessions")
    list_p.add_argument("--user", "-u", default=None, help="Filter by user")
    list_p.add_argument("--vault", type=str, default=None, help="Custom vault path")

    args = parser.parse_args()

    if args.command == "extract":
        text = args.text or ""
        if args.file:
            with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()

        code = EmailOTPExtractor.extract_code(text)
        link = EmailOTPExtractor.extract_magic_link(text)

        if args.json:
            print(json.dumps({
                "code": code,
                "masked_code": EmailOTPExtractor.mask_code(code) if code else None,
                "magic_link": link,
                "found": bool(code or link)
            }, ensure_ascii=False, indent=2))
        else:
            if code:
                print(f"OTP_CODE: {code}")
            elif link:
                print(f"MAGIC_LINK: {link}")
            else:
                print("NO_OTP_FOUND")
                sys.exit(1)

    elif args.command == "check-session":
        vault = SessionVault(args.vault)
        session = vault.get_session(args.domain, args.user)
        if session:
            print(json.dumps({"has_session": True, "session": session}, ensure_ascii=False, indent=2))
        else:
            print(json.dumps({"has_session": False}, ensure_ascii=False, indent=2))
            sys.exit(2)

    elif args.command == "record-session":
        vault = SessionVault(args.vault)
        ok = vault.record_session(args.domain, args.user, args.profile, args.notes)
        print(json.dumps({"success": ok, "domain": args.domain, "user": args.user}, indent=2))

    elif args.command == "list-sessions":
        vault = SessionVault(args.vault)
        sessions = vault.list_sessions(args.user)
        print(json.dumps({"sessions": sessions, "count": len(sessions)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
