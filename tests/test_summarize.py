import unittest
from datetime import datetime, timedelta, timezone

from pulse.summarize import summarize

BASE = datetime(2026, 11, 11, 9, 0, tzinfo=timezone.utc)


def ev(level, service, offset=0):
    return {"ts": BASE + timedelta(seconds=offset), "level": level, "service": service}


class SummarizeTest(unittest.TestCase):
    def test_counts_and_window(self):
        summary = summarize(
            [
                ev("info", "api", 0),
                ev("error", "api", 10),
                ev("fatal", "db", 90),
                ev("debug", "worker", 30),
            ]
        )
        self.assertEqual(summary["total"], 4)
        self.assertEqual(summary["errors"], 2)
        self.assertEqual(summary["by_level"], {"debug": 1, "error": 1, "fatal": 1, "info": 1})
        self.assertEqual(summary["by_service"], {"api": 2, "db": 1, "worker": 1})
        self.assertEqual(summary["window_seconds"], 90)
        self.assertEqual(summary["first_ts"], "2026-11-11T09:00:00Z")
        self.assertEqual(summary["last_ts"], "2026-11-11T09:01:30Z")

    def test_empty(self):
        summary = summarize([])
        self.assertEqual(summary["total"], 0)
        self.assertEqual(summary["errors"], 0)
        self.assertEqual(summary["by_level"], {})
        self.assertIsNone(summary["first_ts"])
        self.assertEqual(summary["window_seconds"], 0)

    def test_accepts_any_iterable(self):
        summary = summarize(iter([ev("warn", "api")]))
        self.assertEqual(summary["total"], 1)


if __name__ == "__main__":
    unittest.main()
