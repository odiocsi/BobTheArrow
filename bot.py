import os
import time
import asyncio
import signal
import json
from dotenv import load_dotenv

import discord
from discord.ext import commands

import config
from classes import api
from classes import music
from classes import views

if config.default_lang == "hu":
    from locales import hu as locale

## Config
intents = discord.Intents.default()
intents.messages = True 
intents.message_content = True  
intents.members = True
ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}


async def get_prefix(bot, message):
    guild = message.guild
    ensure_db_structure(str(guild.id))
    return database[str(guild.id)]['prefix']

bot = commands.Bot(command_prefix=get_prefix, intents=intents, help_command=views.CustomHelpCommand())

## Global variables
database = None
mdown = music.MusicDownloader()
playlists = {}
message_views = {}
responses = {}
download_folder = config.download_path
awaited_delete = False

## Db
json_path = config.database_path
if not os.path.exists(json_path) or os.path.getsize(json_path) == 0:
    database = {}
else:
    with open(json_path, 'r') as db_json:
        database = json.load(db_json) 

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

async def choose_song_msg(ctx, response, view, playlist, search_results):
    response.choosing = True
    msg = await ctx.send(locale.searching)
    embed = discord.Embed(title="Találatok", color=0xFF0000)
    embed.add_field(name="Státusz", value=locale.searching, inline=False)
    await msg.edit(content=None, embed=embed)

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
    ctx.voice_client.stop()

    if playlist.isEmpty():
        return
    
    playlist.next()
    url = playlist.current['url']
    audio_file = mdown.download(url)

    ctx.voice_client.play(discord.FFmpegPCMAudio(audio_file), after=lambda e: play_next(ctx, view, playlist))


async def update_view(view):
    while True:
        time.sleep(1)        
        await view.edit_message()


async def delete_message(ctx = None, msg = None, mgs = None):
    try: 
        if ctx is not None:
            await ctx.message.delete()
            if mgs is not None:
                await ctx.channel.delete_messages(mgs)
        if msg is not None:
            await msg.delete()
    except:
        print(locale.error_delete_msg)

def delete_all_files_in_folder():
    for filename in os.listdir(download_folder):
        file_path = os.path.join(download_folder, filename)
        if os.path.isfile(file_path):
            try: 
                os.remove(file_path)
            except:
                print(locale.error_delete_file)

def ensure_db_structure(guild_id):
    if guild_id not in database:
        database[guild_id] = {"music": None, "welcome": None, "lol": None, "rivals": None, "prefix" : config.default_command_prefix, "lang": config.default_lang, "timezone": "CET", "restricted_words": [], "welcome_msg": "", "welcome_rls" : []}

def db_add_channel(guild_id, category, channel_id):
    ensure_db_structure(guild_id)  
    if category in database[guild_id]:  
        database[guild_id][category] = channel_id

def save_database():
    with open(json_path, 'w') as db_json:
        json.dump(database, db_json, indent=4)

async def shutdown():
    await bot.close() 
    print(locale.stopped)

def on_shutdown_signal():
    asyncio.create_task(shutdown())

@bot.event
async def on_ready():
    print(locale.started)

## Commands
@bot.command()
async def join(ctx):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        await channel.connect()
    else:
        await ctx.send(locale.error_no_channel)

@bot.command()
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
    else:
        await ctx.send(locale.error_not_in_channel)

