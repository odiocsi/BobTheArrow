import os
import time
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
mplay = music.Playlist()
view = None
message = None

class MusicView(View):
    def __init__(self, ctx, message, pl):
        super().__init__(timeout=None)
        self.__ctx = ctx
        self.__message = message
        self.__isPaused = False
        self.__mplay = pl
        self.__loopstatus = ""

        self.__plpa_button = Button(style=discord.ButtonStyle.primary, label="⏯️")
        self.__plpa_button.callback = self.__plpa
        self.__shuff_button = Button(style=discord.ButtonStyle.primary, label="🔀")
        self.__shuff_button.callback = self.__shuffle
        self.__skip_button = Button(style=discord.ButtonStyle.primary, label="⏩")
        self.__skip_button.callback = self.__skip
        self.__loop_button = Button(style=discord.ButtonStyle.primary, label="🔁")
        self.__loop_button.callback = self.__loop

        self.__add_buttons()

    async def __plpa(self, interaction):
        await interaction.response.defer()
        if self.__ctx.voice_client.is_playing():
            self.__ctx.voice_client.pause()
        else:
            self.__ctx.voice_client.resume()
        self.__isPaused = not self.__isPaused

    async def __skip(self, interaction):
        await interaction.response.defer()
        if self.__ctx and self.__ctx.voice_client.is_playing():
            self.__ctx.voice_client.stop()
            play_next(self.__ctx, self)

    async def __shuffle(self, interaction):
        await interaction.response.defer()
        self.__mplay.shuffle()

    async def __loop(self, interaction):
        await interaction.response.defer()
        self.__loopstatus = self.__mplay.loop()

    def __add_buttons(self):
        self.clear_items()
        self.add_item(self.__plpa_button)
        if not self.__mplay.isEmpty():
            self.add_item(self.__shuff_button)
            self.add_item(self.__skip_button)
        self.add_item(self.__loop_button)

    async def edit_message(self):
        new_message = ""
        if self.__mplay.isEmpty() and not self.__ctx.voice_client.is_playing() and not self.__isPaused:
            new_message = "Státusz: Jelenleg nem megy zene."
        else:
            if self.__isPaused:
                new_message = f"Státusz: ⏸️{self.__loopstatus}\n\n"
            else:
                new_message = f"Státusz: ▶️{self.__loopstatus}\n\n"

            if self.__mplay.current:
                new_message += f"Jelenlegi zene: {self.__mplay.current['title']}"
            else:
                new_message += "Jelenlegi zene: Nincs"
            new_message += f"\n\n "+self.__mplay.tostring()

        self.__add_buttons()
        await self.__message.edit(content=new_message, view=self)
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

@bot.command()
async def play(ctx, *, query: str):
    global view, message
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

    if view is None:
        message = await ctx.send("Betöltés...")
        view = MusicView(ctx, message, mplay)
        await message.edit(view=view)

    mplay.add(search_results['entries'][0]['title'], search_results['entries'][0]['url'])

    if not ctx.voice_client.is_playing():
        play_next(ctx, view)
        await loop()

def play_next(ctx, view):
    if mplay.isEmpty():
        return
    mplay.next()
    url = mplay.current['url']
    audio_file = mdown.download(url)
    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(audio_file), after=lambda e: play_next(ctx, view))

async def loop():
    while True:
        time.sleep(0.250)        
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
