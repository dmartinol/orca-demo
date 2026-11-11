import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from pulse.loader import EventError, load_events, parse_event, parse_timestamp


def event(**overrides):
    base = {
        "ts": "2026-11-11T09:00:00Z",
        "level": "info",
        "service": "api",
        "message": "hello",
    }
    base.update(overrides)
    return base


class ParseTimestampTest(unittest.TestCase):
    def test_z_suffix(self):
        self.assertEqual(
            parse_timestamp("2026-11-11T09:00:00Z"),
            datetime(2026, 11, 11, 9, 0, tzinfo=timezone.utc),
        )

    def test_offset_is_normalised_to_utc(self):
        self.assertEqual(
            parse_timestamp("2026-11-11T10:00:00+01:00"),
            datetime(2026, 11, 11, 9, 0, tzinfo=timezone.utc),
        )

    def test_naive_is_assumed_utc(self):
        parsed = parse_timestamp("2026-11-11T09:00:00")
        self.assertEqual(parsed.tzinfo, timezone.utc)

    def test_invalid(self):
        with self.assertRaises(EventError):
            parse_timestamp("not-a-date")


class ParseEventTest(unittest.TestCase):
    def test_normalises_level_and_timestamp(self):
        parsed = parse_event(json.dumps(event(level="ERROR")))
        self.assertEqual(parsed["level"], "error")
        self.assertEqual(parsed["ts"].tzinfo, timezone.utc)

    def test_keeps_unknown_fields(self):
        parsed = parse_event(json.dumps(event(request_id="abc")))
        self.assertEqual(parsed["request_id"], "abc")

    def test_missing_field(self):
        payload = event()
        del payload["service"]
        with self.assertRaisesRegex(EventError, "service"):
            parse_event(json.dumps(payload))

    def test_invalid_json_mentions_line(self):
        with self.assertRaisesRegex(EventError, "line 7"):
            parse_event("{oops", line_number=7)

    def test_non_object(self):
        with self.assertRaises(EventError):
            parse_event("[1, 2, 3]")

    def test_non_string_level(self):
        with self.assertRaises(EventError):
            parse_event(json.dumps(event(level=3)))


class LoadEventsTest(unittest.TestCase):
    def write(self, lines):
        handle = tempfile.NamedTemporaryFile(
            "w", suffix=".jsonl", delete=False, encoding="utf-8"
        )
        handle.write("\n".join(lines))
        handle.close()
        self.addCleanup(Path(handle.name).unlink)
        return handle.name

    def test_skips_blank_lines_and_keeps_order(self):
        path = self.write(
            [
                json.dumps(event(message="first")),
                "",
                json.dumps(event(message="second")),
            ]
        )
        events = load_events(path)
        self.assertEqual([e["message"] for e in events], ["first", "second"])

    def test_propagates_event_error(self):
        path = self.write([json.dumps(event()), "not json"])
        with self.assertRaises(EventError):
            load_events(path)


if __name__ == "__main__":
    unittest.main()
