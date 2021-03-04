from ayiko.client import Ayiko

import lightbulb
import hikari


class Utility(lightbulb.Plugin):
    def __init__(self, client: Ayiko):
        super().__init__()
        self.client: Ayiko = client

    @lightbulb.command(aliases=["latency"])
    async def ping(self, ctx: lightbulb.Context):
        """Shows the bot's ping to the Discord API in milliseconds"""
        heartbeat = self.client.heartbeat_latency * 1000
        em = hikari.Embed(title="Pong!", color="#3498eb")
        em.description = f"Latency: `{int(heartbeat):,.2f}ms`\n\nThat's how late I am 🙃"
        await ctx.respond(em)


def load(client: Ayiko):
    client.add_plugin(Utility(client))
