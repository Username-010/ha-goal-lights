"""Goal Lights — flash + goaltune (YouTube or local) when your team scores."""

from __future__ import annotations

import logging
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers.typing import ConfigType

from .const import DOMAIN
from .controller import GoalLightsController

_LOGGER = logging.getLogger(__name__)
PLATFORMS = [Platform.SWITCH, Platform.BUTTON]
CARD_URL = "/goal_lights/goal-lights-card.js"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    hass.data.setdefault(DOMAIN, {})
    await _register_card(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    controller = GoalLightsController(hass, entry)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = controller
    await controller.async_start()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    if not hass.services.has_service(DOMAIN, "celebrate"):
        hass.services.async_register(DOMAIN, "flash", _service_flash)
        hass.services.async_register(DOMAIN, "test", _service_test)
        hass.services.async_register(DOMAIN, "celebrate", _service_celebrate)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await _register_card(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    controller: GoalLightsController | None = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
    if controller:
        controller.async_stop()
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not hass.data.get(DOMAIN):
        for svc in ("flash", "test", "celebrate"):
            if hass.services.has_service(DOMAIN, svc):
                hass.services.async_remove(DOMAIN, svc)
    return ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    await hass.config_entries.async_reload(entry.entry_id)


def _controllers(hass: HomeAssistant) -> list[GoalLightsController]:
    return [c for c in hass.data.get(DOMAIN, {}).values() if isinstance(c, GoalLightsController)]


def _match(controller: GoalLightsController, team: str | None, entry_id: str | None) -> bool:
    if entry_id and controller.entry.entry_id != entry_id:
        return False
    if team and controller.slug != str(team).strip().lower().replace(" ", "_"):
        # also allow substring: "feyenoord" matches title "Feyenoord"
        if team.lower() not in controller.slug and team.lower() not in (controller.entry.title or "").lower():
            return False
    return True


async def _service_flash(call: ServiceCall) -> None:
    duration = int(call.data.get("duration", 8))
    for c in _controllers(call.hass):
        if _match(c, call.data.get("team"), call.data.get("entry_id")):
            await c.async_celebrate("goal", duration, ignore_watch=True)


async def _service_test(call: ServiceCall) -> None:
    event = str(call.data.get("event", "goal"))
    for c in _controllers(call.hass):
        if _match(c, call.data.get("team"), call.data.get("entry_id")):
            await c.async_test(event)


async def _service_celebrate(call: ServiceCall) -> None:
    event = str(call.data.get("event", "goal"))
    duration = int(call.data.get("duration", 8))
    for c in _controllers(call.hass):
        if _match(c, call.data.get("team"), call.data.get("entry_id")):
            await c.async_celebrate(event, duration, ignore_watch=False)


async def _register_card(hass: HomeAssistant) -> None:
    www = Path(__file__).parent / "www"
    if not (www / "goal-lights-card.js").is_file():
        return
    try:
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig("/goal_lights", str(www), False)]
        )
    except Exception:  # noqa: BLE001
        _LOGGER.debug("static path already registered")
    try:
        resources = hass.data.get("lovelace")
        store = getattr(resources, "resources", None) or resources
        if hasattr(store, "async_create_item"):
            items = list(store.async_items()) if hasattr(store, "async_items") else []
            urls = {str(i.get("url")) for i in items if isinstance(i, dict)}
            if CARD_URL not in urls:
                await store.async_create_item({"res_type": "module", "url": CARD_URL})
    except Exception:  # noqa: BLE001
        _LOGGER.debug("could not auto-add Lovelace resource")
