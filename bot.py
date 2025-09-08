import os
import time
import asyncio
import signal
import json
import requests
from dotenv import load_dotenv

import discord
from discord.ext import tasks, commands

import config
from locales import languages
from classes.apis import marvelrivals
from classes.apis import lol
from classes.apis import warframe as wf
from classes import music
from classes import views
from classes.shared import database, json_path

from threading import Thread
from classes.apis.serverstatistics import app as gameserver_api

## Config
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

def get_locale(guild_id):
    lang = database[str(guild_id)]["lang"]
    return languages.get_dict(lang)

async def get_prefix(bot, message):
    guild = message.guild
    ensure_db_structure(str(guild.id))
    return database[str(guild.id)]['prefix']

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=views.CustomHelpCommand())

## Global variables
mdown = music.MusicDownloader()
playlists = {}
message_views = {}
responses = {}
awaited_delete = False

## Utility
class Response():
    def __init__(self):
        self.answer = -1
        self.choosing = False
        self.event = asyncio.Event()

async def find_existing_message(channel, message_id, limit=100):
    try:
        message_id = int(message_id)
    except:
        return None

    async for message in channel.history(limit=limit):
        if message.id == message_id:
            return message
    return None


async def get_server_playlist(ctx):
    if ctx.guild.id not in playlists:
        playlists[ctx.guild.id] = music.Playlist(get_locale(ctx.guild.id))
    return playlists[ctx.guild.id]

async def get_server_view(ctx, msg):
    if ctx.guild.id not in message_views:
        message_views[ctx.guild.id] = views.MusicView(ctx, msg, await get_server_playlist(ctx), ctx.guild)
    return message_views[ctx.guild.id]

async def get_server_response(ctx):
    if ctx.guild.id not in responses:
        responses[ctx.guild.id] = Response()
    return responses[ctx.guild.id]

async def choose_song_msg(ctx, response, view, playlist, search_results):
    locale = get_locale(ctx.guild.id)
    msg = await ctx.send(locale.searching)
    embed = discord.Embed(title=locale.results, color=0xFF0000)
    embed.add_field(name=locale.status, value=locale.searching, inline=False)
    await asyncio.sleep(0.51)
    await msg.edit(content=None, embed=embed)
    response.choosing = True

    choose_view = views.ChoosingView(msg, response, search_results, ctx.guild)
    await choose_view.edit_message()

    asyncio.create_task(choose_song_automatically(response))
    await response.event.wait()

    playlist.add(search_results['entries'][response.answer]['title'],  search_results['entries'][response.answer]['url'])

    response.choosing = False
    response.answer = -1
    response.event.clear()

    await delete_message(None, msg)
    if not ctx.voice_client.is_playing():
        play_next(ctx, view, playlist)

async def choose_song_automatically(response):
    await asyncio.sleep(10)
    if response.choosing:
        response.choosing = False
        response.answer = 0
        response.event.set()

def play_next(ctx, view, playlist):
    if playlist.isEmpty() and not playlist.getLoop() == "one" or not ctx.voice_client:
        return
    ctx.voice_client.stop()


    playlist.next()
    url = playlist.current['url']
    audio_file = mdown.get_stream_url(url)

    ctx.voice_client.play(discord.FFmpegPCMAudio(audio_file), after=lambda e: play_next(ctx, view, playlist))

@tasks.loop(seconds=1)
async def update_view(view):
    while True:
        time.sleep(1)
        await view.edit_message()

@tasks.loop(seconds=30)
async def update_serverstats():
    for guild in bot.guilds:
        locale = get_locale(guild.id)
        channel_id = database[str(guild.id)]["serverstats"]
        if channel_id:
            params = {
                "server_id": guild.id
            }
            response = requests.get("http://127.0.0.1:5000/gameserver/get", params=params)
            channel = bot.get_channel(channel_id)
            msg_id = database[str(channel.guild.id)]["serverstats_msg"]
            msg = await find_existing_message(channel, msg_id)
            if not msg:
                msg = await channel.send(locale.loading)
                embed = discord.Embed(title=locale.serverstats, color=0xFF0000)
                embed.add_field(name=locale.status, value=locale.loading, inline=False)
                await msg.edit(content=None, embed=embed)
                database[str(channel.guild.id)]["serverstats_msg"] = msg.id
            if response.status_code == 200:
                serverinfo = response.json()
                view = views.ServerStatisticsView(msg, guild, serverinfo["name"], serverinfo["max"], serverinfo["current"], serverinfo["img"])
            else:
                view = views.ServerStatisticsView(msg, guild, locale.serverstats, "A", "N", "https://cdn3.iconfinder.com/data/icons/meteocons/512/n-a-128.png")
            await view.edit_message()
            await msg.edit(view=view)

