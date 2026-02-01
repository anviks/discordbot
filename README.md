# Discord Bot

This project is a Discord bot built using Python and the `discord.py` library.
The bot includes several commands and functionalities to interact with users on a Discord server.

## Features

- **Fun commands**: `/ping`, `/say`, and `/dm`.
- **Utility commands**: `/info`.
- **Moderation commands**: `/mute`, `/unmute`, and `/poll_remind`.
- **Custom Responses**: Sends a random custom responses, when it's mentioned in a message.
- **Language Support**: Supports responses in Estonian and English. Language preferences can be set for the server,
  a category, or a channel, using the `/set_language` command group.

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Commands](#commands)
- [License](#license)

## Requirements

- Python 3.10+
- gettext: This package includes the `msgfmt` tool, which is used for compiling `.po` files into `.mo` files for
  translations. To install it:
    - Windows: `winget install GnuWin32.gettext`
    - Linux: `sudo apt-get install gettext`
    - MacOS: `brew install gettext`
- Libraries from `requirements.txt`

## Installation

1. Clone the repository:
    ```shell
    git clone https://github.com/anviks/discordbot.git
    cd discordbot
    ```

2. Create a virtual environment (optional):
    - Windows:
        ```powershell
        py -m venv .venv
        .venv\Scripts\activate
        ```
    - Linux/MacOS:
        ```shell
        python3 -m venv .venv
        source .venv/bin/activate
        ```

3. Install the required packages:
    ```shell
    pip install -r requirements.txt
    ```

4. Provide the necessary environment variables:
   For that create at least one of the following files in the root directory:
    - `.env.development` (for development)
    - `.env.production` (for production)

   Bot run scripts will automatically copy the content of the appropriate file to the `.env` file.

   Add the following environment variables to the file:
    ```dotenv
    DISCORD_BOT_TOKEN=your_discord_bot_token
    DEFAULT_CHANNEL_ID=your_default_channel_id
    SQLITE_DB_PATH=your_sqlite_db_path
    ```

5. Create a `.sqlite` database file by any means and provide the path to the database file in the `SQLITE_DB_PATH`
   environment variable. After that, run the table creation script in `scripts/init_db.sql` to create the necessary
   table(s).

6. Run the bot by executing:
    - `scripts\run.ps1 dev` for development (Windows)
    - `scripts\run.ps1 prod` for production (Windows)
    - `scripts/run.sh dev` for development (Linux/MacOS)
    - `scripts/run.sh prod` for production (Linux/MacOS)

## Commands

- `/ping <target> [count=1]`  
  Ping the specified user a number of times (default is 1).

- `/say [message=ZWSP] [replying_to_message_id]`  
  Make the bot send a message (default is zero-width space) in the channel.
  Optionally, reply to a message by providing its ID.

- `/dm <target> [message=ZWSP] [attachment]`  
  Send a direct message to the specified user. Optionally, include an attachment.

- `/info <course>`  
  Get information about a TalTech course.

- `/mute <user> [seconds=0] [minutes=0] [hours=0] [days=0] [reason]`  
  Mute a user for a duration.

- `/unmute <user> [reason]`  
  Unmute a user.

- `/poll_remind <role> <message_id>`  
  Pings every channel member with a specified role who hasn't reacted to a specified message.

- `/set_language server|category|channel <language> [category|channel]`  
  Sets the language for the server, a category, or a channel.

## License

### GNU Affero General Public License

This project is licensed under the GNU Affero General Public License. See the [LICENSE](LICENCE) file for details.

### Key Points

- You are free to run, modify, and share this software.
- If you modify this software and distribute it, you must distribute the source code of your modifications under the same license.
- If you run this software on a server, you must make the source code available to your users.
