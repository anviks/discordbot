from discord import Message, Interaction


def get_location(subject: [Message | Interaction]) -> (str, str, str):
    server = subject.guild.name.replace("/", "-")

    if category := subject.channel.category:
        category = category.name.replace("/", "-")
    else:
        category = ""
    channel = subject.channel.name

    return server, category, channel
