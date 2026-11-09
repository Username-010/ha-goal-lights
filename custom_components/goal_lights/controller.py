"""Flash lights + play goaltune (YouTube or local file)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import Event, HomeAssistant, State, callback
from homeassistant.helpers.event import async_track_state_change_event

from .const import (
    ATTR_CLOCK,
    ATTR_QUARTER,
    ATTR_TEAM_SCORE,
    CONF_BRIGHTNESS,
    CONF_COLOR_A,
    CONF_COLOR_B,
    CONF_DURATION_GOAL,
    CONF_DURATION_KICKOFF,
    CONF_DURATION_SECOND_HALF,
    CONF_EXTRA_COLORS,
    CONF_INTERVAL_MS,
    CONF_LIGHTS,
    CONF_LISTEN,
    CONF_LOCAL_MEDIA,
    CONF_MEDIA_DURATION,
    CONF_MEDIA_PLAYER,
    CONF_RESTORE,
    CONF_TRACKERS,
    CONF_YOUTUBE,
    DEFAULT_BRIGHTNESS,
    DEFAULT_COLOR_A,
    DEFAULT_COLOR_B,
    DEFAULT_DURATION_GOAL,
    DEFAULT_DURATION_KICKOFF,
    DEFAULT_DURATION_SECOND_HALF,
    DEFAULT_INTERVAL_MS,
    DEFAULT_LISTEN,
    DEFAULT_MEDIA_DURATION,
    HALFTIME_CLOCKS,
)
from .media import play_media, stop_media

_LOGGER = logging.getLogger(__name__)


def parse_extra_colors(raw: str | None) -> list[list[int]]:
    colors: list[list[int]] = []
    if not raw:
        return colors
    for part in raw.replace(";", "|").split("|"):
        p = part.strip()
        if not p:
            continue
        if p.startswith("#") and len(p) == 7:
            try:
                colors.append([int(p[1:3], 16), int(p[3:5], 16), int(p[5:7], 16)])
            except ValueError:
                continue
        elif p.count(",") == 2:
            try:
                rgb = [int(x.strip()) for x in p.split(",")]
                if len(rgb) == 3:
                    colors.append(rgb)
            except ValueError:
                continue
    return colors


def color_cycle(data: dict[str, Any]) -> list[list[int]]:
    colors = [
        list(data.get(CONF_COLOR_A) or DEFAULT_COLOR_A),
        list(data.get(CONF_COLOR_B) or DEFAULT_COLOR_B),
    ]
    colors.extend(parse_extra_colors(data.get(CONF_EXTRA_COLORS)))
    return colors


def as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value in ("", "None", "unknown", "unavailable"):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


class GoalLightsController:
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._unsub = None
        self._flash_lock = asyncio.Lock()
        self._second_half_done = False
        self._stop = False
        self.watch_on = True

    @property
    def _data(self) -> dict[str, Any]:
        return {**self.entry.data, **self.entry.options}

    @property
    def slug(self) -> str:
        return (self.entry.title or "team").strip().lower().replace(" ", "_")

    def async_stop(self) -> None:
        self._stop = True
        if self._unsub:
            self._unsub()
            self._unsub = None

    async def async_start(self) -> None:
        data = self._data
        if not data.get(CONF_LISTEN, DEFAULT_LISTEN):
            _LOGGER.info("Goal Lights '%s' not listening to trackers (external trigger)", self.entry.title)
            return
        trackers = data.get(CONF_TRACKERS) or []
        if not trackers:
            return
        self._unsub = async_track_state_change_event(self.hass, trackers, self._async_state_change)

    @callback
    def _async_state_change(self, event: Event) -> None:
        if self._stop or not self.watch_on:
            return
        old: State | None = event.data.get("old_state")
        new: State | None = event.data.get("new_state")
        if new is None or old is None:
            return
        self.hass.async_create_task(self._handle_change(old, new))

    async def _handle_change(self, old: State, new: State) -> None:
        if not self.watch_on:
            return
        data = self._data
        if old.state == "PRE" and new.state == "IN":
            self._second_half_done = False
            await self.async_celebrate("kickoff", int(data.get(CONF_DURATION_KICKOFF, DEFAULT_DURATION_KICKOFF)))
            return
        if new.state == "IN" and not self._second_half_done:
            from_clock = (old.attributes or {}).get(ATTR_CLOCK)
            to_clock = (new.attributes or {}).get(ATTR_CLOCK)
            from_q = as_int((old.attributes or {}).get(ATTR_QUARTER), 0)
            to_q = as_int((new.attributes or {}).get(ATTR_QUARTER), 0)
            left_ht = from_clock in HALFTIME_CLOCKS and to_clock not in HALFTIME_CLOCKS
            period_two = from_q == 1 and to_q == 2
            if left_ht or period_two:
                self._second_half_done = True
                await self.async_celebrate(
                    "second_half", int(data.get(CONF_DURATION_SECOND_HALF, DEFAULT_DURATION_SECOND_HALF))
                )
                return
        if new.state == "IN":
            old_score = (old.attributes or {}).get(ATTR_TEAM_SCORE)
            new_score = (new.attributes or {}).get(ATTR_TEAM_SCORE)
            if old_score not in (None, "", "None") and new_score not in (None, "", "None"):
                if as_int(new_score, -1) > as_int(old_score, -1):
                    await self.async_celebrate("goal", int(data.get(CONF_DURATION_GOAL, DEFAULT_DURATION_GOAL)))

    async def async_test(self, event: str) -> None:
        data = self._data
        mapping = {
            "goal": int(data.get(CONF_DURATION_GOAL, DEFAULT_DURATION_GOAL)),
            "kickoff": int(data.get(CONF_DURATION_KICKOFF, DEFAULT_DURATION_KICKOFF)),
            "second_half": int(data.get(CONF_DURATION_SECOND_HALF, DEFAULT_DURATION_SECOND_HALF)),
        }
        await self.async_celebrate(event, mapping.get(event, mapping["goal"]), ignore_watch=True)

    async def async_celebrate(self, event: str, duration: int, ignore_watch: bool = False) -> None:
        if not ignore_watch and not self.watch_on:
            _LOGGER.info("Goal Lights '%s' skipped %s (watch off)", self.entry.title, event)
            return
        duration = max(2, min(int(duration), 15))
        async with self._flash_lock:
            await asyncio.gather(
                self._do_flash(duration),
                self._do_media(duration),
            )

    async def _do_media(self, duration: int) -> None:
        data = self._data
        player = data.get(CONF_MEDIA_PLAYER)
        youtube = data.get(CONF_YOUTUBE)
        local = data.get(CONF_LOCAL_MEDIA)
        media_dur = int(data.get(CONF_MEDIA_DURATION, DEFAULT_MEDIA_DURATION) or duration)
        media_dur = max(2, min(media_dur, 15))
        played = await play_media(self.hass, player, youtube, local)
        if not played:
            return
        await asyncio.sleep(media_dur)
        await stop_media(self.hass, player)

    async def _do_flash(self, duration: int) -> None:
        data = self._data
        lights: list[str] = list(data.get(CONF_LIGHTS) or [])
        if not lights:
            return
        colors = color_cycle(data)
        brightness = int(data.get(CONF_BRIGHTNESS, DEFAULT_BRIGHTNESS))
        interval = max(0.12, int(data.get(CONF_INTERVAL_MS, DEFAULT_INTERVAL_MS)) / 1000.0)
        restore = bool(data.get(CONF_RESTORE, True))
        scene_id = f"goal_lights_{self.entry.entry_id[:8]}"
        available = [
            eid
            for eid in lights
            if (st := self.hass.states.get(eid)) is not None and st.state not in ("unavailable", "unknown")
        ]
        if not available:
            _LOGGER.warning("%s: all lights unavailable, skip flash", self.entry.title)
            return
        if restore:
            try:
                await self.hass.services.async_call(
                    "scene",
                    "create",
                    {"scene_id": scene_id, "snapshot_entities": available},
                    blocking=True,
                )
            except Exception:  # noqa: BLE001
                _LOGGER.exception("%s: snapshot failed", self.entry.title)
        until = self.hass.loop.time() + duration
        idx = 0
        while self.hass.loop.time() < until and not self._stop:
            color = colors[idx % len(colors)]
            idx += 1
            try:
                await self.hass.services.async_call(
                    "light",
                    "turn_on",
                    {ATTR_ENTITY_ID: available, "rgb_color": color, "brightness_pct": brightness},
                    blocking=False,
                )
            except Exception:  # noqa: BLE001
                _LOGGER.exception("%s: light.turn_on failed", self.entry.title)
            await asyncio.sleep(interval)
        if restore:
            try:
                await self.hass.services.async_call(
                    "scene",
                    "turn_on",
                    {ATTR_ENTITY_ID: f"scene.{scene_id}"},
                    blocking=True,
                )
            except Exception:  # noqa: BLE001
                _LOGGER.exception("%s: restore scene failed", self.entry.title)