@tasks.loop(seconds=10)
async def update_wf():
    for guild in bot.guilds:
        locale = get_locale(guild.id)
        channel_id = database[str(guild.id)]["warframe"]
        if channel_id:
            channel = bot.get_channel(channel_id)
            msg_id = database[str(channel.guild.id)]["warframe_msg1"]
            msg = await find_existing_message(channel, msg_id)
            if not msg:
                msg = await channel.send(locale.loading)
                embed = discord.Embed(title=locale.serverstats, color=0xFF0000)
                embed.add_field(name=locale.status, value=locale.loading, inline=False)
                await msg.edit(content=None, embed=embed)
                database[str(channel.guild.id)]["warframe_msg1"] = msg.id

            cycle = wf_api.get_cycle(database[str(channel.guild.id)]["warframe_platform"])
            view = views.WfCycleView(msg, guild, cycle["cetus"], cycle["vallis"], cycle["cambion"])
            await view.edit_message()
            await msg.edit(view=view)

            msg_id = database[str(channel.guild.id)]["warframe_msg2"]
            msg = await find_existing_message(channel, msg_id)
            if not msg:
                msg = await channel.send(locale.loading)
                embed = discord.Embed(title=locale.serverstats, color=0xFF0000)
                embed.add_field(name=locale.status, value=locale.loading, inline=False)
                await msg.edit(content=None, embed=embed)
                database[str(channel.guild.id)]["warframe_msg2"] = msg.id

            trader = wf_api.get_trader(database[str(channel.guild.id)]["warframe_platform"])
            view = views.WfBarooView(msg, guild, trader["status"], trader["arrives"], trader["departs"])
            await view.edit_message()
            await msg.edit(view=view)



async def delete_message(ctx = None, msg = None, mgs = None):
    try:
        if ctx is not None:
            await ctx.message.delete()
            if mgs is not None:
                await ctx.channel.delete_messages(mgs)
        if msg is not None:
            await msg.delete()
    except:
        print("the message deletion failed")

def ensure_db_structure(guild_id):
    if str(guild_id) not in database:
        database[str(guild_id)] = {"members": None,
                                   "serverstats": None,
                                   "serverstats_msg": None,
                                   "music": None,
                                   "music_msg": None,
                                   "welcome": None,
                                   "lol": None,
                                   "rivals": None,
                                   "warframe": None,
                                   "warframe_msg1": None,
                                   "warframe_msg2": None,
                                   "warframe_platform": config.default_platform,
                                   "prefix" : config.default_command_prefix,
                                   "lang": config.default_lang,
                                   "timezone": "CET",
                                   "restricted_words": [],
                                   "welcome_msg": "",
                                   "welcome_rls" : []
                                   }

def db_add_channel(guild_id, category, channel_id):
    ensure_db_structure(guild_id)
    if category in database[str(guild_id)]:
        database[str(guild_id)][category] = channel_id
    save_database()

def save_database():
    with open(json_path, 'w') as db_json:
        json.dump(database, db_json, indent=4)

async def shutdown():
    await bot.close()
    print("the bot have stopped")

def on_shutdown_signal():
    asyncio.create_task(shutdown())

