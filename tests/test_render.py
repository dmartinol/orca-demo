import unittest

from pulse.render import render_text

SUMMARY = {
    "total": 3,
    "errors": 1,
    "by_level": {"error": 1, "info": 2},
    "by_service": {"api": 2, "db": 1},
    "first_ts": "2026-11-11T09:00:00Z",
    "last_ts": "2026-11-11T09:01:00Z",
    "window_seconds": 60,
}


class RenderTextTest(unittest.TestCase):
    def test_contains_totals_and_breakdowns(self):
        output = render_text(SUMMARY)
        self.assertIn("Events: 3  Errors: 1", output)
        self.assertIn("60s", output)
        self.assertIn("error", output)
        self.assertIn("api", output)

    def test_empty_summary(self):
        empty = dict(SUMMARY, total=0, errors=0, by_level={}, by_service={},
                     first_ts=None, last_ts=None, window_seconds=0)
        self.assertIn("No events.", render_text(empty))


if __name__ == "__main__":
    unittest.main()
