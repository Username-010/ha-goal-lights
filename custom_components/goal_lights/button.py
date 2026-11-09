"""Test goal / kickoff / second half buttons on the device page and dashboard."""

from __future__ import annotations

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .controller import GoalLightsController


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    controller: GoalLightsController = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            TestButton(controller, entry, "goal", "test_goal", "mdi:soccer"),
            TestButton(controller, entry, "kickoff", "test_kickoff", "mdi:whistle"),
            TestButton(controller, entry, "second_half", "test_second_half", "mdi:soccer-field"),
        ]
    )


class TestButton(ButtonEntity):
    _attr_has_entity_name = True

    def __init__(
        self,
        controller: GoalLightsController,
        entry: ConfigEntry,
        event: str,
        key: str,
        icon: str,
    ) -> None:
        self._controller = controller
        self._event = event
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key
        self._attr_icon = icon
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "Goal Lights",
        }

    async def async_press(self) -> None:
        await self._controller.async_test(self._event)