## Commands
if config.musicplayer:
    @bot.command(name="join", aliases=["j"])
    async def join(ctx):
        locale =get_locale(ctx.guild.id)
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            await channel.connect()
        else:
            await ctx.send(locale.join_voice_first)

    @bot.command(name="leave", aliases=["l"])
    async def leave(ctx):
        locale =get_locale(ctx.guild.id)
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
        else:
            await ctx.send(locale.not_in_voice)


    @bot.command(name="play", aliases=["p"])
    async def play(ctx, *, query: str):
        locale =get_locale(ctx.guild.id)
        if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['music'] == None:
            msg = await ctx.send(locale.music_channel_not_set)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if not database[str(ctx.guild.id)]['music'] == ctx.channel.id:
            msg = await ctx.send(locale.cant_use_here)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        response = await get_server_response(ctx)
        if response.choosing:
            responses[ctx.guild.id].answer = 0
            responses[ctx.guild.id].choosing = False

        if ctx.voice_client is None:
            if ctx.author.voice:
                channel = ctx.author.voice.channel
                await channel.connect()
                mgs = []
                async for msg in ctx.channel.history(limit=100):
                    mgs.append(msg)
                await delete_message(ctx, None, mgs)
            else:
                msg = await ctx.send(locale.join_voice_first)
                await asyncio.sleep(2)
                await delete_message(ctx, msg)
                return

        result_type, search_results = mdown.search(query)
        if result_type == "link" :
            if search_results is None:
                msg = await ctx.send(locale.wrong_link)
                await asyncio.sleep(2)
                await delete_message(ctx, msg)
                return
        else:
            if not search_results['entries']:
                msg = await ctx.send(locale.no_song_found)
                await asyncio.sleep(2)
                await delete_message(ctx, msg)
                return

        playlist = await get_server_playlist(ctx)

        msg_id = database[str(ctx.guild.id)]["music_msg"]
        msg = await find_existing_message(ctx, msg_id)
        if not msg:
            msg = await ctx.send(locale.loading)
            embed = discord.Embed(title=locale.musicplayer, color=0xFF0000)
            embed.add_field(name=locale.status, value=locale.loading, inline=False)
            await msg.edit(content=None, embed=embed)
            database[str(ctx.guild.id)]["music_msg"] = msg.id
            save_database()
        view = await get_server_view(ctx, msg)
        await msg.edit(view=view)

        if result_type == "keyword":
            await choose_song_msg(ctx, response, view, playlist, search_results)
        elif result_type == "playlist":
            for song in search_results['entries']:
                playlist.add(song['title'], song['url'])
        else:
            playlist.add(search_results['title'], search_results['url'])

        if not update_view.is_running():
            update_view.start(view)

        await asyncio.sleep(2)
        await delete_message(ctx)

        while result_type == "keyword" and response.answer == -1:
            await asyncio.sleep(0.1)

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            play_next(ctx, view, playlist)

if config.lolapi:
    @bot.command(name="league", aliases=["lol"])
    async def league(ctx, name=None, tag=None, region=None):
        locale = get_locale(ctx.guild.id)
        if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['lol'] == None:
            msg = await ctx.send(locale.lol_channel_not_set)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if not database[str(ctx.guild.id)]['lol'] == ctx.channel.id:
            msg = await ctx.send(locale.cant_use_here)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if name is None:
            msg = await ctx.send(locale.name_required)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if tag is None:
            msg = await ctx.send(locale.tag_required)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if region is None:
            msg = await ctx.send(locale.region_required)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if region not in ['na1', 'br1', 'lan1', 'las1', 'kr', 'jp1', 'eun1', 'euw1', 'tr1', 'ru', 'oc1', 'ph2', 'sg2', 'th2', 'tw2', 'vn2']:
            msg = await ctx.send(locale.wrong_third_param)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        msg = await ctx.send("...")
        embed = discord.Embed(title=f"{name}{locale.statistics}", color=0x800080)
        embed.add_field(name=locale.status, value=locale.loading, inline=False)
        await msg.edit(content=None, embed=embed)
        data = lol_api.get_player_data(name, tag, region)
        if isinstance(data, dict):
            view = views.LolPlayerView(msg, data, name, tag, ctx.guild)
            await view.edit_message()
            await msg.edit(view=view)
        else:
            embed = discord.Embed(title=f"{name}{locale.statistics}", color=0x800080)
            embed.add_field(name=locale.status, value=locale.unexpected_error, inline=False)
            await msg.edit(content=None, embed=embed)
            return


