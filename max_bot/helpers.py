from threading import Thread

from discord import Message, Interaction, VoiceChannel, StageChannel, ForumChannel, TextChannel, CategoryChannel
from discord.abc import PrivateChannel


def get_location(subject: Message | Interaction | VoiceChannel | StageChannel | ForumChannel | TextChannel | CategoryChannel | Thread | PrivateChannel) -> tuple[str, str, str]:
    if isinstance(subject, (Message, Interaction)):
        channel = subject.channel
    else:
        channel = subject

    server_str: str = channel.guild.name.replace("/", "-")

    category_str = ""
    if category := subject.channel.category:
        category_str = category.name.replace("/", "-")

    channel_str: str = subject.channel.name

    return server_str, category_str, channel_str
