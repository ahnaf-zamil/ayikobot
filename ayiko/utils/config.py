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

import json
import typing
import hikari
import attr


@attr.s
class BotConfig:
    """An interface of the bot's config."""

    owner_ids: typing.List[hikari.Snowflakeish] = attr.ib()
    """List of all the bot owner's snowflake IDs"""

    prefix: str = attr.ib()
    """The bot's prefix"""

    case_insensitive: bool = attr.ib()
    """Commands are case-insensitive"""


def get_config(file_path: str = "config.json") -> BotConfig:
    with open(file_path) as f:
        config_json = json.load(f)

    return BotConfig(**config_json)
