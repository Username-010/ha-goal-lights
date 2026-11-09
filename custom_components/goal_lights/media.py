"""Play / stop goaltune on a media_player."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant

from .parse import media_payload

_LOGGER = logging.getLogger(__name__)


async def play_media(
    hass: HomeAssistant,
    player: str | None,
    youtube: str | None,
    local: Any,
) -> bool:
    if not player:
        return False
    payload = media_payload(youtube, local)
    if not payload:
        return False
    mtype, mid = payload
    st = hass.states.get(player)
    if st is None or st.state in ("unavailable", "unknown"):
        _LOGGER.warning("goal_lights: media player %s not ready", player)
        return False
    try:
        await hass.services.async_call(
            "media_player",
            "turn_on",
            {"entity_id": player},
            blocking=False,
        )
        await hass.services.async_call(
            "media_player",
            "play_media",
            {
                "entity_id": player,
                "media_content_type": mtype,
                "media_content_id": mid,
            },
            blocking=False,
        )
        return True
    except Exception:  # noqa: BLE001
        _LOGGER.exception("goal_lights: play_media failed")
        return False


async def stop_media(hass: HomeAssistant, player: str | None) -> None:
    if not player:
        return
    try:
        await hass.services.async_call(
            "media_player",
            "media_stop",
            {"entity_id": player},
            blocking=False,
        )
    except Exception:  # noqa: BLE001
        _LOGGER.debug("goal_lights: media_stop failed", exc_info=True)
