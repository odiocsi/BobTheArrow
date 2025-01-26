import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import music

## Config

intents = discord.Intents.default()
intents.messages = True 
intents.message_content = True  
bot = commands.Bot(command_prefix=".", intents=intents)
allowed_channel_id = None

mdown = music.MusicDownloader()

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
