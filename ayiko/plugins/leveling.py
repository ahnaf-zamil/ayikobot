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

from ayiko.client import Ayiko
from ayiko.utils.image import ImageUtils
from ayiko.utils.misc import human_format
from motor.motor_asyncio import AsyncIOMotorCollection
from PIL import Image
from datetime import datetime
from io import BytesIO

import typing
import lightbulb
import hikari
import asyncio
import aiohttp
import pymongo
import random
import logging


class Leveling(lightbulb.Plugin):
    def __init__(self, client: Ayiko):
        super().__init__()
        self.client: Ayiko = client
        self.logger: logging.Logger = self.client.logger
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession()
        self.collection: typing.Optional[AsyncIOMotorCollection] = None
        self.guild_collection: typing.Optional[AsyncIOMotorCollection] = None

        # Debounce/Cooldown for getting XP after each message,
        # so that users won't get XP for spamming the bot
        self.debounce: typing.List[hikari.Snowflakeish] = []

    @lightbulb.listener(hikari.StartedEvent)
    async def on_started(self, event: hikari.StartingEvent):
        # Initializing the collection after the bot has started and the DB connection has been initialized
        self.collection = self.client.db.levels
        self.guild_collection = self.client.db.guild_config

    @lightbulb.listener(hikari.StoppingEvent)
    async def on_stopping(self, event: hikari.StoppingEvent):
        # Closing the client session when bot is stopping, prevents from Unclosed client session exception
        self.logger.info("Closing client session")
        await self.session.close()

    @lightbulb.listener(hikari.GuildMessageCreateEvent)
    async def on_guild_message(self, event: hikari.GuildMessageCreateEvent):
        """Event listener for all guild messages"""

        prefix = await self.client.get_prefix(self.client, event.message)

        # Commands don't count and bots don't get XP... sad :c
        if not event.author.is_bot and not event.message.content.startswith(prefix):
            # Checking if the user is in debounce/cooldown or not
            if event.author.id not in self.debounce:
                # Giving the user XP
                await self.add_xp(
                    event.guild_id, event.author, random.randint(1, 10), event.channel
                )
                # Putting the user on cooldown
                await asyncio.create_task(self.do_debounce(event.author))

    @staticmethod
    async def get_xp_for_level(level: int):
        """Helper method to calculate required XP to hit the next level"""
        return level * level * 100

    @staticmethod
    async def calculate_level_from_xp(xp):
        """Helper method to calculate level from XP. An inverse of get_xp_for_level"""
        return (
            int((xp / 100) ** 0.5) + 1
        )  # Since I want the default level to be level 1

    @staticmethod
    async def format_xp_text(current_xp: int, last_level_xp: int, next_level_xp: int):
        if (denominator := next_level_xp - last_level_xp) > 999:
            right_side = human_format(denominator)
        else:
            right_side = denominator

        if (numerator := current_xp - last_level_xp) > 999:
            left_side = human_format(numerator)
        else:
            left_side = numerator

        return f"{left_side}/{right_side}"

    async def do_debounce(self, user: hikari.Member):
        """Basically puts a user on cooldown, waits for 5 seconds, and takes them off from cooldown"""
        self.debounce.append(user.id)
        await asyncio.sleep(5)
        self.debounce.remove(user.id)

    async def add_xp(
        self,
        guild_id: hikari.Snowflakeish,
        user: hikari.Member,
        xp_to_add: int,
        channel: hikari.GuildTextChannel,
    ):
        """Adds XP to a user"""
        await asyncio.sleep(
            1
        )  # Sleeping for 1 second so that it doesn't glitch out when a user levels up.

        user_data = await self.collection.find_one(
            {"guildID": guild_id, "userID": user.id}
        )

        if not user_data:
            await self.collection.find_one_and_update(
                {"guildID": guild_id, "userID": user.id},
                {
                    "$inc": {"xp": xp_to_add},
                    "$set": {
                        "guildID": guild_id,
                        "userID": user.id,
                    },
                },
                upsert=True,
                return_document=True,
            )
            return

        level_before = await self.calculate_level_from_xp(user_data["xp"])

        result = await self.collection.find_one_and_update(
            {"guildID": guild_id, "userID": user.id},
            {
                "$inc": {"xp": xp_to_add},
                "$set": {
                    "guildID": guild_id,
                    "userID": user.id,
                },
            },
            upsert=True,
            return_document=True,
        )

        level_after = await self.calculate_level_from_xp(result["xp"])
        guild_config = await self.guild_collection.find_one({"guildID": guild_id})

        if not guild_config:
            config = {"guildID": guild_id, "levelMessages": True}

            await self.guild_collection.insert_one(config)
            leveling_enabled = True
        else:
            leveling_enabled = guild_config["levelMessages"]

        if leveling_enabled:
            if level_after > level_before:
                await channel.send(
                    f"{user.mention} You have levelled up! Now you are level {level_after}!"
                )

    @lightbulb.command(aliases=["stats"])
    async def rank(
        self, ctx: lightbulb.Context, *, user: lightbulb.member_converter = None
    ):
        """Shows your leveling stats for this server"""
        if not user:
            user = ctx.author

        # Database query
        user_data = await self.collection.find_one(
            {"guildID": ctx.guild_id, "userID": user.id}
        )

        if not user_data:
            await ctx.respond(
                "This user has not sent a single message in the server!! >:C"
            )
            return

        # Getting the avatar
        resp = await self.session.get(str(user.format_avatar(size=128, ext="png")))
        avatar: Image = await self.loop.run_in_executor(
            None, ImageUtils.get_circle_img, await resp.read()
        )

        # Getting server icon
        resp = await self.session.get(str(ctx.guild.format_icon(size=128, ext="png")))
        icon: Image = await self.loop.run_in_executor(
            None, ImageUtils.get_circle_img, await resp.read()
        )

        # Getting the rank of the user
        members = await (
            self.collection.find({"guildID": ctx.guild_id}).sort(
                "xp", pymongo.DESCENDING
            )
        ).to_list(length=None)

        rank = None

        for i, member in enumerate(members, start=1):
            if member["userID"] == user.id:
                rank = i
                break

        if not rank:
            return await ctx.respond("You don't have a rank in this server :c")

        # Calculating math stuff
        current_xp = (
            user_data["xp"] if user.id not in self.debounce else user_data["xp"]
        )
        current_level = await self.calculate_level_from_xp(current_xp)

        # Creating XP Bar
        last_level_xp = await self.get_xp_for_level(current_level - 1)
        next_level_xp = await self.get_xp_for_level(current_level)

        # Adding the last level XP to the current XP to get a total XP,
        # since we subtract the number when the user hits a new level

        formula = (current_xp - last_level_xp) / (next_level_xp - last_level_xp)
        # Dimensions of the XP bar
        width = 373
        height = 30

        x1, y1 = 292, 125
        x2 = x1 + (width * formula)
        y2 = y1 + height
        coords = [(x1, y1), (x2, y2)]

        xp_text = await self.format_xp_text(current_xp, last_level_xp, next_level_xp)

        card = await self.loop.run_in_executor(
            None,
            ImageUtils.create_rank_card,
            avatar,
            user,
            icon,
            rank,
            current_level,
            coords,
            xp_text,
        )

        bio = BytesIO()
        card.save(bio, format="PNG")
        bio.seek(0)
        await ctx.respond(bio.read())

    @lightbulb.command(aliases=["lb"])
    async def leaderboard(self, ctx: lightbulb.Context):
        """Shows a leaderboard for the total XP of all server members"""
        users = await (
            self.collection.find(
                {"guildID": ctx.guild_id}, limit=10, sort=[("xp", pymongo.DESCENDING)]
            )
        ).to_list(length=None)

        description = ""

        for i, entry in enumerate(users, start=1):
            user: hikari.guilds.Member = self.client.cache.get_member(
                ctx.guild_id, entry["userID"]
            )
            current_level = await self.calculate_level_from_xp(entry["xp"])
            display_xp = entry["xp"] - await self.get_xp_for_level(current_level - 1)
            description += f"{i}. **{str(user)}** - **{human_format(display_xp)}** xp (Level **{current_level}**)\n"

        embed = hikari.Embed(
            title=f"Leaderboard for {ctx.guild.name}",
            color="#0394fc",
            description=description,
        )
        embed.set_footer(
            text=f"Requested by: {ctx.message.author}",
            icon=ctx.message.author.avatar_url,
        )
        embed.timestamp = datetime.now().astimezone()
        await ctx.respond(embed)


def load(client: Ayiko):
    client.add_plugin(Leveling(client))
