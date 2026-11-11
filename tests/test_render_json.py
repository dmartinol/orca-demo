import json
import unittest

from pulse.render_json import render_json


SUMMARY = {
    "total": 3,
    "errors": 1,
    "by_level": {"error": 1, "info": 2},
    "by_service": {"api": 2, "db": 1},
    "first_ts": "2026-11-11T09:00:00Z",
    "last_ts": "2026-11-11T09:01:00Z",
    "window_seconds": 60,
}


class RenderJsonTest(unittest.TestCase):
    def test_output_round_trips(self):
        output = render_json(SUMMARY)
        self.assertEqual(json.loads(output), SUMMARY)
        self.assertIn("\n  \"total\": 3", output)

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
        self.assertEqual(json.loads(render_json(empty)), empty)


if __name__ == "__main__":
    unittest.main()
