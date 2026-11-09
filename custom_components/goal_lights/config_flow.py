"""Config flow for Goal Lights."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    BooleanSelector,
    ColorRGBSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    TextSelector,
)

from .const import (
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
    DEFAULT_RESTORE,
    DOMAIN,
)


def _schema(d: dict[str, Any] | None = None) -> vol.Schema:
    d = d or {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=d.get(CONF_NAME, "Goal Lights")): TextSelector(),
            vol.Optional(CONF_TRACKERS, default=d.get(CONF_TRACKERS, [])): EntitySelector(
                EntitySelectorConfig(domain=["sensor"], multiple=True)
            ),
            vol.Required(CONF_LIGHTS, default=d.get(CONF_LIGHTS, [])): EntitySelector(
                EntitySelectorConfig(domain=["light"], multiple=True)
            ),
            vol.Required(CONF_COLOR_A, default=d.get(CONF_COLOR_A, DEFAULT_COLOR_A)): ColorRGBSelector(),
            vol.Required(CONF_COLOR_B, default=d.get(CONF_COLOR_B, DEFAULT_COLOR_B)): ColorRGBSelector(),
            vol.Optional(CONF_EXTRA_COLORS, default=d.get(CONF_EXTRA_COLORS, "")): TextSelector(),
            vol.Optional(CONF_MEDIA_PLAYER, default=d.get(CONF_MEDIA_PLAYER)): EntitySelector(
                EntitySelectorConfig(domain=["media_player"])
            ),
            vol.Optional(CONF_YOUTUBE, default=d.get(CONF_YOUTUBE, "")): TextSelector(),
            vol.Optional(CONF_LOCAL_MEDIA, default=d.get(CONF_LOCAL_MEDIA, "")): TextSelector(),
            vol.Required(
                CONF_MEDIA_DURATION, default=d.get(CONF_MEDIA_DURATION, DEFAULT_MEDIA_DURATION)
            ): NumberSelector(
                NumberSelectorConfig(min=2, max=15, step=1, unit_of_measurement="s", mode=NumberSelectorMode.SLIDER)
            ),
            vol.Required(
                CONF_BRIGHTNESS, default=d.get(CONF_BRIGHTNESS, DEFAULT_BRIGHTNESS)
            ): NumberSelector(
                NumberSelectorConfig(min=1, max=100, step=1, unit_of_measurement="%", mode=NumberSelectorMode.SLIDER)
            ),
            vol.Required(
                CONF_INTERVAL_MS, default=d.get(CONF_INTERVAL_MS, DEFAULT_INTERVAL_MS)
            ): NumberSelector(
                NumberSelectorConfig(min=150, max=1200, step=50, unit_of_measurement="ms", mode=NumberSelectorMode.SLIDER)
            ),
            vol.Required(
                CONF_DURATION_GOAL, default=d.get(CONF_DURATION_GOAL, DEFAULT_DURATION_GOAL)
            ): NumberSelector(
                NumberSelectorConfig(min=2, max=15, step=1, unit_of_measurement="s", mode=NumberSelectorMode.BOX)
            ),
            vol.Required(
                CONF_DURATION_KICKOFF, default=d.get(CONF_DURATION_KICKOFF, DEFAULT_DURATION_KICKOFF)
            ): NumberSelector(
                NumberSelectorConfig(min=2, max=15, step=1, unit_of_measurement="s", mode=NumberSelectorMode.BOX)
            ),
            vol.Required(
                CONF_DURATION_SECOND_HALF,
                default=d.get(CONF_DURATION_SECOND_HALF, DEFAULT_DURATION_SECOND_HALF),
            ): NumberSelector(
                NumberSelectorConfig(min=2, max=15, step=1, unit_of_measurement="s", mode=NumberSelectorMode.BOX)
            ),
            vol.Required(CONF_RESTORE, default=d.get(CONF_RESTORE, DEFAULT_RESTORE)): BooleanSelector(),
            vol.Required(CONF_LISTEN, default=d.get(CONF_LISTEN, DEFAULT_LISTEN)): BooleanSelector(),
        }
    )


class GoalLightsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            name = user_input.pop(CONF_NAME)
            await self.async_set_unique_id(f"{DOMAIN}:{name}")
            self._abort_if_unique_id_configured()
            data = {k: v for k, v in user_input.items() if v not in (None, "")}
            return self.async_create_entry(title=name, data=data)
        return self.async_show_form(step_id="user", data_schema=_schema())

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return GoalLightsOptionsFlow()


class GoalLightsOptionsFlow(config_entries.OptionsFlow):
    async def async_step_init(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            user_input.pop(CONF_NAME, None)
            data = {k: v for k, v in user_input.items() if v not in (None, "")}
            return self.async_create_entry(title="", data=data)
        current = {**self.config_entry.data, **self.config_entry.options}
        current[CONF_NAME] = self.config_entry.title
        return self.async_show_form(step_id="init", data_schema=_schema(current))
