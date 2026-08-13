from typing import Literal

from discord import CategoryChannel, Interaction, TextChannel, app_commands
from discord.app_commands import Group
from discord.ext import commands
from discord.ext.commands import Bot

from ..helpers import get_response
from ..translator import Translator

ValidLanguages = Literal['en', 'et']


class LanguageCog(commands.Cog):
    def __init__(self, bot: Bot, translator: Translator):
        self.bot = bot
        self.translator = translator

    set_language_group = Group(name='set_language',
                               description='Set the language for the server, a category, or a channel.')

    def set_language(
            self,
            interaction: Interaction,
            language: ValidLanguages,
            entity_id: int,
            entity_type: str,
            **format_kwargs
    ):
        self.translator.set_language(language, **{f'{entity_type}_id': entity_id})
        t = self.translator.get_translator(interaction)
        return t(f'set_language_success_{entity_type}', language=t(language), **format_kwargs)

    @set_language_group.command(name='server', description='Set the language for the current server.')
    @app_commands.describe(language='The language to set.')
    @app_commands.guild_only
    @app_commands.checks.has_permissions(manage_guild=True)
    async def set_language_server(
            self,
            interaction: Interaction,
            language: ValidLanguages
    ):
        message = self.set_language(interaction, language, interaction.guild_id, 'server')
        await get_response(interaction).send_message(message)

    @set_language_group.command(name='category', description='Set the language for a category.')
    @app_commands.describe(language='The language to set.')
    @app_commands.describe(category='The category to set the language for.')
    @app_commands.guild_only
    @app_commands.checks.has_permissions(manage_channels=True)
    async def set_language_category(
            self,
            interaction: Interaction,
            language: ValidLanguages,
            category: CategoryChannel
    ):
        message = self.set_language(interaction, language, category.id, 'category', category=repr(category.name))
        await get_response(interaction).send_message(message)

    @set_language_group.command(name='channel', description='Set the language for a channel.')
    @app_commands.describe(language='The language to set.')
    @app_commands.describe(channel='The channel to set the language for.')
    @app_commands.guild_only
    @app_commands.checks.has_permissions(manage_channels=True)
    async def set_language_channel(
            self,
            interaction: Interaction,
            language: ValidLanguages,
            channel: TextChannel
    ):
        message = self.set_language(interaction, language, channel.id, 'channel', channel=channel.jump_url)
        await get_response(interaction).send_message(message)
