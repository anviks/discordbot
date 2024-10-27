import importlib
import inspect
import os

import discord.ext.commands
from aioconsole import ainput
from colorama import Fore
from discord import Activity, ActivityType, Intents
from discord.ext.commands import Bot, Cog, GroupCog
from dotenv import load_dotenv

from .cogs.fun_cog import send_pings
from .translator import Translator

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

        registry = {Bot: bot, Translator: Translator()}

        for d in os.listdir('src/cogs'):
            if d.endswith('.py'):
                importlib.import_module('src.cogs.' + d[:-3])

        for cls in Cog.__subclasses__():
            if cls == GroupCog:
                continue

            annotations = inspect.get_annotations(cls.__init__)
            annotations.pop('return', None)
            kwargs = {key: registry[value] for key, value in annotations.items() if value in registry}
            await bot.add_cog(cls(**kwargs))

        await bot.tree.sync()
        await bot.change_presence(activity=Activity(name="your thoughts", type=ActivityType.listening, state="🗿"))

        await console_listener()

    async def console_listener():
        # Send messages to testing channel by default
        channel = bot.get_channel(default_channel_id)

        while True:
            message: str = await ainput()

            if not message:
                continue

            if not message.startswith(COMMAND_PREFIX):
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
            elif command_name == 'reply':
                target_message = await channel.fetch_message(int(args[0]))
                await target_message.reply(' '.join(args[1:]))
            else:
                print("Unrecognised command: " + command_name)

    bot.run(token)
