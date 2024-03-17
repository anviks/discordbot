from __future__ import annotations

import json
import random

import discord.ext.commands
import requests
from aioconsole import ainput
from colorama import Fore
from discord import Message, Intents, Activity

from max_bot.resources import commands, events
from max_bot.resources.commands import send_pings

COMMAND_PREFIX = "$"
TESTING_CHANNEL_ID = 1043173920041357335


class CustomResponse:
    def __init__(self, message: str, *, is_reply: bool = False):
        self.message = message
        self.is_reply = is_reply

    def replace_placeholders(self, target_msg: Message) -> None:
        self.message = (self.message
                        .replace("&ping&", target_msg.author.mention)
                        .replace("&name&", target_msg.author.name))

    @classmethod
    def get_random_response(cls) -> CustomResponse:
        with open("max_bot/resources/replies/responses.json", encoding="utf-8") as f:
            return cls(**random.choice(json.load(f)))


async def send_response(target_msg, private: bool, response: CustomResponse = None) -> CustomResponse:
    response = response or CustomResponse.get_random_response()
    response.replace_placeholders(target_msg)

    if response.is_reply:
        await target_msg.reply(response)
    elif private:
        await target_msg.author.send(response)
    else:
        await target_msg.channel.send(response)

    return response


def run_discord_bot():
    with open("max_bot/tokens.json", encoding="utf-8") as data:
        token = json.load(data)["MAX_TOKEN"]

    intents = Intents.all()
    bot = discord.ext.commands.Bot(COMMAND_PREFIX, intents=intents)

    @bot.event
    async def on_ready():
        print(f"{bot.user} is now running!")

        await bot.load_extension(commands.__name__)
        await bot.load_extension(events.__name__)
        await bot.tree.sync()
        await bot.change_presence(activity=Activity(name="your thoughts", type=2, state="🗿"))

        img = requests.get('https://media1.tenor.com/m/bNPhV9IvmnkAAAAd/phonk-troll-face.gif').content
        await bot.user.edit(avatar=img)

        guild_names = list(map(lambda x: x.name, bot.guilds))
        guild_ids = list(map(lambda x: str(x.id), bot.guilds))

        with open("max_bot/guild_ids.json", "w", encoding="utf-8") as f:
            ids = dict(zip(guild_names, guild_ids))
            json.dump(ids, f, indent=2, ensure_ascii=False)

        with open("max_bot/guild_ids.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(guild_ids))

        with open("max_bot/guilds_info.txt", "w", encoding="utf-8") as f:
            for guild in bot.guilds:
                f.write(repr(guild) + "\n")

        await console_listener()

    async def console_listener():
        # Send messages to testing channel by default
        channel = bot.get_channel(TESTING_CHANNEL_ID)

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
