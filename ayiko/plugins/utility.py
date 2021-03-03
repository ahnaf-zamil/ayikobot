from ayiko.client import Ayiko

import lightbulb
import hikari


class Utility(lightbulb.Plugin):
    def __init__(self, bot: Ayiko):
        super().__init__()
        self.bot: Ayiko = bot

    @lightbulb.command(aliases=["latency"])
    async def ping(self, ctx: lightbulb.Context):
        """Shows the bot's ping to the Discord API in milliseconds"""
        heartbeat = self.bot.heartbeat_latency * 1000
        em = hikari.Embed(title="Pong!", color="#3498eb")
        em.description = f"Latency: `{int(heartbeat):,.2f}ms`\n\nThat's how late I am 🙃"
        await ctx.respond(em)


def load(bot: Ayiko):
    bot.add_plugin(Utility(bot))
