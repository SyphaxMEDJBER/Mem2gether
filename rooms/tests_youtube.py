from django.test import SimpleTestCase

from .views import _extract_youtube_id


class ExtractYouTubeIdTests(SimpleTestCase):
    def test_extracts_watch_url(self):
        self.assertEqual(
            _extract_youtube_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_extracts_short_url(self):
        self.assertEqual(
            _extract_youtube_id("https://youtu.be/dQw4w9WgXcQ?si=test"),
            "dQw4w9WgXcQ",
        )

    def test_extracts_shorts_url(self):
        self.assertEqual(
            _extract_youtube_id("https://www.youtube.com/shorts/dQw4w9WgXcQ"),
            "dQw4w9WgXcQ",
        )

    def test_extracts_live_url(self):
        self.assertEqual(
            _extract_youtube_id("https://www.youtube.com/live/dQw4w9WgXcQ?feature=share"),
            "dQw4w9WgXcQ",
        )

    def test_accepts_raw_video_id(self):
        self.assertEqual(_extract_youtube_id("dQw4w9WgXcQ"), "dQw4w9WgXcQ")

    def test_rejects_invalid_value(self):
        self.assertEqual(_extract_youtube_id("pas-une-video"), "")
