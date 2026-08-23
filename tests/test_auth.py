import tempfile
import unittest
from pathlib import Path

from biobricks.auth import strip_token_from_url, scrub_git_config_tokens, git_auth
from unittest.mock import patch


class AuthUrlTests(unittest.TestCase):
    def test_strip_token_from_url(self):
        self.assertEqual(
            strip_token_from_url("https://ghp_secret123@github.com/biobricks-ai/tox21"),
            "https://github.com/biobricks-ai/tox21")
        self.assertEqual(
            strip_token_from_url("https://github.com/biobricks-ai/tox21"),
            "https://github.com/biobricks-ai/tox21")

    def test_git_auth_without_token(self):
        with patch("biobricks.auth.get_github_token", return_value=None):
            args, env = git_auth({"PATH": "/usr/bin"})
        self.assertEqual(args, [])
        self.assertNotIn("BIOBRICKS_GIT_TOKEN", env)

    def test_git_auth_with_token_keeps_token_out_of_args(self):
        with patch("biobricks.auth.get_github_token", return_value="gho_secret"):
            args, env = git_auth({"PATH": "/usr/bin"})
        self.assertNotIn("gho_secret", " ".join(args))
        self.assertEqual(env["BIOBRICKS_GIT_TOKEN"], "gho_secret")

    def test_scrub_git_config_tokens(self):
        with tempfile.TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "biobricks-ai" / "tox21" / ("a" * 40) / ".git"
            cfg.mkdir(parents=True)
            cfg = cfg / "config"
            cfg.write_text('[remote "origin"]\n\turl = https://gho_secret@github.com/biobricks-ai/tox21\n')
            self.assertEqual(scrub_git_config_tokens(tmp), 1)
            self.assertNotIn("gho_secret", cfg.read_text())
            self.assertIn("url = https://github.com/biobricks-ai/tox21", cfg.read_text())
            # second run finds nothing to fix
            self.assertEqual(scrub_git_config_tokens(tmp), 0)


if __name__ == "__main__":
    unittest.main()
