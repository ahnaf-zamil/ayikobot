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
