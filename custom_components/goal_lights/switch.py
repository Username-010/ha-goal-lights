"""Watch switch — live goals only fire when this is on. Test buttons still work."""

from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .controller import GoalLightsController


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    controller: GoalLightsController = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([WatchSwitch(controller, entry)])


class WatchSwitch(SwitchEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "watch"
    _attr_icon = "mdi:eye"

    def __init__(self, controller: GoalLightsController, entry: ConfigEntry) -> None:
        self._controller = controller
        self._attr_unique_id = f"{entry.entry_id}_watch"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Goal Lights",
        }
        self._attr_is_on = True
        controller.watch_on = True

    @property
    def is_on(self) -> bool:
        return self._controller.watch_on

    async def async_turn_on(self, **kwargs) -> None:
        self._controller.watch_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        self._controller.watch_on = False
        self.async_write_ha_state()
