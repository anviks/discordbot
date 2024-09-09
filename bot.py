from __future__ import annotations

import json
import os
import discord.ext.commands
import requests
from aioconsole import ainput
from colorama import Fore
from discord import Intents, Activity
from dotenv import load_dotenv

from resources import commands, events
from resources.commands import send_pings

COMMAND_PREFIX = "$"

load_dotenv()

current_directory = os.path.dirname(__file__)
token = os.getenv('DISCORD_BOT_TOKEN')
default_channel_id = int(os.getenv('DEFAULT_CHANNEL_ID'))


def run_discord_bot():
    intents = Intents.all()
    bot = discord.ext.commands.Bot(COMMAND_PREFIX, intents=intents)

    @bot.event
    async def on_ready():
        print(f"{bot.user} is now running!")

        # img = requests.get('https://media1.tenor.com/m/bNPhV9IvmnkAAAAd/phonk-troll-face.gif').content
        # img = requests.get(bot.application.icon.url).content
        # await bot.user.edit(avatar=img)

        await bot.load_extension(commands.__name__)
        await bot.load_extension(events.__name__)
        await bot.tree.sync(guild=discord.Object(1043173920041357332))
        await bot.tree.sync()
        await bot.change_presence(activity=Activity(name="your thoughts", type=2, state="🗿"))

        guild_names = list(map(lambda x: x.name, bot.guilds))
        guild_ids = list(map(lambda x: str(x.id), bot.guilds))

        with open(f"{current_directory}/guild_ids.json", "w", encoding="utf-8") as f:
            ids = dict(zip(guild_names, guild_ids))
            json.dump(ids, f, indent=2, ensure_ascii=False)

        with open(f"{current_directory}/guild_ids.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(guild_ids))

        with open(f"{current_directory}/guilds_info.txt", "w", encoding="utf-8") as f:
            for guild in bot.guilds:
                f.write(repr(guild) + "\n")

        await console_listener()

    async def console_listener():
        # Send messages to testing channel by default
        channel = bot.get_channel(default_channel_id)

        while True:
            message = await ainput()

            if not message:
                continue

            if message[0] != COMMAND_PREFIX:
                await channel.send(message)
                continue

            command, *args = message.split()
            command_name = command[1:]

            if command_name == 'cd':
                if not args:
                    print(Fore.GREEN + f'✅ Currently talking in {channel.guild} > #{channel} ✅' + Fore.RESET)
                else:
                    channel = bot.get_channel(int(args[0]))
                    print(Fore.GREEN + f'✅ Now talking in {channel.guild} > #{channel} ✅' + Fore.RESET)
            elif command_name == 'ping':
                target = bot.get_user(int(args[0]))
                count = int(args[1]) if len(args) > 1 else 1
                print(Fore.YELLOW + f'⏳ Pinging {target} {count} times... ⏳' + Fore.RESET)
                await send_pings(channel, target, count)
                print(Fore.GREEN + f'✅ Done! ✅' + Fore.RESET)
            elif command_name == 'dm':
                target = bot.get_user(int(args[0]))
                await target.send(' '.join(args[1:]))
            else:
                print("Unrecognised command: " + command_name)

    bot.run(token)
