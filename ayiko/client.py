# Copyright (C) 2021 K.M Ahnaf Zamil

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from ayiko.utils.config import BotConfig, get_config

from datetime import datetime
from datetime import timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient

import os
import logging
import typing
import hikari
import lightbulb


__all__: typing.Final[typing.List[str]] = ["Ayiko"]


class Ayiko(lightbulb.Bot):
    """A subclass of lightbulb's bot class. Has some extra stuff that Ayiko requires"""

    def __init__(
        self,
        intents: typing.Optional[hikari.Intents] = hikari.Intents.ALL,
        token: typing.Optional[str] = None,
        *,
        logger: typing.Optional[logging.Logger] = None,
    ):
        self.config: BotConfig = get_config()

        self._logger = logger

        self.start_time = None

        super().__init__(
            token=token if token else os.environ["BOT_TOKEN"],
            prefix=self.get_prefix,
            intents=intents,
            banner="ayiko.resources",
            insensitive_commands=self.config.case_insensitive,
        )

        self.owner_ids = self.config.owner_ids
        # A list of the bot's guilds for it's current shard
        self.my_guilds: typing.Optional[typing.List[hikari.Snowflake]] = []

        self.mongo_client: typing.Optional[AsyncIOMotorClient] = None
        self.db: typing.Optional[AsyncIOMotorDatabase] = None

        self.load_all_extensions()
        self.subscribe(hikari.StartingEvent, self._initialize_mongo)

    async def _initialize_mongo(self, event: hikari.StartingEvent):
        """Initializes a MongoDB connection"""
        mongo_user = os.environ["MONGO_USER"]
        mongo_password = os.environ["MONGO_PASSWORD"]
        mongo_host = os.environ["MONGO_HOST"]
        mongo_port = os.environ["MONGO_PORT"]
        self.mongo_client = AsyncIOMotorClient(
            f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/"
        )
        self.logger.info(
            f"Initialized connection to MongoDB on {mongo_host}:{mongo_port} as {mongo_user}"
        )
        self.db = self.mongo_client["ayiko"]

    async def get_prefix(self, bot, message: hikari.Message) -> str:
        # Will implement custom prefix, for now it will be static
        return self.config.prefix

    def load_all_extensions(self):
        """Loads all lightbulb plugins"""
        for file in os.listdir("ayiko/plugins"):
            if file.endswith(".py"):
                self.load_extension(f"ayiko.plugins.{file[:-3]}")
                self.logger.info(f'Loaded plugin "{file[:-3]}"')

    def run(self, *args, **kwargs):
        self.start_time = datetime.utcnow()
        super().run(*args, **kwargs)

    @property
    def logger(self) -> logging.Logger:
        """The bot's logger"""
        if not self._logger:
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger

    @property
    def uptime(self) -> timedelta:
        """Returns the bot's current uptime"""
        delta_uptime = datetime.utcnow() - self.start_time
        return delta_uptime
