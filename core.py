# -*- coding: utf-8 -*-
"""
core.py: Universal Email OTP Extractor & Session Vault Manager
Pure Python implementation compatible with all AI agent environments.
"""

import os
import re
import sys
import time
import json
import threading
from typing import Optional, Dict, Any, List


class EmailOTPExtractor:
    """Regex-based engine to accurately extract 4-8 digit OTP codes and magic links."""

    EXPLICIT_PATTERNS = [
        re.compile(r"(?:인증번호|인증\s*코드|보안\s*코드|확인\s*코드|verification\s*code|security\s*code|one-time\s*pass(?:word|code)|otp|code)\s*[:：\-is\s]*([0-9]{4,8})\b", re.IGNORECASE),
        re.compile(r"\[([0-9]{4,8})\]\s*(?:이메일\s*인증|인증번호|를\s*입력|is\s*your)", re.IGNORECASE),
        re.compile(r"\b([0-9]{4,8})\b\s*(?:이\s*인증번호|is\s*your\s*verification|is\s*your\s*code)", re.IGNORECASE)
    ]

    SIX_DIGIT_PATTERN = re.compile(r"(?<!\d)([0-9]{6})(?!\d)")
    HYPHEN_PATTERN = re.compile(r"\b(?:G-)?([0-9]{3})-([0-9]{3})\b", re.IGNORECASE)
    MAGIC_LINK_PATTERN = re.compile(r"https?://[^\s'\"<>\n\r]+(?:verify|confirm|magic|auth|token|login)[^\s'\"<>\n\r]*", re.IGNORECASE)

    @classmethod
    def extract_code(cls, text: str) -> Optional[str]:
        """Extract a 4~8 digit OTP code from raw text, prioritizing explicit contexts."""
        if not text:
            return None

        # 1. Check explicit keyword patterns
        for pattern in cls.EXPLICIT_PATTERNS:
            match = pattern.search(text)
            if match:
                return match.group(1)

        # 2. Check hyphenated pattern (e.g., G-123456 or 123-456)
        match = cls.HYPHEN_PATTERN.search(text)
        if match:
            return f"{match.group(1)}{match.group(2)}"

        # 3. Check standalone 6-digit number
        match = cls.SIX_DIGIT_PATTERN.search(text)
        if match:
            return match.group(1)

        return None

    @classmethod
    def extract_magic_link(cls, text: str) -> Optional[str]:
        """Extract a magic verification URL from text."""
        if not text:
            return None
        match = cls.MAGIC_LINK_PATTERN.search(text)
        if match:
            return match.group(0)
        return None

    @classmethod
    def mask_code(cls, code: str) -> str:
        """Mask an OTP code for safe logging (e.g., '849201' -> '84**01')."""
        if not code or len(code) <= 4:
            return "****"
        return f"{code[:2]}{'*' * (len(code) - 4)}{code[-2:]}"


class SessionVault:
    """Thread-safe persistent session registry for cross-agent session reuse."""

    def __init__(self, vault_path: Optional[str] = None):
        if vault_path:
            self.vault_path = vault_path
        else:
            self.vault_path = os.getenv("SESSION_VAULT_PATH", "/opt/gateway/session_vault.json")
            if not os.path.exists(os.path.dirname(self.vault_path)):
                self.vault_path = os.path.expanduser("~/.session_vault.json")

        self.lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        parent = os.path.dirname(self.vault_path)
        if parent and not os.path.exists(parent):
            try:
                os.makedirs(parent, exist_ok=True)
            except Exception:
                pass
        if not os.path.exists(self.vault_path):
            try:
                with open(self.vault_path, "w", encoding="utf-8") as f:
                    json.dump({"version": 1, "sessions": {}}, f, indent=2)
            except Exception:
                pass

    def _load_data(self) -> Dict[str, Any]:
        default_data = {"version": 1, "sessions": {}}
        if not os.path.exists(self.vault_path):
            return default_data
        try:
            with open(self.vault_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return default_data
                return json.loads(content)
        except Exception:
            return default_data

    def get_session(self, domain: str, user_id: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            data = self._load_data()
            sessions = data.get("sessions", {})
            key = f"{user_id}@{domain}"
            return sessions.get(key)

    def record_session(self, domain: str, user_id: str, profile_path: str, notes: str = ""):
        with self.lock:
            try:
                data = self._load_data()
                key = f"{user_id}@{domain}"
                data.setdefault("sessions", {})[key] = {
                    "domain": domain,
                    "user_id": user_id,
                    "profile_path": profile_path,
                    "last_authenticated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "authenticated_epoch": int(time.time()),
                    "notes": notes
                }

                with open(self.vault_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                return False

    def list_sessions(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        with self.lock:
            data = self._load_data()
            sessions = list(data.get("sessions", {}).values())
            if user_id:
                sessions = [s for s in sessions if s.get("user_id") == user_id]
            return sessions
