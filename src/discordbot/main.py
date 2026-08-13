import asyncio
import importlib
import inspect
import os
import secrets
from pathlib import Path

import discord.ext.commands
import uvicorn
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from discord import Activity, ActivityType, Intents, Interaction, app_commands
from discord.ext.commands import Bot, Cog, GroupCog
from dotenv import load_dotenv

from .cogs.fun_cog import send_pings
from .helpers import get_location, get_response
from .logger import entry
from .translator import Translator
from .types import CHANNEL_TYPES, Channel, State

COMMAND_PREFIX = "$"
WEB_DIR = Path(__file__).parents[2] / "web"
MAX_PING_COUNT = 20

load_dotenv()

token = os.getenv("DISCORD_BOT_TOKEN")
default_guild_id = int(os.getenv("DEFAULT_GUILD_ID"))
default_channel_id = int(os.getenv("DEFAULT_CHANNEL_ID"))
api_port = int(os.getenv("API_PORT", "8000"))
api_host = os.getenv("API_HOST", "0.0.0.0")
api_key = os.getenv("API_KEY")

if not api_key:
    raise RuntimeError(
        "API_KEY is not set. Refusing to start, because the control API can send messages, "
        "DMs and pings as the bot to anyone who can reach the port. Generate one with "
        "`python -c 'import secrets; print(secrets.token_urlsafe(32))'` and add it to .env."
    )

app = FastAPI()
bot = discord.ext.commands.Bot(COMMAND_PREFIX, intents=Intents.all())


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(provided: str | None = Security(api_key_header)) -> None:
    if provided is None or not secrets.compare_digest(provided, api_key):
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# Every route on this router requires the key; the static UI below deliberately does not,
# since the page has to load before it can ask for one.
api = APIRouter(prefix="/api", dependencies=[Depends(require_api_key)])

# Shared mutable state between bot and API
state: State = {"channel": None}


class MessageRequest(BaseModel):
    message: str


class PingRequest(BaseModel):
    user_id: int
    count: int = Field(1, ge=1, le=MAX_PING_COUNT)


class DmRequest(BaseModel):
    user_id: int
    message: str


class ReplyRequest(BaseModel):
    message_id: int
    content: str


def describe(channel: Channel) -> dict[str, str]:
    return {
        "id": str(channel.id),
        "name": str(channel),
        "guild": str(channel.guild) if channel.guild else "DM",
    }


@api.get("/channel")
async def get_channel():
    channel = state["channel"]
    if channel is None:
        raise HTTPException(status_code=503, detail="Bot not ready")
    return describe(channel)


@api.put("/channel/{channel_id}")
async def set_channel(channel_id: int):
    channel = bot.get_channel(channel_id)
    if channel is None:
        raise HTTPException(status_code=404, detail="Channel not found")
    if not isinstance(channel, CHANNEL_TYPES):
        # Categories and forums are channels but can't be posted to.
        raise HTTPException(
            status_code=400,
            detail=f"Cannot send messages to a {type(channel).__name__}",
        )
    state["channel"] = channel
    return describe(channel)


@api.post("/message")
async def send_message(req: MessageRequest):
    channel = state["channel"]
    if channel is None:
        raise HTTPException(status_code=503, detail="Bot not ready")
    await channel.send(req.message)
    return {"ok": True}


@api.post("/ping")
async def ping_user(req: PingRequest):
    channel = state["channel"]
    if channel is None:
        raise HTTPException(status_code=503, detail="Bot not ready")
    target = bot.get_user(req.user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    await send_pings(channel, target, req.count)
    return {"ok": True}


@api.post("/dm")
async def dm_user(req: DmRequest):
    target = bot.get_user(req.user_id)
    if target is None:
        raise HTTPException(status_code=404, detail="User not found")
    await target.send(req.message)
    return {"ok": True}


@api.post("/reply")
async def reply_message(req: ReplyRequest):
    channel = state["channel"]
    if channel is None:
        raise HTTPException(status_code=503, detail="Bot not ready")
    target_message = await channel.fetch_message(req.message_id)
    await target_message.reply(req.content)
    return {"ok": True}


app.include_router(api)
# Mounted last so it doesn't shadow /api. Serving the UI from this same app keeps it
# same-origin with the API, which is why no CORS middleware is needed.
app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")


def run_discord_bot():
    @bot.event
    async def on_ready():
        print(f"{bot.user} is now running!")

        registry = {Bot: bot, Translator: Translator()}

        cogs_dir = Path(__file__).parent / "cogs"
        for d in os.listdir(cogs_dir):
            if d.endswith(".py") and not d.startswith("__"):
                importlib.import_module(f".cogs.{d[:-3]}", __package__)

        for cls in Cog.__subclasses__():
            if cls == GroupCog:
                continue

            annotations = inspect.get_annotations(cls.__init__)
            annotations.pop("return", None)
            kwargs = {
                key: registry[value]
                for key, value in annotations.items()
                if value in registry
            }
            await bot.add_cog(cls(**kwargs))

        await bot.tree.sync()
        await bot.change_presence(
            activity=Activity(
                name="your thoughts", type=ActivityType.listening, state="🗿"
            )
        )

        default_channel = await bot.fetch_channel(default_channel_id)
        if not isinstance(default_channel, CHANNEL_TYPES):
            raise TypeError(
                f"DEFAULT_CHANNEL_ID points at a {type(default_channel).__name__}, "
                "which cannot be posted to"
            )
        state["channel"] = default_channel

    @bot.tree.error
    async def on_app_command_error(
        interaction: Interaction, error: app_commands.AppCommandError
    ):
        response = get_response(interaction)
        location = get_location(interaction)

        if isinstance(error, app_commands.errors.MissingPermissions):
            entry(
                *location,
                f"""An error occurred:
    ❌  {interaction.user} tried to execute \"{interaction.data['name']}\" but didn't have the following permissions: {', '.join(error.missing_permissions)}
    Arguments given: {interaction.data['options']}""",
            )
            await response.send_message(
                "You don't have the required permissions to use this command. Please contact an administrator.",
                ephemeral=True,
            )
        else:
            entry(
                *location,
                f"""An error occurred:
    ❌  {interaction.user} tried to execute \"{interaction.data['name']}\" but an unexpected error occurred.
    Arguments given: {interaction.data['options']}
    Error: {error}""",
            )
            await response.send_message(
                "An unexpected error occurred. Please try again later.", ephemeral=True
            )

    async def main():
        # bot.start() skips the logging setup that bot.run() does, and discord.py's
        # NullHandler means unhandled event errors are silently dropped without this.
        discord.utils.setup_logging()

        config = uvicorn.Config(app, host=api_host, port=api_port, loop="none")
        server = uvicorn.Server(config)
        await asyncio.gather(
            bot.start(token),
            server.serve(),
        )

    asyncio.run(main())


if __name__ == "__main__":
    run_discord_bot()
