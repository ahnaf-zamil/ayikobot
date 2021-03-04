from ayiko.client import Ayiko
from motor.motor_asyncio import AsyncIOMotorCollection

import lightbulb
import hikari
import typing


class GuildConfig(lightbulb.Plugin):
    def __init__(self, client: Ayiko):
        super().__init__()
        self.client = client
        self.collection: typing.Optional[AsyncIOMotorCollection] = None

    @lightbulb.listener(hikari.StartedEvent)
    async def on_started(self, event: hikari.StartingEvent):
        # Initializing the collection after the bot has started and the DB connection has been initialized
        self.collection = self.client.db.guild_config

    @lightbulb.listener(hikari.ShardReadyEvent)
    async def on_shard_ready(self, event: hikari.ShardReadyEvent):
        self.client.my_guilds = event.unavailable_guilds

    @lightbulb.listener(hikari.GuildAvailableEvent)
    async def guild_create(self, event: hikari.GuildAvailableEvent):
        # Since hikari doesn't have an event to check if the bot joined
        # a server or not, im just making my own way around it
        if event.guild_id in self.client.my_guilds:
            return
        self.client.my_guilds.append(event.guild_id)

        config = {"guildID": event.guild_id, "levelMessages": True}

        await self.collection.insert_one(config)

    @lightbulb.listener(hikari.GuildUnavailableEvent)
    async def guild_leave(self, event: hikari.GuildUnavailableEvent):
        # Whenever the bot has been removed from a server, we delete it's config
        await self.collection.find_one_and_delete({"guildID": event.guild_id})


def load(client: Ayiko):
    client.add_plugin(GuildConfig(client))
