#
## Desc
A Discord bot that provides multiple functionalities, including musicplayer, game statistics retrieval(Marvel Rivals), moderation tools, database based configuration for each server, all of the mentioned functions can be disabled.

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
pip install discord python-dotenv requests pytz certifi yt-dlp
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
    - `musicplayer`: Enables or disables the music player.
    - `rivalsapi`: Enables or disables the Marvel Rivals API.
    - `lolapi`: Enables or disables the League of Legends API.
    - `moderation`: Enables or disables the moderation functions.
    - `welcome`: Enables or disables welcome messages.
    - `clear`: Enables or disables the clear command.
    - `prefixchange`: Enables or disables the command prefix change function.
    - `systemmessage`: Enables or disables the system message command.

### .env Setup
1. rename the `example.env` file to `.env`
#### Bot Token Setup:
1. Go to the [Discord Developer Portal](https://discord.com/developers/applications).
2. Create a new application and navigate to the **Bot** section.
3. Click **Add Bot**, configure its settings, and copy the **Bot Token**.
4. Store the token securely in a `.env` file:
   ```sh
   DISCORD_BOT_TOKEN=your-bot-token-here
   ```

#### Marvel Rivals API Key Setup:
1. Go to [MarvelRivalsAPI.com](https://marvelrivalsapi.com) and sign up for an API key.
2. Store the API key in the `.env` file:
   ```sh
   MARVEL_RIVALS_API_KEY=your-api-key-here
   ```

### Running the bot

1. To start the bot, activate the virtual environment and execute the following command:
```sh/cmd
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
python3 bot.py
```
Ensure your `.env` file is properly configured with the bot token and other necessary credentials.

## Acknowledgments
Marvel Rivals statistics: [MarvelRivalsAPI.com](https://marvelrivalsapi.com) by Alastor