if config.rivalsapi:
    @bot.command(name="rivals", aliases=["rv"])
    async def rivals(ctx, name=None, season=None, typ=None):
        locale =get_locale(ctx.guild.id)
        if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['rivals'] == None:
            msg = await ctx.send(locale.rivals_channel_not_set)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if not database[str(ctx.guild.id)]['rivals'] == ctx.channel.id:
            msg = await ctx.send(locale.cant_use_here)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if name is None:
            msg = await ctx.send(locale.name_required)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if season not in (config.seasons + ["update"]):
            if season is None:
                season = config.seasons[-1]
            else:
                msg = await ctx.send(locale.wrong_second_param)
                await asyncio.sleep(2)
                await delete_message(ctx, msg)
                return

        if typ not in ["map", "matchup", None]:
            msg = await ctx.send(locale.wrong_third_param)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if typ == "map":
            msg = await ctx.send("...")
            embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
            embed.add_field(name=locale.status, value=locale.loading, inline=False)
            await msg.edit(content=None, embed=embed)
            data = rivals_api.get_map_data(name, season)
            if data == False:
                embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
                embed.add_field(name=locale.status, value=locale.private_profile, inline=False)
                await msg.edit(content=None, embed=embed)
                return
            if data is None:
                embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
                embed.add_field(name=locale.status, value=locale.unexpected_error, inline=False)
                await msg.edit(content=None, embed=embed)
                return

            view = views.RivalsMapView(msg, data, name, season, ctx.guild)
            await view.edit_message()
            await msg.edit(view=view)
        elif typ == "matchup":
            msg = await ctx.send("...")
            embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
            embed.add_field(name=locale.status, value=locale.loading, inline=False)
            await msg.edit(content=None, embed=embed)
            data = rivals_api.get_matchup_data(name, season)

            if data == False:
                embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
                embed.add_field(name=locale.status, value=locale.private_profile, inline=False)
                await msg.edit(content=None, embed=embed)
                return
            if data is None:
                embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
                embed.add_field(name=locale.status, value=locale.unexpected_error, inline=False)
                await msg.edit(content=None, embed=embed)
                return

            view = views.RivalsMatchupView(msg, data, name, season, 1, ctx.guild)
            await view.edit_message()
            await msg.edit(view=view)
            if len(data['heroes']) > 24:
                msg = await ctx.send("...")
                view = views.RivalsMatchupView(msg, data, name, season, 2, ctx.guild)
                await view.edit_message()
                await msg.edit(view=view)
        else:
            if season == "update":
                msg = await ctx.send("...")
                embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
                embed.add_field(name=locale.status, value=locale.profile_update_started, inline=False)
                await msg.edit(content=None, embed=embed)
                data = rivals_api.get_player_data(name, season)

                if data == False:
                    embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
                    embed.add_field(name=locale.status, value=locale.private_profile, inline=False)
                    await msg.edit(content=None, embed=embed)
                    return
                if data is None:
                    embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
                    embed.add_field(name=locale.status, value=locale.unexpected_error, inline=False)
                    await msg.edit(content=None, embed=embed)
                    return
            else:
                msg = await ctx.send("...")
                embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
                embed.add_field(name=locale.status, value=locale.loading, inline=False)
                await msg.edit(content=None, embed=embed)
                data = rivals_api.get_player_data(name, season)
                if data == False:
                    embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
                    embed.add_field(name=locale.status, value=locale.private_profile, inline=False)
                    await msg.edit(content=None, embed=embed)
                    return
                if data is None:
                    embed = discord.Embed(title=f"{name}{locale.ranked_statistics}", color=0x800080)
                    embed.add_field(name=locale.status, value=locale.unexpected_error, inline=False)
                    await msg.edit(content=None, embed=embed)
                    return

                view = views.RivalsPlayerView(msg, data, name, season, ctx.guild)

                await view.edit_message()
                await msg.edit(view=view)

if config.wfapi:
    @bot.command(name="warframe", aliases=["wf"])
    async def warframe(ctx, platform=None):
        locale = get_locale(ctx.guild.id)
        if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['warframe'] == None:
            msg = await ctx.send(locale.wf_channel_not_set)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if not database[str(ctx.guild.id)]['warframe'] == ctx.channel.id:
            msg = await ctx.send(locale.cant_use_here)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if platform is None:
            msg = await ctx.send(locale.platform_required)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if platform not in ["pc", "ps4", "xb1", "swi"]:
            msg = await ctx.send(locale.platform_must_be)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        database[str(ctx.guild.id)]["warframe_platform"] = platform
        msg = await ctx.send(f"{locale.platform_set_to}{platform}")
        await asyncio.sleep(2)
        await delete_message(ctx, msg)


