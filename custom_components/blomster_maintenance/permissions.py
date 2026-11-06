"""Behörighetskontroller för integrationens skrivande tjänster."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import Unauthorized, UnknownUser


async def async_require_admin(hass: HomeAssistant, call: ServiceCall) -> None:
    """Tillåt interna anrop men kräv admin för användarinitierade anrop."""
    user_id = call.context.user_id
    if not user_id:
        return

    user = await hass.auth.async_get_user(user_id)
    if user is None:
        raise UnknownUser(context=call.context, user_id=user_id)
    if not user.is_admin:
        raise Unauthorized(context=call.context, user_id=user_id)
