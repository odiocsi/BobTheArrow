import os
import time
import asyncio

from dotenv import load_dotenv

import discord
from discord.ext import commands

import music
import views

## Config
intents = discord.Intents.default()
intents.messages = True 
intents.message_content = True  
bot = commands.Bot(command_prefix=".", intents=intents)
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

## Global variables
allowed_channel_id = None
mdown = music.MusicDownloader()
playlists = {}
message_views = {}
responses = {}

## Util
class Response():
    def __init__(self):
        self.answer = -1
        self.choosing = False

async def find_existing_message(channel):
    async for msg in channel.history(limit=50):
        if msg.author == channel.guild.me and msg.components:
            return msg 
    return None

async def get_server_playlist(ctx):
    if ctx.guild.id not in playlists:
        playlists[ctx.guild.id] = music.Playlist() 
    return playlists[ctx.guild.id]

async def get_server_view(ctx, msg):
    if ctx.guild.id not in message_views:
        message_views[ctx.guild.id] = views.MusicView(ctx, msg, await get_server_playlist(ctx))
    return message_views[ctx.guild.id]

async def get_server_response(ctx):
    if ctx.guild.id not in responses:
        responses[ctx.guild.id] = Response()
    return responses[ctx.guild.id]

async def delete_message(ctx = None, msg = None, mgs = None):
    try: 
        if ctx is not None:
            await ctx.message.delete()
            if mgs is not None:
                await ctx.channel.delete_messages(mgs)
        if msg is not None:
            await msg.delete()
    except:
        print("Az üzenet törlése sikertelen.")

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
    response = await get_server_response(ctx) 
    if response.choosing:
        msg = await ctx.send("Először válaszd ki a zenét!")
        await asyncio.sleep(2)
        await delete_message(ctx, msg)
        return
    
    if ctx.voice_client is None:
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
            mgs = []
            async for msg in ctx.channel.history(limit=100):
                mgs.append(msg)
            await delete_message(ctx, None, mgs)
        else:
            msg = await ctx.send("Először lépj be egy hangcsatornába!")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

    search_results = mdown.search(query)
    if not search_results['entries']:
        await ctx.send("Nem található zene a megadott kereséssel.")
        await asyncio.sleep(2)
        await delete_message(ctx)
    playlist = await get_server_playlist(ctx)

    msg = await find_existing_message(ctx)
    if not msg:
        msg = await ctx.send("Betöltés...")
    view = await get_server_view(ctx, msg)
    await msg.edit(view=view)

    await choose_song_msg(ctx, response, view, playlist, search_results)
    bot.loop.create_task(update_view(view))

    await asyncio.sleep(2)
    await delete_message(ctx)

    while response.answer == -1:
        await asyncio.sleep(0.1)

    if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
        play_next(ctx, view, playlist)

async def choose_song_msg(ctx, response, view, playlist, search_results):
    response.choosing = True
    msg = await ctx.send("Keresés...")
    choose_view = views.ChoosingView(msg, response, search_results)
    await choose_view.edit_message()

    while response.answer == -1:
        await asyncio.sleep(0.1) 

    playlist.add(search_results['entries'][response.answer]['title'],  search_results['entries'][response.answer]['url'])

    response.choosing = False
    response.answer = -1

    if not ctx.voice_client.is_playing():
        play_next(ctx, view, playlist)
    await asyncio.sleep(1)


def play_next(ctx, view, playlist):
    if playlist.isEmpty():
        return
    
    playlist.next()
    url = playlist.current['url']
    audio_file = mdown.download(url)

    ctx.voice_client.stop()
    ctx.voice_client.play(discord.FFmpegPCMAudio(audio_file), after=lambda e: play_next(ctx, view, playlist))

async def update_view(view):
    while True:
        time.sleep(1)        
        await view.edit_message()

@bot.command()
@commands.has_permissions(administrator=True)
async def clear(ctx, number=None):
    mgs = []
    if number is None:
        number = 100
    number = int(number) 
    counter = 0
    async for msg in ctx.channel.history(limit=number):
        mgs.append(msg)
        counter += 1
    await delete_message(ctx, None, mgs)
    msg = await ctx.send(f"{counter} üzenet törölve.")
    await asyncio.sleep(5)
    await delete_message(None, msg, None)

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
