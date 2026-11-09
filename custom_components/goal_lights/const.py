"""Constants for Goal Lights."""

DOMAIN = "goal_lights"

CONF_LIGHTS = "lights"
CONF_TRACKERS = "trackers"
CONF_COLOR_A = "color_a"
CONF_COLOR_B = "color_b"
CONF_EXTRA_COLORS = "extra_colors"
CONF_BRIGHTNESS = "brightness"
CONF_INTERVAL_MS = "interval_ms"
CONF_DURATION_GOAL = "duration_goal"
CONF_DURATION_KICKOFF = "duration_kickoff"
CONF_DURATION_SECOND_HALF = "duration_second_half"
CONF_RESTORE = "restore"
CONF_MEDIA_PLAYER = "media_player"
CONF_YOUTUBE = "youtube"
CONF_LOCAL_MEDIA = "local_media"
CONF_LISTEN = "listen_trackers"
CONF_MEDIA_DURATION = "media_duration"

DEFAULT_COLOR_A = [255, 0, 0]
DEFAULT_COLOR_B = [255, 255, 255]
DEFAULT_BRIGHTNESS = 100
DEFAULT_INTERVAL_MS = 350
DEFAULT_DURATION_GOAL = 8
DEFAULT_DURATION_KICKOFF = 8
DEFAULT_DURATION_SECOND_HALF = 8
DEFAULT_MEDIA_DURATION = 10
DEFAULT_LISTEN = True
DEFAULT_RESTORE = True

HALFTIME_CLOCKS = {
    "Halftime",
    "HT",
    "Half Time",
    "Half-Time",
    "HALF TIME",
    "half-time",
}

ATTR_TEAM_SCORE = "team_score"
ATTR_CLOCK = "clock"
ATTR_QUARTER = "quarter"
