import unittest

from pulse.render_markdown import render_markdown


SUMMARY = {
    "total": 3,
    "errors": 1,
    "by_level": {"error": 1, "info": 2},
    "by_service": {"api": 2, "db": 1},
    "first_ts": "2026-11-11T09:00:00Z",
    "last_ts": "2026-11-11T09:01:00Z",
    "window_seconds": 60,
}


class RenderMarkdownTest(unittest.TestCase):
    def test_report_has_summary_and_tables(self):
        output = render_markdown(SUMMARY)
        self.assertTrue(output.startswith("# Pulse report"))
        self.assertIn("Events: 3  Errors: 1  Window: 60s", output)
        self.assertIn("## By level", output)
        self.assertIn("| Level | Count |", output)
        self.assertIn("## By service", output)
        self.assertIn("| Service | Count |", output)

    def test_table_cells_escape_pipes_and_collapse_newlines(self):
        summary = dict(
            SUMMARY,
            by_level={"warn|ing\nnext": 1},
            by_service={"api\r\ndb": 1},
        )
        output = render_markdown(summary)
        self.assertIn(r"| warn\|ing next | 1 |", output)
        self.assertIn("| api db | 1 |", output)

    def test_empty_summary(self):
        empty = dict(
            SUMMARY,
            total=0,
            errors=0,
            by_level={},
            by_service={},
            first_ts=None,
            last_ts=None,
            window_seconds=0,
        )
        output = render_markdown(empty)
        self.assertEqual(output, "# Pulse report\n\nNo events recorded.")
        self.assertNotIn("| Level | Count |", output)
        self.assertNotIn("| Service | Count |", output)


if __name__ == "__main__":
    unittest.main()
