import discord
import json
import os
from max_bot.create_log import entry
from max_bot.util.forbidden_chars import get_location


async def info(interaction: discord.Interaction, course: str):
    location = get_location(interaction)

    with open(os.getcwd() + "/max_bot/resources/info_about_courses/courses.json", encoding="UTF-8") as f:
        course_info: dict = json.load(f)

    with open(os.getcwd() + "/max_bot/resources/info_about_courses/course_to_code.json", encoding="UTF-8") as f:
        to_course_code: dict = json.load(f)

    with open(os.getcwd() + "/max_bot/resources/info_about_courses/code_to_course.json", encoding="UTF-8") as f:
        to_course_name: dict = json.load(f)

    if course.lower() not in list(map(str.lower, course_info.keys())):
        for name in to_course_code:
            if course.lower() in name.lower():
                code = to_course_code.get(name)
                break
        else:
            await interaction.response.send_message(content="Sellist kursust ma ei näe, vabandust palun.",
                                                    ephemeral=True)
            entry(*location,
                  f"XXX {interaction.user} wanted to see info about {course}, but I think that this course doesn't exist.")
            return
    else:
        code = course.upper()

    await interaction.response.send_message(content=course_info.get(code), ephemeral=True)
    entry(*location,
          f">>> {interaction.user} read info about {to_course_name.get(code)}.")
