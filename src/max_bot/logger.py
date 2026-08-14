import datetime
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).parents[2]

LOGS_DIR = Path(os.getenv("LOGS_DIR") or PROJECT_ROOT / "chat_logs")


def _write(directory: Path, filename: str, header: str, log: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    line = f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " + log

    with open(directory / f"{filename}.txt", "a", encoding="utf-8") as f:
        f.write(line + "\n")

    print(header + "\n" + line)


def entry(server: str, category: str, channel: str, log: str):
    directory = LOGS_DIR / server / category if category else LOGS_DIR / server
    header = f"[{server}" + f" | {category}" * bool(category) + f" | #{channel}]"
    _write(directory, channel, header, log)


def entry_dm(user, log: str):
    _write(LOGS_DIR / "DMs", str(user), "[Direct Messages]", log)
