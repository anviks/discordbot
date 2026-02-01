import datetime
import os

LOGS_DIR = 'chat_logs'


def entry(server: str, category: str, channel: str, log: str):
    if not os.path.exists(f"{LOGS_DIR}/{server}" + f"/{category}" * bool(category)):
        os.makedirs(f"{LOGS_DIR}/{server}" + f"/{category}" * bool(category))

    with open(f"{LOGS_DIR}/{server}" + f"/{category}" * bool(category) + f"/{channel}.txt", "a",
              encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " + log + "\n")

    print(f"[{server}" + f" | {category}" * bool(category) + f" | #{channel}]"
          + f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " + log)


def entry_dm(user, log: str):
    if not os.path.exists(f"{LOGS_DIR}/DMs"):
        os.makedirs(f"{LOGS_DIR}/DMs")

    with open(f"{LOGS_DIR}/DMs/{user}.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " + log + "\n")

    print(f"[Direct Messages]"
          + f"\n[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " + log)
