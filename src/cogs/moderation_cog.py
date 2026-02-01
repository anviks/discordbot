import datetime

import discord
from discord import Interaction, Member, Message, Role, app_commands
from discord.ext import commands
from discord.ext.commands import Bot

from ..helpers import get_location, get_response
from ..logger import entry
from ..translator import Translator


class ModerationCog(commands.Cog):
    def __init__(self, bot: Bot, translator: Translator):
        self.bot = bot
        self.translator = translator

    @app_commands.command(name="mute", description="Mute a user")
    @app_commands.describe(user="The user to mute.")
    @app_commands.describe(seconds="The number of seconds to mute the user.")
    @app_commands.describe(minutes="The number of minutes to mute the user.")
    @app_commands.describe(hours="The number of hours to mute the user.")
    @app_commands.describe(days="The number of days to mute the user.")
    @app_commands.describe(reason="The reason for the mute.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute_command(
            self,
            interaction: Interaction,
            user: Member,
            seconds: int = 0,
            minutes: int = 0,
            hours: int = 0,
            days: int = 0,
            reason: str = None
    ):
        location = get_location(interaction)
        response = get_response(interaction)
        t = self.translator.get_translator(interaction)

        if user.guild_permissions.administrator:
            await response.send_message(content=t('mute_command_target_admin'), ephemeral=True)
            entry(*location,
                  f"❌  {interaction.user} tried to mute {user} (ADMIN)"
                  + f" for \"{reason}\"" * bool(reason)
                  + ".")
            return

        muted_until = discord.utils.utcnow()

        if seconds or minutes or hours or days:
            muted_until += datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
            await user.edit(timed_out_until=muted_until)
        else:
            await user.edit(timed_out_until=None)

        muted_until_str = muted_until.strftime("%d.%m.%Y %H:%M:%S (UTC)")

        if not reason:
            content = t('mute_command_success_no_reason', target=user.mention, until=muted_until_str)
        else:
            content = t('mute_command_success', target=user.mention, until=muted_until_str, reason=reason)

        await response.send_message(content=content, ephemeral=True)

        entry(*location,
              f"✅  {interaction.user} muted {user}"
              + f" for \"{reason}\"" * bool(reason)
              + f" for the duration of"
              + f" {days} days, {hours} hours, {minutes} minutes and {seconds} seconds.")

    @app_commands.command(name="unmute", description="Unmute a user")
    @app_commands.describe(user="The user to unmute.")
    @app_commands.describe(reason="The reason for the unmute.")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: Interaction, user: Member, reason: str = None):
        location = get_location(interaction)
        t = self.translator.get_translator(interaction)
        await get_response(interaction).send_message(t('unmute_command_success', target=user.mention), ephemeral=True)
        await user.edit(timed_out_until=None)

        entry(*location,
              f"✅  {interaction.user} unmuted {user}"
              + f" because \"{reason}\"" * bool(reason)
              + ".")

    @app_commands.command(name="poll_remind",
                          description="Ping every channel member with the specified role, who hasn't reacted to the specified message.")
    @app_commands.describe(role="The role to ping.")
    @app_commands.describe(message_id="The ID of the message to check.")
    @app_commands.checks.has_permissions(administrator=True)
    async def poll_remind(self, interaction: Interaction, role: Role, message_id: str):
        channel_members = set(interaction.channel.members)
        members = {m for m in role.members if m in channel_members and not m.bot}
        msg: Message = await interaction.channel.fetch_message(int(message_id))
        reactions = msg.reactions
        reactors = {react.users() for react in reactions}
        reactors = {user_ for a_iter in reactors async for user_ in a_iter}

        pings = ""

        for person in members - reactors:
            if person == msg.author:
                continue
            pings += person.mention

        t = self.translator.get_translator(interaction)

        if pings:
            response = t('poll_remind_command_success', pings=pings)
            await msg.reply(pings)
        else:
            response = t('poll_remind_command_no_pings')

        await get_response(interaction).send_message(response, ephemeral=True)

        location = get_location(interaction)
        entry(*location,
              f"✅  {interaction.user} pinged everyone, who hasn't reacted to a message with an id of {message_id}")
