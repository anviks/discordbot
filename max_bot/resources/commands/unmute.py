import discord

from max_bot.create_log import entry
from max_bot.util.forbidden_chars import get_location


async def unmute(interaction: discord.Interaction, user: discord.Member, reason: str = None):
    location = get_location(interaction)

    if not interaction.user.guild_permissions.manage_messages:
        entry(*location,
              f"XXX {interaction.user} tried to mute {user}"
              + f" for \"{reason}\"" * bool(reason)
              + ".")
        return

    await interaction.response.send_message(f"{user.mention} kirjutada palun mulle. Ma ootan")
    await interaction.channel.send("kas sa oled praegu siin?")
    await interaction.channel.send("Kas sa oled siin või ei?")
    await interaction.channel.send("Kas sa magab?")

    await user.edit(timed_out_until=None)

    entry(*location,
          f">>> {interaction.user} unmuted {user}"
          + f" for \"{reason}\"" * bool(reason)
          + ".")
