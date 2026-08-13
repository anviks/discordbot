import json

from discord import Interaction, app_commands
from discord.ext import commands
from discord.ext.commands import Bot

from ..helpers import get_location, get_response
from ..logger import entry
from ..translator import Translator


class UtilityCog(commands.Cog):
    def __init__(self, bot: Bot, translator: Translator):
        self.bot = bot
        self.translator = translator

    @app_commands.command(name='info', description='Get information about a course.')
    @app_commands.describe(course='The course to get information about.')
    async def info(self, interaction: Interaction, course: str):
        location = get_location(interaction)
        response = get_response(interaction)

        with open('resources/info_about_courses/courses.json', encoding='UTF-8') as f:
            course_info: dict = json.load(f)

        with open('resources/info_about_courses/course_to_code.json', encoding='UTF-8') as f:
            to_course_code: dict = json.load(f)

        with open('resources/info_about_courses/code_to_course.json', encoding='UTF-8') as f:
            to_course_name: dict = json.load(f)

        if course.lower() not in (key.lower for key in course_info.keys()):
            for name in to_course_code:
                if course.lower() in name.lower():
                    code = to_course_code.get(name)
                    break
            else:
                t = self.translator.get_translator(interaction)
                await response.send_message(content=t('info_command_no_such_course'), ephemeral=True)
                entry(*location,
                      f'❌  {interaction.user} wanted to see info about {course}, but I think that this course doesn\'t exist.')
                return
        else:
            code = course.upper()

        await response.send_message(content=course_info.get(code), ephemeral=True)
        entry(*location,
              f'✅  {interaction.user} read info about {to_course_name.get(code)}.')
