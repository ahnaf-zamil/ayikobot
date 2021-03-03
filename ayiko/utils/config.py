import json
import typing
import hikari
import attr


@attr.s
class BotConfig:
    """An interface of the bot's config."""

    """List of all the bot owner's snowflake IDs"""
    owner_ids: typing.List[hikari.Snowflakeish] = attr.ib()

    """The bot's prefix"""
    prefix: str = attr.ib()


def get_config(file_path: str = "config.json") -> BotConfig:
    with open(file_path) as f:
        config_json = json.load(f)

    return BotConfig(**config_json)
