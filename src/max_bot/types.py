from typing import TypedDict

from discord import DMChannel, StageChannel, TextChannel, Thread, VoiceChannel

type Channel = TextChannel | VoiceChannel | StageChannel | Thread | DMChannel

# Runtime counterpart to Channel, keep in sync with the alias above.
CHANNEL_TYPES = (TextChannel, VoiceChannel, StageChannel, Thread, DMChannel)


class State(TypedDict):
    channel: Channel | None
