import discord
from max_bot.create_log import entry
from max_bot.util.forbidden_chars import get_location


async def say(interaction: discord.Interaction, message: str, replying_to: str):
    location = get_location(interaction)

    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message(":point_right: :ok_hand:", ephemeral=True)

        entry(*location,
              f"XXX {interaction.user} tried to say \"{message}\" as maxammad23.")
        return

    await interaction.response.send_message(content="Tehtud", ephemeral=True)

    if replying_to:
        replied_msg: discord.Message = await interaction.channel.fetch_message(int(replying_to))
        await replied_msg.reply(message)
    else:
        await interaction.channel.send(message)

    entry(*location,
          f"^^^ This message was ordered by {interaction.user}")
