import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import music
from discord.ui import Button, View

## Config

intents = discord.Intents.default()
intents.messages = True 
intents.message_content = True  
bot = commands.Bot(command_prefix=".", intents=intents)
allowed_channel_id = None

mdown = music.MusicDownloader()
playlist = []

@bot.event
async def on_ready():
    print('A bot elindult.')

## Parancsok
@bot.command()
async def test(ctx):
    await ctx.send("Hello World!")

@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send("Először lépj be egy hangcsatornába!")

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send("Nem vagyok egy hangcsatornában sem!")

class MusicView(View):
    def __init__(self, ctx, message):
        super().__init__()
        self.ctx = ctx
        self.message = message
        self.isPaused = 0

        self.plpa_button = Button(style=discord.ButtonStyle.primary, label="⏯️")
        self.plpa_button.callback = self.plpa

    async def plpa(self, interaction):
        await interaction.response.defer()
        if self.ctx.voice_client.is_playing():
            self.ctx.voice_client.pause()
            self.isPaused = 1
        else:
            self.ctx.voice_client.resume()
            self.isPaused = 0
        await self.edit_message()

    async def add_buttons(self):
        self.clear_items()
        self.add_item(self.plpa_button)

    async def edit_message(self):
        new_message = ""
        if not playlist:
            new_message = "Jelenleg nem megy zene."
        else:
            if self.isPaused:
                new_message = "⏸️ "
            else:
                new_message = "▶️ "

            if len(playlist) > 1:
                new_message += f"Jelenlegi zene: {playlist[0]['title']}"
                for i in range(1, len(playlist)):
                    new_message += f"\nKövetkező zene: {playlist[i]['title']}"
            else:
                new_message += f"Jelenlegi zene: {playlist[0]['title']} \n \n Nincsen következő zene"

        await self.add_buttons()
        await self.message.edit(content=new_message, view=self)


@bot.command()
async def play(ctx, *, query: str):
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send("Először lépj be egy hangcsatornába!")
            return

    search_results = mdown.search(query)
    if not search_results['entries']:
        await ctx.send("Nem található zene a megadott kereséssel.")
        return

    message = await ctx.send("Betöltés...")
    view = MusicView(ctx, message)
    await message.edit(view=view)

    url = search_results['entries'][0]['url']
    audio_file = mdown.download(url)
    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(audio_file))

    playlist.append({'title': search_results['entries'][0]['title']})
    await view.edit_message()

@bot.command()
@commands.has_permissions(administrator=True)
async def set_channel(ctx, channel: discord.TextChannel):
    global allowed_channel_id
    allowed_channel_id = channel.id 
    await ctx.send(f"A bot mostantól csak a következő csatornát látja: {channel.mention}")

@bot.command()
@commands.has_permissions(administrator=True)
async def clear_channel(ctx):
    global allowed_channel_id
    allowed_channel_id = None
    await ctx.send("A bot mostantól látja az összes csatornát.")

@bot.event
async def on_message(message):
    global allowed_channel_id

    if message.author == bot.user:
        return

    if allowed_channel_id is not None and message.channel.id != allowed_channel_id:
        return

    await bot.process_commands(message)

## Bot init
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("Hiányzik a token.")
    
try:
    bot.run(TOKEN)
except Exception as e:
    print(f"Hiba történt: {e}")
