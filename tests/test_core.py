import unittest
import os
import tempfile
from core import EmailOTPExtractor, SessionVault


class TestEmailOTPExtractor(unittest.TestCase):
    def test_korean_brackets(self):
        text = "안녕하세요. 요청하신 인증번호는 [849201] 입니다."
        self.assertEqual(EmailOTPExtractor.extract_code(text), "849201")

    def test_korean_keyword(self):
        text = "보안 인증을 진행해주세요. 인증번호: 938201"
        self.assertEqual(EmailOTPExtractor.extract_code(text), "938201")

    def test_english_standard(self):
        text = "Your verification code is 482910. It will expire in 5 minutes."
        self.assertEqual(EmailOTPExtractor.extract_code(text), "482910")

    def test_hyphenated_google_code(self):
        text = "G-592819 is your Google verification code."
        self.assertEqual(EmailOTPExtractor.extract_code(text), "592819")

    def test_magic_link(self):
        text = "Click here to login: https://auth.example.com/magic/confirm?token=xyz123"
        self.assertEqual(
            EmailOTPExtractor.extract_magic_link(text),
            "https://auth.example.com/magic/confirm?token=xyz123"
        )

    def test_masking(self):
        self.assertEqual(EmailOTPExtractor.mask_code("123456"), "12**56")
        self.assertEqual(EmailOTPExtractor.mask_code("1234"), "****")


class TestSessionVault(unittest.TestCase):
    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.vault = SessionVault(self.temp_file.name)

    def tearDown(self):
        if os.path.exists(self.temp_file.name):
            os.remove(self.temp_file.name)

    def test_session_lifecycle(self):
        self.assertIsNone(self.vault.get_session("github.com", "chani"))
        self.assertTrue(self.vault.record_session("github.com", "chani", "/profiles/chani", "Test login"))

        session = self.vault.get_session("github.com", "chani")
        self.assertIsNotNone(session)
        self.assertEqual(session["domain"], "github.com")
        self.assertEqual(session["user_id"], "chani")

        sessions = self.vault.list_sessions()
        self.assertEqual(len(sessions), 1)


if __name__ == "__main__":
    unittest.main()