if config.musicplayer:
    @bot.command(name="play", aliases=["p"])
    async def play(ctx, *, query: str):
        if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['music'] == None:
            msg = await ctx.send("Nincsen beállítva csatorna a zenelejátszóhoz.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if not database[str(ctx.guild.id)]['music'] == ctx.channel.id:
            msg = await ctx.send("Ezt a parancsot itt nem használhatod.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

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

        result_type, search_results = mdown.search(query)
        if result_type == "link" :
            if search_results is None:
                msg = await ctx.send("Érvénytelen hivatkozás.")
                await asyncio.sleep(2)
                await delete_message(ctx, msg)
                return
        else:
            if not search_results['entries']:
                msg = await ctx.send("Nem található zene a megadott kereséssel.")
                await asyncio.sleep(2)
                await delete_message(ctx, msg)
                return

        playlist = await get_server_playlist(ctx)

        msg = await find_existing_message(ctx)
        if not msg:
            msg = await ctx.send("Betöltés...")
            embed = discord.Embed(title="Zenelejátszó", color=0xFF0000)
            embed.add_field(name="Státusz", value="Betöltés...", inline=False)
            await msg.edit(content=None, embed=embed)
        view = await get_server_view(ctx, msg)
        await msg.edit(view=view)

        if result_type == "keyword":
            await choose_song_msg(ctx, response, view, playlist, search_results)
        elif result_type == "playlist":
            for song in search_results['entries']:
                playlist.add(song['title'], song['url'])
        else:
            playlist.add(search_results['title'], search_results['url'])

        bot.loop.create_task(update_view(view))

        await asyncio.sleep(2)
        await delete_message(ctx)

        while result_type == "keyword" and response.answer == -1:
            await asyncio.sleep(0.1)

        if not ctx.voice_client.is_playing() and not ctx.voice_client.is_paused():
            play_next(ctx, view, playlist)

if config.lolapi:
    @bot.command(name="league", aliases=["lol"])
    async def league(ctx):
        msg = await ctx.send ("Nincs implementálva.")
        await asyncio.sleep(2)
        await delete_message(ctx, msg)

if config.rivalsapi:
    @bot.command(name="rivals", aliases=["rv"])
    async def rivals(ctx, name=None, season=None, typ=None):
        if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['rivals'] == None:
            msg = await ctx.send("Nincsen beállítva csatorna a rivals statisztikákhoz.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if not database[str(ctx.guild.id)]['rivals'] == ctx.channel.id:
            msg = await ctx.send("Ezt a parancsot itt nem használhatod.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if name is None:
            msg = await ctx.send("A név megadása kötelező.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        if season not in ["0", "1", "1.5", "update"]:
            if season is None:
                season = "1.5"
            else:
                msg = await ctx.send("Hibás 2. paraméter.")
                await asyncio.sleep(2)
                await delete_message(ctx, msg)
                return

        if typ not in ["map", "matchup", None]:
            msg = await ctx.send("Hibás 3. paraméter.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return


        if typ == "map":
            msg = await ctx.send("...")
            embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
            embed.add_field(name="Státusz", value="Betöltés...", inline=False)
            await msg.edit(content=None, embed=embed)
            data = rivals_api.get_map_data(name, season)
            if data == False:
                embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
                embed.add_field(name="Státusz", value="A megadott profil privát", inline=False)
                await msg.edit(content=None, embed=embed)
                return
            if data is None:
                embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
                embed.add_field(name="Státusz", value="Váratlan hiba történt", inline=False)
                await msg.edit(content=None, embed=embed)
                return

            view = views.RivalsMapView(msg, data, name, season)
            await view.edit_message()
            await msg.edit(view=view)
        elif typ == "matchup":
            msg = await ctx.send("...")
            embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
            embed.add_field(name="Státusz", value="Betöltés...", inline=False)
            await msg.edit(content=None, embed=embed)
            data = rivals_api.get_matchup_data(name, season)

            if data == False:
                embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
                embed.add_field(name="Státusz", value="A megadott profil privát", inline=False)
                await msg.edit(content=None, embed=embed)
                return
            if data is None:
                embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
                embed.add_field(name="Státusz", value="Váratlan hiba történt", inline=False)
                await msg.edit(content=None, embed=embed)
                return

            view = views.RivalsMatchupView(msg, data, name, season, 1)
            await view.edit_message()
            await msg.edit(view=view)
            if len(data['heroes']) > 24:
                msg = await ctx.send("...")
                view = views.RivalsMatchupView(msg, data, name, season, 2)
                await view.edit_message()
                await msg.edit(view=view)
        else:
            if season == "update":
                msg = await ctx.send("...")
                embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
                embed.add_field(name="Státusz", value="A profil frissítése megkezdödött", inline=False)
                await msg.edit(content=None, embed=embed)
                data = rivals_api.get_player_data(name, season)

                if data == False:
                    embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
                    embed.add_field(name="Státusz", value="A megadott profil privát", inline=False)
                    await msg.edit(content=None, embed=embed)
                    return
                if data is None:
                    embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
                    embed.add_field(name="Státusz", value="Váratlan hiba történt", inline=False)
                    await msg.edit(content=None, embed=embed)
                    return
            else:
                msg = await ctx.send("...")
                embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
                embed.add_field(name="Státusz", value="Betöltés...", inline=False)
                await msg.edit(content=None, embed=embed)
                data = rivals_api.get_player_data(name, season)

                if data == False:
                    embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
                    embed.add_field(name="Státusz", value="A megadott profil privát", inline=False)
                    await msg.edit(content=None, embed=embed)
                    return
                if data is None:
                    embed = discord.Embed(title=f"{name} rangsorolt statisztikái", color=0x800080)
                    embed.add_field(name="Státusz", value="Váratlan hiba történt", inline=False)
                    await msg.edit(content=None, embed=embed)
                    return

                view = views.RivalsPlayerView(msg, data, name, season)

                await view.edit_message()
                await msg.edit(view=view)

if config.clear:
    @bot.command(name="clear", aliases=["cl"])
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

if config.musicplayer or config.rivalsapi or config.welcome or config.lolapi:
    @bot.command(name="set_channel", aliases=["sc"])
    @commands.has_permissions(administrator=True)
    async def set_channel(ctx, typ=None):
        if typ is None:
            msg = await ctx.send("A típus megadása kötelező.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
        msg = ""
        if typ == "music" and config.musicplayer:
            if database[str(ctx.guild.id)]['music'] == None:
                db_add_channel(str(ctx.guild.id), "music", ctx.channel.id)
                save_database()

                msg = await ctx.send(f"A zene csatorna beállítva a következőre: {ctx.channel.mention}")
            else:
                msg = await ctx.send("A zene csatorna már be van állítva.")
        elif typ == "lol"  and config.lolapi:
            if database[str(ctx.guild.id)]['lol'] == None:
                db_add_channel(str(ctx.guild.id), "lol", ctx.channel.id)
                save_database()

                msg = await ctx.send(f"A lol csatorna beállítva a következőre: {ctx.channel.mention}")
        elif typ == "rivals"  and config.rivalsapi:
            if database[str(ctx.guild.id)]['rivals'] == None:
                db_add_channel(str(ctx.guild.id), "rivals", ctx.channel.id)
                save_database()

                msg = await ctx.send(f"A rivals csatorna beállítva a következőre: {ctx.channel.mention}")
            else:
                msg = await ctx.send("A rivals csatorna már be van állítva.")
        elif typ == "welcome"  and config.welcome:
            if database[str(ctx.guild.id)]['welcome'] == None:
                db_add_channel(str(ctx.guild.id), "welcome", ctx.channel.id)
                save_database()

                msg = await ctx.send(f"Az üdvözlő csatorna beállítva a következőre: {ctx.channel.mention}")
            else:
                msg = await ctx.send("Az üdvözlő csatorna már be van állítva.")
        else:
            msg = await ctx.send("Hibás paraméter.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return
        await asyncio.sleep(2)
        await delete_message(ctx, msg)

    @bot.command(name="clear_channel", aliases=["cc"])
    @commands.has_permissions(administrator=True)
    async def clear_channel(ctx, typ=None):
        if typ is None:
            msg = await ctx.send("A típus megadása kötelező.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
        msg = ""
        if typ == "music"  and config.musicplayer:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['music'] == None:
                msg = await ctx.send("A zene csatorna nincsen beállítva.")
            else:
                database[str(ctx.guild.id)]['music'] = None
                save_database()

                msg = await ctx.send("A zene csatorna törölve.")
        elif typ == "lol"  and config.lolapi:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['lol'] == None:
                msg = await ctx.send("A lol csatorna nincsen beállítva.")
            else:
                database[str(ctx.guild.id)]['lol'] = None
                save_database()

                msg = await ctx.send("A lol csatorna törölve.")
        elif typ == "rivals"  and config.rivalsapi:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['rivals'] == None:
                msg = await ctx.send("A rivals csatorna nincsen beállítva.")
            else:
                database[str(ctx.guild.id)]['rivals'] = None
                save_database()

                msg = await ctx.send("A rivals csatorna törölve.")
        elif typ == "welcome"  and config.welcome:
            if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['welcome'] == None:
                msg = await ctx.send("Az üdvözlő csatorna nincsen beállítva.")
            else:
                database[str(ctx.guild.id)]['welcome'] = None
                save_database()

                msg = await ctx.send("Az üdvözlő csatorna törölve.")
        else:
            msg = await ctx.send("Hibás paraméter.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return
        await asyncio.sleep(2)
        await delete_message(ctx, msg)

if config.prefixchange:
    @bot.command(name="set_prefix", aliases=["sp"])
    @commands.has_permissions(administrator=True)
    async def set_prefix(ctx, prefix=None):
        if prefix is None:
            msg = await ctx.send("A prefix megadása kötelező.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return
        if len(prefix) > 1:
            msg = await ctx.send("A prefix maximum 1 karakter lehet.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return

        database[str(ctx.guild.id)]['prefix'] = prefix
        save_database()
        bot.command_prefix = prefix

        msg = await ctx.send(f"A prefix beállítva a következőre: {prefix}")
        await asyncio.sleep(2)
        await delete_message(ctx, msg)

if config.welcome:
    @bot.command(name="set_welcome_msg", aliases=["swm"])
    @commands.has_permissions(administrator=True)
    async def set_welcome_msg(ctx, *message : str):
        if not message:
            msg = await ctx.send("Az üzenet megadása kötelező.")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)
            return
        if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['welcome'] == None:
            msg = await ctx.send("Az üdvözlő csatorna nincsen beállítva.")
            await asyncio.sleep(2);
            await delete_message(ctx, msg)
        else:
            database[str(ctx.guild.id)]['welcome_msg'] = " ".join(message)
            save_database()

            msg = await ctx.send(f"Az üvözlő üzenet beállítva a következőre: {" ".join(message)}")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)

    @bot.command(name="set_welcome_rls", aliases=["swr"])
    @commands.has_permissions(administrator=True)
    async def set_welcome_rls(ctx, *roles: discord.Role):
        if not roles:
            msg = await ctx.send("Meg kell adnod legalább egy rangot.")
            await asyncio.sleep(2)
            await msg.delete()
            return
        if str(ctx.guild.id) not in database or database[str(ctx.guild.id)]['welcome'] == None:
            msg = await ctx.send("Az üdvözlő csatorna nincsen beállítva.")
            await asyncio.sleep(2);
            await delete_message(ctx, msg)
        else:
            database[str(ctx.guild.id)]["welcome_rls"] = [role.id for role in roles]
            save_database()

            role_mentions = ", ".join(role.mention for role in roles)
            msg = await ctx.send(f"Az üdvözlő szerepkörök beállítva: {role_mentions}")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)

if config.moderation:
    @bot.command(name="add_restricted", aliases=["ar"])
    @commands.has_permissions(administrator=True)
    async def add_restricted(ctx, *words: str):
        if not words:
            msg = await ctx.send("Meg kell adnod legalább egy szót.")
            await asyncio.sleep(2)
            await msg.delete()
            return
        else:
            for word in words:
                database[str(ctx.guild.id)]["restricted_words"].append(word)
            print(database[str(ctx.guild.id)]["restricted_words"])
            save_database()
            msg = await ctx.send(f"A következő szavak rákerültek a tiltólistára: {" ".join(words)}")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)

    @bot.command(name="remove_restricted", aliases=["rs"])
    @commands.has_permissions(administrator=True)
    async def remove_restricted(ctx, *words: str):
        if not words:
            msg = await ctx.send("Meg kell adnod legalább egy szót.")
            await asyncio.sleep(2)
            await msg.delete()
            return
        else:
            for word in words:
                database[str(ctx.guild.id)]["restricted_words"].remove(word)
            save_database()
            msg = await ctx.send(f"A következő szavak lekerültek a tiltólistáról: {" ".join(words)}")
            await asyncio.sleep(2)
            await delete_message(ctx, msg)


    @bot.command(name="clear_restricted", aliases=["cr"])
    @commands.has_permissions(administrator=True)
    async def clear_restricted(ctx):
        database[str(ctx.guild.id)]["restricted_words"] = []
        save_database()
        msg = await ctx.send(f"A tiltólista törölve lett.")
        await asyncio.sleep(2)
        await delete_message(ctx, msg)

if config.systemmessage:
    @bot.command(name="system_message", aliases=["sm"])
    @commands.has_permissions(administrator=True)
    async def system_message(ctx, title=None, *message : str):
        if title is None:
            msg = await ctx.send("Meg kell adnod egy címet!")
            await asyncio.sleep(2)
            await delete_message(None, msg)
            return
        if not message:
            msg = await ctx.send("Meg kell adnod egy üzenetet!")
            await asyncio.sleep(2)
            await delete_message(None, msg)
            return

        await delete_message(ctx)

        msg = await ctx.send("Betöltés...")
        embed = discord.Embed(title=f"{ctx.guild.name}")

        embed.set_thumbnail(url=ctx.guild.icon.url)
        embed.add_field(name=title, value="".join(message), inline=False)
        await msg.edit(content=None, embed=embed)

## Events
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if config.moderation:
        restricted = False
        for word in database[str(message.guild.id)]['restricted_words']:
            if word in message.content.lower():
                restricted = True

        if restricted:
            await message.delete()
            msg = await message.channel.send(f"Az üzenet moderálva lett.")
            await asyncio.sleep(2)
            await delete_message(None, msg)

    await bot.process_commands(message)

@bot.event
async def on_member_join(member):
    guild = member.guild

    if config.welcome:
        if str(guild.id) in database and database[str(guild.id) ]['welcome_rls'] != None:
            roles = [member.guild.get_role(role_id) for role_id in database[str(guild.id) ]["welcome_rls"]]
            roles = [role for role in roles if role is not None]
            if roles:
                try:
                    await member.add_roles(*roles)
                except discord.Forbidden:
                    msg = await member.guild.get_channel.send(f"Nincs joga a botnak a rang hozzáadásához!")
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
async def on_guild_join(guild):
    ensure_db_structure(str(guild.id))

## Bot init
load_dotenv()
TOKEN = os.getenv("RIVALS_API_KEY")
if TOKEN is None:
    raise ValueError("Hiányzik a token.")
rivals_api = api.RivalsAPI(TOKEN)

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("Hiányzik a token.")

delete_all_files_in_folder()

try:
    signal.signal(signal.SIGINT, lambda signal, frame: on_shutdown_signal())
    bot.run(TOKEN)
except Exception as e:
    print(f"Hiba történt: {e}")

