import asyncio
import random

import yaml
from discord import Member, Message, User
from discord.ext import commands
from discord.ext.commands import Bot


class CustomResponse:
    def __init__(self, message: str, *, is_reply: bool = False):
        self.message = message
        self.is_reply = is_reply

    def replace_placeholders(self, target: User | Member) -> None:
        self.message = (self.message
                        .replace('&ping&', target.mention)
                        .replace('&name&', target.name))

    @classmethod
    def get_random_response(cls) -> 'CustomResponse':
        with open('resources/responses.yaml', encoding='utf-8') as f:
            return cls(**random.choice(yaml.safe_load(f)))


class ResponseCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_send_random_response(self, trigger_msg: Message):
        response = CustomResponse.get_random_response()
        response.replace_placeholders(trigger_msg.author)

        async with trigger_msg.channel.typing():
            await asyncio.sleep(1)

        if response.is_reply:
            await trigger_msg.reply(response.message)
        else:
            await trigger_msg.channel.send(response.message)
