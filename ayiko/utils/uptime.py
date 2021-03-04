import attr
import typing


__all__: typing.Final = ["Uptime"]


@attr.s
class Uptime(object):
    days: int = attr.ib()
    hours: int = attr.ib()
    minutes: int = attr.ib()
    seconds: int = attr.ib()
