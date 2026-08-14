from discord import Member, Message, Reaction, User
from discord.ext import commands
from discord.ext.commands import Bot


class GeneralEventsCog(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author == self.bot.user:
            return

        if self.bot.user.mentioned_in(message):
            self.bot.dispatch('send_random_response', message)
            return

        await self.bot.process_commands(message)

    async def should_mirror(self, reaction: Reaction, user: Member | User) -> bool:
        return (reaction.is_custom_emoji() and reaction.emoji.name in ('max', 'maximilian')
                or await self.bot.is_owner(user))

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: Reaction, user: Member | User):
        if await self.should_mirror(reaction, user):
            await reaction.message.add_reaction(reaction.emoji)

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: Reaction, user: Member | User):
        if await self.should_mirror(reaction, user):
            await reaction.remove(self.bot.user)
