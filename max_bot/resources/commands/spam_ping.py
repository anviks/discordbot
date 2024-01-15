import random

from discord import *

from max_bot.create_log import entry
from max_bot.delete_log import delete
from max_bot.util.forbidden_chars import get_location


async def ping(interaction: Interaction, target: Member, count: int | None):
    if count is None:
        count = random.randint(5, 10)

    location = get_location(interaction)

    if not interaction.user.guild_permissions.manage_messages or str(interaction.user) != "buffer_overflow#0":
        await interaction.response.send_message(":point_right: :ok_hand:", ephemeral=True)

        entry(*location,
              f"XXX {interaction.user} tried to ping {target} {count} times.")
        return

    await interaction.response.send_message(content=f"Olgu, pingin {target} {count} korda.", ephemeral=True)
    entry(*location,
          f">>> {interaction.user} pinged {target} {count} times.")

    for i in range(count):
        sent_message = await interaction.channel.send(target.mention)
        await sent_message.delete()
        delete(sent_message)



