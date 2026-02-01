from functools import wraps
from threading import Thread

from discord import Interaction, InteractionResponse, Message
from discord.abc import GuildChannel, PrivateChannel


def get_response(interaction: Interaction) -> InteractionResponse:
    return interaction.response  # type: ignore


def get_location(subject: Message | Interaction | GuildChannel | Thread | PrivateChannel) -> tuple[str, str, str]:
    if isinstance(subject, (Message, Interaction)):
        channel = subject.channel
    else:
        channel = subject

    server_str: str = channel.guild.name.replace("/", "-").replace("\\", "-")

    category_str = ""
    if category := subject.channel.category:
        category_str = category.name.replace("/", "-").replace("\\", "-")

    channel_str: str = subject.channel.name

    return server_str, category_str, channel_str


class cache:
    storage = {}

    def __new__(cls, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (func, args, frozenset(kwargs.items()))
            if key in cls.storage:
                return cls.storage[key]
            cls.storage[key] = func(*args, **kwargs)
            return cls.storage[key]

        return wrapper

    @classmethod
    def clears(cls, function):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.storage = {key: value for key, value in cls.storage.items() if key[0] != function.__wrapped__}
                return func(*args, **kwargs)

            return wrapper

        return decorator