if config.clear:
    @bot.command(name="clear", aliases=["cl"])
    @commands.has_permissions(administrator=True)
    async def clear(ctx, number=None):
        locale =get_locale(ctx.guild.id)
        mgs = []
        if number is None:
            number = 100
        number = int(number)
        counter = 0
        async for msg in ctx.channel.history(limit=number):
            mgs.append(msg)
            counter += 1
        await delete_message(ctx, None, mgs)
        msg = await ctx.send(f"{counter}{locale.message_deleted}")
        await asyncio.sleep(5)
        await delete_message(None, msg, None)

if config.musicplayer or config.rivalsapi or config.welcome or config.lolapi:
    @bot.command(name="set_channel", aliases=["sc"])
    @commands.has_permissions(administrator=True)
    async def set_channel(ctx, typ=None):
        locale = get_locale(ctx.guild.id)
        if typ is None:
            msg = await ctx.send(locale.type_required)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
        id = str(ctx.guild.id)
        if typ == "music" and config.musicplayer:
            if database[id]['music'] == None:
                db_add_channel(id, "music", ctx.channel.id)

                msg = await ctx.send(f"{locale.music_set_to}{ctx.channel.mention}")
            else:
                msg = await ctx.send(locale.music_channel_already_set)
        elif typ == "lol"  and config.lolapi:
            if database[id]['lol'] == None:
                db_add_channel(id, "lol", ctx.channel.id)

                msg = await ctx.send(f"{locale.lol_set_to}{ctx.channel.mention}")
            else :
                msg = await ctx.send(locale.lol_channel_already_set)
        elif typ == "rivals"  and config.rivalsapi:
            if database[id]['rivals'] == None:
                db_add_channel(id, "rivals", ctx.channel.id)

                msg = await ctx.send(f"{locale.rivals_set_to}{ctx.channel.mention}")
            else:
                msg = await ctx.send(locale.rivals_channel_already_set)
        elif typ == "welcome"  and config.welcome:
            if database[id]['welcome'] == None:
                db_add_channel(id, "welcome", ctx.channel.id)

                msg = await ctx.send(f"{locale.welcome_set_to}{ctx.channel.mention}")
            else:
                msg = await ctx.send(locale.welcome_channel_already_set)
        elif typ == "members"  and config.membercount:
            if database[id]['members'] == None:
                db_add_channel(id, "members", ctx.channel.id)

                msg = await ctx.send(f"{locale.members_set_to}{ctx.channel.mention}")
            else:
                msg = await ctx.send(locale.members_channel_already_set)
        elif typ == "serverstats"  and config.serverstats:
            if database[id]['serverstats'] == None:
                db_add_channel(id, "serverstats", ctx.channel.id)

                msg = await ctx.send(locale.loading)
                embed = discord.Embed(title=locale.serverstats, color=0xFF0000)
                embed.add_field(name=locale.status, value=locale.loading, inline=False)
                view = views.ServerStatisticsView(msg, ctx.guild, locale.serverstats, "A", "N", "https://cdn3.iconfinder.com/data/icons/meteocons/512/n-a-128.png")
                await view.edit_message()
                await msg.edit(view=view)

                database[str(ctx.guild.id)]["serverstats_msg"] = msg.id
                save_database()

                msg = await ctx.send(f"{locale.serverstats_set_to}{ctx.channel.mention}")
            else:
                msg = await ctx.send(locale.serverstats_channel_already_set)
        elif typ == "wf" and config.wfapi:
            if database[id]['warframe'] == None:
                db_add_channel(id, "warframe", ctx.channel.id)

                msg_id = database[str(ctx.guild.id)]["warframe_msg1"]
                msg = await find_existing_message(ctx, msg_id)
                if not msg:
                    msg = await ctx.send(locale.loading)
                    embed = discord.Embed(title=locale.serverstats, color=0xFF0000)
                    embed.add_field(name=locale.status, value=locale.loading, inline=False)
                    await msg.edit(content=None, embed=embed)
                    database[str(ctx.guild.id)]["warframe_msg1"] = msg.id
                    save_database()

                cycle = wf_api.get_cycle(database[str(ctx.guild.id)]["warframe_platform"])
                view = views.WfCycleView(msg, ctx.guild, cycle["cetus"], cycle["vallis"], cycle["cambion"])
                await view.edit_message()
                await msg.edit(view=view)

                msg_id = database[str(ctx.guild.id)]["warframe_msg2"]
                msg = await find_existing_message(ctx, msg_id)
                if not msg:
                    msg = await ctx.send(locale.loading)
                    embed = discord.Embed(title=locale.serverstats, color=0xFF0000)
                    embed.add_field(name=locale.status, value=locale.loading, inline=False)
                    await msg.edit(content=None, embed=embed)
                    database[str(ctx.guild.id)]["warframe_msg2"] = msg.id
                    save_database()

                trader = wf_api.get_trader(database[str(ctx.guild.id)]["warframe_platform"])
                view = views.WfBarooView(msg, ctx.guild, trader["status"], trader["arrives"], trader["departs"])
                await view.edit_message()
                await msg.edit(view=view)

                msg = await ctx.send(f"{locale.wf_set_to}{ctx.channel.mention}")
            else:
                msg = await ctx.send(locale.wf_channel_already_set)
        else:
            msg = await ctx.send(locale.wrong_first_param)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return
        await asyncio.sleep(2)
        await delete_message(ctx, msg)

    @bot.command(name="clear_channel", aliases=["cc"])
    @commands.has_permissions(administrator=True)
    async def clear_channel(ctx, typ=None):
        locale =get_locale(ctx.guild.id)
        if typ is None:
            msg = await ctx.send(locale.type_required)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
        if typ == "music"  and config.musicplayer:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['music'] == None:
                msg = await ctx.send(locale.music_channel_not_set)
            else:
                database[str(ctx.guild.id)]['music'] = None
                save_database()

                msg = await ctx.send(locale.music_channel_deleted)
        elif typ == "lol"  and config.lolapi:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['lol'] == None:
                msg = await ctx.send(locale.lol_channel_not_set)
            else:
                database[str(ctx.guild.id)]['lol'] = None
                save_database()

                msg = await ctx.send(locale.lol_channel_deleted)
        elif typ == "rivals"  and config.rivalsapi:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['rivals'] == None:
                msg = await ctx.send(locale.rivals_channel_not_set)
            else:
                database[str(ctx.guild.id)]['rivals'] = None
                save_database()

                msg = await ctx.send(locale.rivals_channel_deleted)
        elif typ == "welcome"  and config.welcome:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['welcome'] == None:
                msg = await ctx.send(locale.welcome_channel_not_set)
            else:
                database[str(ctx.guild.id)]['welcome'] = None
                save_database()

                msg = await ctx.send(locale.welcome_channel_deleted)
        elif typ == "members"  and config.welcome:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['members'] == None:
                msg = await ctx.send(locale.members_channel_not_set)
            else:
                database[str(ctx.guild.id)]['members'] = None
                save_database()

                msg = await ctx.send(locale.members_channel_deleted)
        elif typ == "serverstats"  and config.serverstats:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['serverstats'] == None:
                msg = await ctx.send(locale.serverstats_channel_not_set)
            else:
                database[str(ctx.guild.id)]['serverstats'] = None
                save_database()

                msg = await ctx.send(locale.serverstats_channel_deleted)
        elif typ == "wf" and config.wfapi:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['warframe'] == None:
                msg = await ctx.send(locale.wf_channel_not_set)
            else:
                database[str(ctx.guild.id)]['warframe'] = None
                save_database()

                msg = await ctx.send(locale.wf_channel_deleted)
        else:
            msg = await ctx.send(locale.wrong_first_param)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return
        await asyncio.sleep(2)
        await delete_message(ctx, msg)

