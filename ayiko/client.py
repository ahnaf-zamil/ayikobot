from ayiko.utils.config import BotConfig, get_config
from ayiko.utils.uptime import Uptime

from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorClient

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
        logger: typing.Optional[logging.Logger] = None,
    ):
        self.config: BotConfig = get_config()

        self._logger = logger

        super().__init__(
            token=token if token else os.getenv("BOT_TOKEN"),
            prefix=self.get_prefix,
            intents=intents,
            banner="ayiko.resources",
            insensitive_commands=self.config.case_insensitive,
        )

        self.owner_ids = self.config.owner_ids
        # A list of the bot's guilds for it's current shard
        self.my_guilds: typing.Optional[typing.List[hikari.Snowflake]] = None

        self.start_time = datetime.utcnow()

        self.mongo_client: typing.Optional[AsyncIOMotorClient] = None
        self.db: typing.Optional[AsyncIOMotorDatabase] = None

        self.load_all_extensions()
        self.subscribe(hikari.StartingEvent, self._initialize_mongo)

    async def _initialize_mongo(self, event: hikari.StartingEvent):
        """Initializes a MongoDB connection"""
        mongo_user = os.getenv("MONGO_USER")
        mongo_password = os.getenv("MONGO_PASSWORD")
        mongo_host = os.getenv("MONGO_HOST")
        mongo_port = os.getenv("MONGO_PORT")
        self.mongo_client = AsyncIOMotorClient(
            f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}/ayiko"
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

    @property
    def logger(self) -> logging.Logger:
        """The bot's logger"""
        if not self._logger:
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
