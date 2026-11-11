import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from pulse.cli import main


def write_events(lines):
    handle = tempfile.NamedTemporaryFile(
        "w", suffix=".jsonl", delete=False, encoding="utf-8"
    )
    handle.write("\n".join(lines))
    handle.close()
    return Path(handle.name)


class CliTest(unittest.TestCase):
    def run_cli(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_report_text(self):
        path = write_events([
            json.dumps({"ts": "2026-11-11T09:00:00Z", "level": "info",
                        "service": "api", "message": "hi"}),
        ])
        self.addCleanup(path.unlink)
        code, out, _ = self.run_cli(["report", str(path)])
        self.assertEqual(code, 0)
        self.assertIn("Events: 1", out)

    def test_missing_file(self):
        code, _, err = self.run_cli(["report", "/nope/missing.jsonl"])
        self.assertEqual(code, 2)
        self.assertIn("pulse:", err)

    def test_invalid_event(self):
        path = write_events(["not json"])
        self.addCleanup(path.unlink)
        code, _, err = self.run_cli(["report", str(path)])
        self.assertEqual(code, 2)
        self.assertIn("invalid JSON", err)


if __name__ == "__main__":
    unittest.main()