if config.prefixchange:
    @bot.command(name="set_prefix", aliases=["sp"])
    @commands.has_permissions(administrator=True)
    async def set_prefix(ctx, prefix=None):
        locale =get_locale(ctx.guild.id)
        if prefix is None:
            msg = await ctx.send(locale.prefix_required)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return
        if len(prefix) > 1:
            msg = await ctx.send(locale.prefix_max_char)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        database[str(ctx.guild.id)]['prefix'] = prefix
        save_database()
        bot.command_prefix = prefix

        msg = await ctx.send(f"{locale.prefix_set_to}{prefix}")
        await asyncio.sleep(2)
        await delete_message(ctx, msg)

if config.welcome:
    @bot.command(name="set_welcome_msg", aliases=["swm"])
    @commands.has_permissions(administrator=True)
    async def set_welcome_msg(ctx, *message : str):
        locale =get_locale(ctx.guild.id)
        if not message:
            msg = await ctx.send(locale.message_required)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return
        if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['welcome'] == None:
            msg = await ctx.send(locale.welcome_channel_not_set)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
        else:
            database[str(ctx.guild.id)]['welcome_msg'] = ' '.join(message)
            save_database()

            msg = await ctx.send(f"{locale.welcome_message_set_to}{' '.join(message)}")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)

    @bot.command(name="set_welcome_rls", aliases=["swr"])
    @commands.has_permissions(administrator=True)
    async def set_welcome_rls(ctx, *roles: discord.Role):
        locale =get_locale(ctx.guild.id)
        if not roles:
            msg = await ctx.send(locale.rank_required)
            await asyncio.sleep(2)
            await msg.delete()
            return
        if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['welcome'] == None:
            msg = await ctx.send(locale.welcome_channel_not_set)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
        else:
            database[str(ctx.guild.id)]["welcome_rls"] = [role.id for role in roles]
            save_database()

            role_mentions = ' '.join(role.mention for role in roles)
            msg = await ctx.send(f"{locale.welcome_roles_set_to}{role_mentions}")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)

