import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "custom_components" / "goal_lights"))
from parse import media_payload, youtube_id


def test_youtube_plain_id():
    assert youtube_id("fubgSjadPY0") == "fubgSjadPY0"


def test_youtube_watch_url():
    assert youtube_id("https://www.youtube.com/watch?v=fubgSjadPY0&t=3") == "fubgSjadPY0"


def test_youtube_short():
    assert youtube_id("https://youtu.be/LEF0kcPdlZA") == "LEF0kcPdlZA"


def test_local_mp3():
    typ, mid = media_payload(None, "/media/goaltunes/fey.mp3")
    assert typ == "music"
    assert mid.endswith("fey.mp3")


def test_youtube_wins_over_local():
    typ, mid = media_payload("https://youtu.be/abcDEF123_-", "/media/x.mp4")
    assert typ == "cast"
    assert "abcDEF123_-" in mid
