from ayiko.client import Ayiko
from ayiko.utils.image import ImageUtils
from motor.motor_asyncio import AsyncIOMotorCollection
from PIL import Image, ImageFont, ImageDraw
from io import BytesIO

import typing
import lightbulb
import hikari
import asyncio
import aiohttp
import pymongo


class Leveling(lightbulb.Plugin):
    def __init__(self, client: Ayiko):
        super().__init__()
        self.client: Ayiko = client
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
        self.client.logger.info("Closing client session")
        await self.session.close()

    @lightbulb.listener(hikari.GuildMessageCreateEvent)
    async def on_guild_message(self, event: hikari.GuildMessageCreateEvent):
        """Event listener for all guild messages"""

        # Bot's dont get Xp... sad :c
        if not event.author.is_bot:
            # Checking if the user is in debounce/cooldown or not
            if event.author.id not in self.debounce:
                # Giving the user XP
                await self.add_xp(event.guild_id, event.author, 15, event.channel)
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

        current_xp = user_data["xp"]
        current_level = await self.calculate_level_from_xp(current_xp)

        # Getting the avatar and pasting it
        resp = await self.session.get(str(user.format_avatar(size=128, ext="png")))
        avatar: Image = await self.loop.run_in_executor(
            None, ImageUtils.get_circle_img, await resp.read()
        )
        bg = Image.open("ayiko/resources/img/stats_bg.png")
        bg.paste(avatar, (31, 31), avatar)

        draw = ImageDraw.Draw(bg)

        # Drawing the author's username
        font = ImageFont.truetype(
            "ayiko/resources/font/Asap-SemiBold.ttf", int(450 / len(str(ctx.author)))
        )
        draw.text((210, 31), str(user), (255, 255, 255), font=font)

        # Drawing the server icon
        resp = await self.session.get(str(ctx.guild.format_icon(size=128, ext="png")))
        icon: Image = await self.loop.run_in_executor(
            None, ImageUtils.get_circle_img, await resp.read()
        )
        icon = icon.resize((50, 50), Image.ANTIALIAS)
        bg.paste(icon, (630, 35), icon)

        # Drawing the server rank
        members = await (
            self.collection.find({"guildID": ctx.guild_id}).sort(
                "xp", pymongo.DESCENDING
            )
        ).to_list(length=None)
        for i, member in enumerate(members, start=1):
            if member["userID"] == user.id:
                rank = i
                break

        font = ImageFont.truetype("ayiko/resources/font/Asap-SemiBold.ttf", 60)
        draw.text((210, 100), f"#{rank}", (164, 165, 166), font=font)

        # Drawing the level
        font = ImageFont.truetype("ayiko/resources/font/Asap-SemiBold.ttf", 30)
        draw.text((517, 42), f"Level {current_level}", "white", font=font)

        # Creating XP Bar
        last_level_xp = await self.get_xp_for_level(current_level - 1)
        next_level_xp = await self.get_xp_for_level(current_level)

        # Adding the last level XP to the current XP to get a total XP,
        # since we subtract the number when the user hits a new level

        formula = (current_xp - last_level_xp) / (next_level_xp - last_level_xp)
        color = "white"
        # Dimensions of the XP bar
        width = 373
        height = 30

        x1, y1 = 292, 125
        x2 = x1 + (width * formula)
        y2 = y1 + height

        rectangle_color = (89, 172, 255)

        rectangle_base = Image.new("RGBA", bg.size, color)
        d = ImageDraw.Draw(rectangle_base)
        d.rectangle([(x1, y1), (x2, y2)], rectangle_color)
        rectangle_base.paste(bg, (0, 0), bg)
        bg = rectangle_base

        # Drawing the XP ratio on top of XP bar
        draw = ImageDraw.Draw(bg)
        font = ImageFont.truetype("ayiko/resources/font/Asap-SemiBold.ttf", 30)
        draw.text(
            (555, 122),
            f"{current_xp - last_level_xp}/{next_level_xp - last_level_xp}",
            "black",
            font=font,
            anchor="rs",
        )

        bio = BytesIO()
        bg.save(bio, format="PNG")
        bio.seek(0)
        await ctx.respond(bio.read())


def load(client: Ayiko):
    client.add_plugin(Leveling(client))
