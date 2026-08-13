import discord
from discord import Attachment, CategoryChannel, ForumChannel, Interaction, Member, Message, PartialMessageable, \
    StageChannel, TextChannel, Thread, User, VoiceChannel, app_commands
from discord.ext import commands
from discord.ext.commands import Bot

from ..helpers import get_location, get_response
from ..logger import entry, entry_dm
from ..translator import Translator

InteractionChannel = VoiceChannel | StageChannel | TextChannel | ForumChannel | CategoryChannel | Thread | PartialMessageable


async def send_pings(channel: InteractionChannel, target: User | Member, count: int):
    for i in range(count):
        await channel.send(target.mention, delete_after=0)


async def is_owner(interaction: discord.Interaction) -> bool:
    return interaction.user.id == interaction.client.owner_id


class FunCog(commands.Cog):
    def __init__(self, bot: Bot, translator: Translator):
        self.bot = bot
        self.translator = translator

    @app_commands.command(name='ping', description='Ping a user.')
    @app_commands.describe(target='The user to ping.')
    @app_commands.describe(count='The number of times to ping.')
    @app_commands.check(is_owner)
    async def ping(self, interaction: Interaction, target: Member, count: int = 1):
        channel: InteractionChannel = interaction.channel
        location = get_location(interaction)
        response = get_response(interaction)
        t = self.translator.get_translator(interaction)

        await response.send_message(content=t('ping_command_success', count, target=target.mention, count=count),
                                    ephemeral=True)
        entry(*location, f'✅  {interaction.user} pinged {target} {count} times.')

        await send_pings(channel, target, count)

    @app_commands.command(name='say', description='Say something as the bot.')
    @app_commands.describe(message='The message to say.')
    @app_commands.describe(replying_to='The ID of the message to reply to.')
    @app_commands.checks.has_permissions(administrator=True)
    async def say(self, interaction: Interaction, message: str = '​', replying_to: str = None):
        t = self.translator.get_translator(interaction)
        response = get_response(interaction)

        if interaction.guild:
            location = get_location(interaction)
            log_func = entry
        else:
            location = [interaction.user]
            log_func = entry_dm

        await response.send_message(content=t('say_command_success'), ephemeral=True)

        if replying_to:
            replied_msg: Message = await interaction.channel.fetch_message(int(replying_to))
            await replied_msg.reply(message)
        else:
            await interaction.channel.send(message)

        log_func(*location, f'{interaction.user} ordered me to say "{message}".')

    @app_commands.command(name="dm", description="DM someone")
    @app_commands.describe(target="The user to DM.")
    @app_commands.describe(message="The message to send.")
    @app_commands.describe(attachment="The attachment to add to the message")
    @app_commands.checks.has_permissions(administrator=True)
    async def dm(self, interaction: Interaction, target: User, message: str = '​', attachment: Attachment = None):
        if attachment is None:
            await target.send(message)
        else:
            file = await attachment.to_file()
            await target.send(message, file=file)
            message += ' ' + attachment.url

        t = self.translator.get_translator(interaction)
        await get_response(interaction).send_message(t('dm_command_success', target=target.mention), ephemeral=True)
        entry(*get_location(interaction), f'{interaction.user} ordered me to DM {target} "{message}"')