if config.moderation:
    @bot.command(name="add_restricted", aliases=["ar"])
    @commands.has_permissions(administrator=True)
    async def add_restricted(ctx, *words: str):
        locale =get_locale(ctx.guild.id)
        if not words:
            msg = await ctx.send(locale.word_required)
            await asyncio.sleep(2)
            await msg.delete()
            return
        else:
            for word in words:
                database[str(ctx.guild.id)]["restricted_words"].append(word)
            save_database()
            msg = await ctx.send(f"{locale.restricted_words_added}{' '.join(words)}")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)

    @bot.command(name="remove_restricted", aliases=["rs"])
    @commands.has_permissions(administrator=True)
    async def remove_restricted(ctx, *words: str):
        locale =get_locale(ctx.guild.id)
        if not words:
            msg = await ctx.send(locale.word_required)
            await asyncio.sleep(2)
            await msg.delete()
            return
        else:
            for word in words:
                database[str(ctx.guild.id)]["restricted_words"].remove(word)
            save_database()
            msg = await ctx.send(f"{locale.restricted_words_removed}{' '.join(words)}")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)


    @bot.command(name="clear_restricted", aliases=["cr"])
    @commands.has_permissions(administrator=True)
    async def clear_restricted(ctx):
        locale =get_locale(ctx.guild.id)
        database[str(ctx.guild.id)]["restricted_words"] = []
        save_database()
        msg = await ctx.send(locale.restricted_words_cleared)
        await asyncio.sleep(2)
        await delete_message(ctx, msg)

if config.systemmessage:
    @bot.command(name="system_message", aliases=["sm"])
    @commands.has_permissions(administrator=True)
    async def system_message(ctx, title=None, *message : str):
        locale =get_locale(ctx.guild.id)
        if title is None:
            msg = await ctx.send(locale.title_required)
            await asyncio.sleep(2)
            await delete_message(None, msg)
            return
        if not message:
            msg = await ctx.send(locale.message_required)
            await asyncio.sleep(2)
            await delete_message(None, msg)
            return

        await delete_message(ctx)

        msg = await ctx.send(locale.loading)
        embed = discord.Embed(title=f"{ctx.guild.name}")

        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.add_field(name=title, value=' '.join(message).replace('\\n', '\n'), inline=False)
        await msg.edit(content=None, embed=embed)

if config.setlang:
    @bot.command(name="set_language", aliases=["sl"])
    @commands.has_permissions(administrator=True)
    async def system_message(ctx, lang=None):
        locale=get_locale(ctx.guild.id)
        if lang is None:
            msg = await ctx.send(locale.lang_required)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return
        if not languages.key_exists(lang):
            msg = await ctx.send(locale.wrong_lang)
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        database[str(ctx.guild.id)]["lang"] = lang
        save_database()

        locale=get_locale(ctx.guild.id)
        msg = await ctx.send(f"{locale.lang_set}{lang}")
        await asyncio.sleep(2)
        await delete_message(ctx, msg)

