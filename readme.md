# BobTheArrow
## Desc
BobTheArrow is a fully modular multi purpose discord bot.
## Features
- Music Player
- Game statistics retrieval (Marvel Rivals, League of Legends)
- Server moderation tools
- Command based configuration for each server

## Usage

### Dependencies
- python3
- pip
- ffmpeg
- Python packages:
    - discord
    - python-dotenv
    - requests
    - pytz
    - certifi
    - yt-dlp

### Installation
#### Python and pip:
Install Python 3 and pip depending on your OS:
- **Windows:** Download and install from [Python.org](https://www.python.org/downloads/), ensure `pip` is installed.
- **Linux:** Install via package manager:
  ```sh/cmd
  sudo apt update && sudo apt install python3 python3-pip
  ```

Ensure `pip` is updated:
```sh/cmd
python3 -m ensurepip --default-pip
python3 -m pip install --upgrade pip
```

#### ffmpeg:
Install `ffmpeg` depending on your OS:
- **Windows:** Download and install from [FFmpeg.org](https://ffmpeg.org/download.html)
- **Linux:** Install using apt:
  ```sh/cmd
  sudo apt update && sudo apt install ffmpeg
  ```

#### Virtual Environment Setup:
It is recommended to create a virtual environment before installing dependencies:
```sh/cmd
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

#### Python packages:
Once inside the virtual environment, install the required Python packages using `pip`:
```sh/cmd
pip install -r requirements.txt
```

### Config
Configuration settings are stored in the `config.py` file

- **DBDefaults:**
    - `default_lang`: Sets the default language the bot uses for each server.
    - `default_command_prefix`: Sets the default command prefix the bot uses for each server.
- **Paths:**
    - `download_path`: The path of the folder where the bot downloads the music.
    - `database_path`: The path of the JSON file containing the database.
- **Components:**
    - `setlang`: Enables or disables to change the language of the bot through a command.
    - `musicplayer`: Enables or disables the music player.
    - `rivalsapi`: Enables or disables the Marvel Rivals API.
    - `lolapi`: Enables or disables the League of Legends API.
    - `wfapi`: Enables or disables the Warframe API.
    - `membercount`: Enables or disables the membercount function.
    - `moderation`: Enables or disables the moderation functions.
    - `welcome`: Enables or disables welcome messages.
    - `clear`: Enables or disables the clear command.
    - `prefixchange`: Enables or disables the command prefix change function.
    - `systemmessage`: Enables or disables the system message command.
    - `serverstats`: Enables or disables the Server statistics function.

### .env and Database Setup
1. rename the `database-empty.json` file to `database.json`
2. rename the `example.env` file to `.env`
#### Bot Token Setup:
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application and navigate to the **Bot** section.
3. Click **Add Bot**, configure its settings, and copy the **Bot Token**.
4. Store the token securely in a `.env` file:
   ```.env
   DISCORD_TOKEN=your-bot-token-here
   ```

#### Marvel Rivals API Key Setup:
1. Go to [MarvelRivalsAPI.com](https://marvelrivalsapi.com) and sign up for an API key.
2. Store the API key in the `.env` file:
   ```.env
   RIVALS_API_KEY=your-api-key-here
   ```

#### League of Legends API Key Setup:
1. Go to [Riot Games Developer Portal](https://developer.riotgames.com) and sign up for an API key.
2. Store the API key in the `.env` file:
   ```.env
   LOL_API_KEY=your-api-key-here

#### Warfame API Key Setup:
1. The Warframe API needs no key.

#### Serverstats API Setup:
1. Get the Guild ID of your discord server:
    1. Enable Developer Mode in Discord:
       - Open **User Settings** → **Advanced** → Enable **Developer Mode**.
    2. Right-click your Discord server icon and click **"Copy Server ID"**.
2. Make a script like the one below on your game server that sends the player count to the API every XY seconds (the maximum is 10 requests every 60 sec).
    ```example.py
        import requests

        params = {
            "server_id": <(your servers guild id)>,
            "server_name": "example",
            "max_players": 100,
            "current_players": 1,
            "image": "https://example.com/example.png"
        }

        response = requests.post("http://127.0.0.1:5000/gameserver/update", params=params)

### Running the bot

1. To start the bot, activate the virtual environment and execute the following command:
```sh/cmd
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
python3 bot.py
```
Ensure your `.env` file is properly configured with the bot token and other necessary credentials.

## Acknowledgments
Marvel Rivals statistics: [MarvelRivalsAPI](https://marvelrivalsapi.com)   
Warframe information: [WarframeStatus API](https://docs.warframestat.us)

## Support
If you encounter any issues, feel free to open an issue here on GitHub or contact me on Discord.   
Discord: `lightning7510`
