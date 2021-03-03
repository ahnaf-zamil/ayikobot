from ayiko.utils.config import BotConfig, get_config
from ayiko.utils.uptime import Uptime

from datetime import datetime

import os
import logging
import typing
import hikari
import lightbulb


__all__: typing.Final = ["Ayiko"]


class Ayiko(lightbulb.Bot):
    """A subclass of lightbulb's bot class. Has some extra stuff that Ayiko requires"""

    def __init__(
        self,
        intents: typing.Optional[hikari.Intents] = hikari.Intents.ALL,
        token: typing.Optional[str] = None,
        *,
        logger: typing.Optional[logging.Logger] = None
    ):
        self.config: BotConfig = get_config()

        self._logger = logger

        super().__init__(
            token=token if token else os.getenv("BOT_TOKEN"),
            prefix=self.get_prefix,
            intents=intents,
            banner="ayiko.resources",
        )

        self.owner_ids = self.config.owner_ids
        self.start_time = datetime.utcnow()

    async def get_prefix(self, bot, message: hikari.Message) -> str:
        # Will implement custom prefix, for now it will be static
        return self.config.prefix

    @property
    def logger(self) -> logging.Logger:
        if self._logger:
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger

    @property
    def uptime(self) -> Uptime:
        """Returns the bot's current uptime"""
        delta_uptime = datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        return Uptime(days=days, hours=hours, minutes=minutes, seconds=seconds)