@bot.command(name="test")
async def test(ctx):
    guild = ctx.guild
    locale = get_locale(guild.id)
    if database[str(guild.id)]["members"]:
        count = len([m for m in guild.members if not m.bot])
        database[str(guild.id)]["member_count"] = count
        save_database()
        await bot.get_channel(database[str(guild.id)]["members"]).edit(name=f"{locale.member_count}{count}")

## Events
@bot.event
async def on_message(message):
    ensure_db_structure(message.guild.id)
    locale =get_locale(message.guild.id)
    if message.author == bot.user:
        return

    if config.moderation:
        restricted = False
        for word in database[str(message.guild.id)]['restricted_words']:
            if word in message.content.lower():
                restricted = True

        if restricted:
            await message.delete()
            msg = await message.channel.send(locale.message_moderated)
            await asyncio.sleep(2)
            await delete_message(None, msg)

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    guild = member.guild
    locale = get_locale(guild.id)
    if config.membercount and database[str(guild.id)]["members"]:
        count = len([m for m in guild.members if not m.bot])
        await bot.get_channel(database[str(guild.id)]["members"]).edit(name=f"{locale.member_count}{count}")
    if config.welcome:
        if str(guild.id) in database and database[str(guild.id) ]['welcome_rls'] != None:
            roles = [member.guild.get_role(role_id) for role_id in database[str(guild.id) ]["welcome_rls"]]
            roles = [role for role in roles if role is not None]
            if roles:
                try:
                    await member.add_roles(*roles)
                except discord.Forbidden:
                    msg = await member.guild.get_channel.send(locale.no_perm)
                    await asyncio.sleep(2)
                    await delete_message(None, msg)

        if str(guild.id)  in database and "welcome" in database[str(guild.id) ]:
            channel = member.guild.get_channel(database[str(guild.id) ]["welcome"])
            if channel:
                msg = await channel.send(f"{member.mention} {database[str(guild.id) ]['welcome_msg']}")
                embed = discord.Embed(title=f"{guild.name}")

                embed.set_thumbnail(url=guild.icon.url)
                embed.add_field(name=database[str(guild.id)]['welcome_msg'], value=member.mention, inline=False)
                await msg.edit(content=None, embed=embed)

@bot.event
async def on_member_remove(member):
    guild = member.guild
    locale = get_locale(guild.id)
    if config.membercount and database[str(guild.id)]["members"]:
        count = len([m for m in guild.members if not m.bot])
        await bot.get_channel(database[str(guild.id)]["members"]).edit(name=f"{locale.member_count}{count}")

@bot.event
async def on_guild_join(guild):
    ensure_db_structure(str(guild.id))

## Bot init
load_dotenv()
if config.rivalsapi:
    TOKEN = os.getenv("RIVALS_API_KEY")
    if TOKEN is None:
        raise ValueError("Rivals API Key not set.")
    rivals_api = marvelrivals.RivalsAPI(TOKEN)

if config.lolapi:
    TOKEN = os.getenv("LOL_API_KEY")
    if TOKEN is None:
        raise ValueError("Lol API Key not set.")
    lol_api = lol.LolAPI(TOKEN)

if config.wfapi:
    wf_api = wf.WfAPI()

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("Discord API Token not set.")

@bot.event
async def on_ready():
    for guild in bot.guilds:
        ensure_db_structure(guild.id)
    save_database()

    activity = discord.Game(name=config.activity_status)
    await bot.change_presence(activity=activity)
    print(f"Logged in as {bot.user}")

    if config.serverstats:
        if not update_serverstats.is_running():
            update_serverstats.start()

    if config.wfapi:
        if not update_wf.is_running():
            update_wf.start()
def run_flask():
    gameserver_api.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)

if __name__ == "__main__":
    if config.serverstats:
        flask_thread = Thread(target=run_flask)
        flask_thread.daemon = True
        flask_thread.start()

    bot.run(TOKEN)
    signal.signal(signal.SIGINT, lambda signal, frame: on_shutdown_signal())
