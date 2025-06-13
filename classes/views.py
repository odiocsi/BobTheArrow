import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import config
from locales import languages
from classes.shared import database, json_path

def get_locale(guild_id):
    lang = database[str(guild_id)]["lang"]
    return languages.get_dict(lang)
class MusicView(View):
    def __init__(self, ctx, msg, playlist, guild):
        super().__init__(timeout=None)
        self.__ctx = ctx
        self.__msg = msg
        self.__isPaused = False
        self.__playlist = playlist
        self.__loopstatus = ""
        self.__guild = guild

        self.__plpa_button = Button(style=discord.ButtonStyle.secondary, label="⏯️")
        self.__plpa_button.callback = self.__plpa
        self.__shuff_button = Button(style=discord.ButtonStyle.secondary, label="🔀")
        self.__shuff_button.callback = self.__shuffle
        self.__skip_button = Button(style=discord.ButtonStyle.secondary, label="⏩")
        self.__skip_button.callback = self.__skip
        self.__loop_button = Button(style=discord.ButtonStyle.secondary, label="🔁")
        self.__loop_button.callback = self.__loop

        self.__add_buttons()

    async def __plpa(self, interaction):
        await interaction.response.defer()
        if not self.__ctx.voice_client:
            return
        if self.__ctx.voice_client.is_playing():
            self.__ctx.voice_client.pause()
        else:
            self.__ctx.voice_client.resume()
        self.__isPaused = not self.__isPaused

    async def __skip(self, interaction):
        await interaction.response.defer()
        if not self.__ctx.voice_client:
            return
        if self.__ctx and self.__ctx.voice_client.is_playing():
            self.__ctx.voice_client.stop()

    async def __shuffle(self, interaction):
        await interaction.response.defer()
        if not self.__ctx.voice_client:
            return
        self.__playlist.shuffle()

    async def __loop(self, interaction):
        await interaction.response.defer()
        self.__loopstatus = self.__playlist.loop()

    def __add_buttons(self):
        self.clear_items()
        if self.__playlist.current:
            self.add_item(self.__plpa_button)
            self.add_item(self.__skip_button)
            self.add_item(self.__loop_button)
        if not self.__playlist.isEmpty():
            self.add_item(self.__shuff_button)

    async def edit_message(self):
        locale = get_locale(self.__guild.id)
        embed = discord.Embed(title=locale.musicplayer, color=0xFF0000)

        if self.__playlist.isEmpty() and (not self.__ctx.voice_client or not self.__ctx.voice_client.is_playing()) and not self.__isPaused:
           embed.add_field(name=locale.status, value="Jelenleg nem megy zene.", inline=False)
        else:
            if self.__isPaused:
                embed.add_field(name=locale.status, value=f"⏸️{self.__loopstatus}", inline=False)
            else:
                embed.add_field(name=locale.status, value=f"▶️{self.__loopstatus}", inline=False)

            if self.__playlist.current:
                embed.add_field(name=locale.current_song, value=f"{self.__playlist.current['title']}", inline=False)
            else:
                embed.add_field(name=locale.current_song, value="N/A", inline=False)

            embed.add_field(name=locale.playlist, value=f"{self.__playlist.tostring()}", inline=False)

        self.__add_buttons()
        await self.__msg.edit(content=None, embed=embed, view=self)


class ChoosingView(View):
    def __init__(self, msg, response, search_results, guild):
        super().__init__(timeout=None)
        self.__msg = msg
        self.__resp = response
        self.__search_results = search_results
        self.__emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]
        self.__guild = guild

        for i in range(5):
            button = Button(style=discord.ButtonStyle.secondary, label=f"{self.__emojis[i]}")
            button.callback = self.__create_callback(i)
            self.add_item(button)

    def __create_callback(self, i):
        async def callback(interaction: discord.Interaction):
            self.__resp.answer = i
            await interaction.response.defer()
            try:
                await self.__msg.delete()
            except:
                print("the message deletion failed")
        return callback

    async def edit_message(self):
        locale = get_locale(self.__guild.id)
        embed = discord.Embed(title=locale.results, color=0xFF0000)

        results = ""
        for i, item in enumerate(self.__search_results['entries']):
            results += f"{i+1}. {item['title']}\n"

        embed.add_field(name=locale.choose_a_song, value=results, inline=False)

        await self.__msg.edit(content=None, embed=embed, view=self)

class RivalsPlayerView(View):
    def __init__(self, msg, data, name, season, guild):
        super().__init__(timeout=None)
        self.__msg = msg
        self.__data = data
        self.__name = name
        self.__season = season
        self.__guild = guild

    async def edit_message(self):
        locale = get_locale(self.__guild.id)
        string = f"{self.__name}{locale.ranked_statistics} S{self.__season}"
        title = f"{string}{self.__calculate_spaces(string)}"
        embed = discord.Embed(title=title, color=0x800080)

        embed.set_thumbnail(url=self.__data['heroes'][0]['img_url'])

        embed.add_field(name=locale.rank, value=self.__data['rank'], inline=False)

        embed.add_field(name=locale.winrate, value=f"{self.__data['winrate']}%", inline=False)

        heroes_data = ""
        for hero in self.__data['heroes']:
            heroes_data += f"\n**{hero['name'].title()}**\n{locale.matches}: {hero['matches']}\n{locale.winrate}: {hero['winrate']}%\nMVP/SVP: {hero['mvpsvp']}\nJátszott idő: {hero['playtime']} óra\n"
        embed.add_field(name=f"Top {len(self.__data['heroes'])}{locale.hero}", value=heroes_data, inline=False)

        embed.add_field(name=locale.last_updated, value=self.__data['update'], inline=False)

        await self.__msg.edit(content=None, embed=embed, view=self)

    def __calculate_spaces(self, title):
        if (70-len(title)>0):
            return (70-len(title))*" \u200b"
        return ""

class RivalsMapView(View):
    def __init__(self, msg, data, name, season, guild):
        super().__init__(timeout=None)
        self.__msg = msg
        self.__data = data
        self.__name = name
        self.__season = season
        self.__guild = guild

    async def edit_message(self):
        locale = get_locale(self.__guild.id)
        string = f"{self.__name}{locale.map_statistics} S{self.__season}"
        title = f"{string}{self.__calculate_spaces(string)}"
        embed = discord.Embed(title=title, color=0x800080)

        for m in self.__data['maps']:
            map_data = f"{locale.matches}: {m['matches']}\n{locale.winrate}: {m['winrate']}"
            embed.add_field(name=m['name'], value=map_data, inline=False)

        embed.add_field(name=locale.last_updated, value=self.__data['update'], inline=False)

        await self.__msg.edit(content=None, embed=embed, view=self)

    def __calculate_spaces(self, title):
        if (50-len(title)>0):
            return (50-len(title))*" \u200b"
        return ""

class RivalsMatchupView(View):
    def __init__(self, msg, data, name, season, half, guild):
        super().__init__(timeout=None)
        self.__msg = msg
        self.__data = data
        self.__name = name
        self.__season = season
        self.__half = half
        self.__guild = guild

    async def edit_message(self):
        locale = get_locale(self.__guild.id)
        embed = None
        if self.__half == 1:
            string = f"{self.__name}{locale.matchup_statistics} S{self.__season}"
            title = f"{string}{self.__calculate_spaces(string)}"
            embed = discord.Embed(title=title, color=0x800080)

            for h in self.__data['heroes'][:24]:
                map_data = f"{locale.matches}: {h['matches']}\n{locale.winrate}: {h['winrate']}"
                embed.add_field(name=h['name'].title(), value=map_data, inline=False)


        elif self.__half == 2:
            string = f"{self.__name}{locale.matchup_statistics} S{self.__season}"
            title = f"{string}{self.__calculate_spaces(string)}"
            embed = discord.Embed(title=title, color=0x800080)
            for h in self.__data['heroes'][24:]:
                map_data = f"{locale.matches}: {h['matches']}\n{locale.winrate}: {h['winrate']}"
                embed.add_field(name=h['name'].title(), value=map_data, inline=False)

        if len(self.__data['heroes']) < 25 and self.__half == 1:
            embed.add_field(name=locale.last_updated, value=self.__data['update'], inline=False)
        elif self.__half == 2:
            embed.add_field(name=locale.last_updated, value=self.__data['update'], inline=False)

        await self.__msg.edit(content=None, embed=embed, view=self)

    def __calculate_spaces(self, title):
        if (50-len(title)>0):
            return (50-len(title))*" \u200b"
        return ""

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        guild = self.context.guild
        locale = get_locale(guild.id)
        help_embed = discord.Embed(
            title=locale.bot_commands,
            description=locale.list_of_commands,
            color=0x00FF00
        )

        lang_options = str(languages.get_keys()).strip("[\\]'")
        commands_info = {
            "join": {
                "description": locale.join_desc,
                "usage": f"<prefix>join {locale.join_usage}",
                "aliases": ["j"],
                "enabled": config.musicplayer,
            },
            "leave": {
                "description": locale.leave_desc,
                "usage": f"<prefix>leave {locale.leave_usage}",
                "aliases": ["l"],
                "enabled": config.musicplayer,
            },
            "play": {
                "description": locale.play_desc,
                "usage": f"<prefix>play {locale.play_usage}",
                "aliases": ["p"],
                "enabled": config.musicplayer,
            },
            "league": {
                "description": locale.lol_desc,
                "usage": f"<prefix>league {locale.lol_usage}",
                "aliases": ["lol"],
                "enabled": config.lolapi,
            },
            "rivals": {
                "description": locale.rivals_desc,
                "usage": f"<prefix>rivals {locale.rivals_usage}",
                "aliases": ["rv"],
                "enabled": config.rivalsapi,
            },
            "clear": {
                "description": locale.chat_desc,
                "usage": f"<prefix>clear {locale.chat_usage}",
                "aliases": ["cl"],
                "enabled": config.clear,
            },
            "set_channel": {
                "description": locale.set_channel_desc,
                "usage": f"<prefix>set_channel {locale.set_channel_usage}",
                "aliases": ["sc"],
                "enabled": config.musicplayer or config.rivalsapi or config.lolapi or config.welcome,
            },
            "clear_channel": {
                "description": locale.clear_channel_desc,
                "usage": f"<prefix>clear_channel {locale.clear_channel_usage}",
                "aliases": ["cc"],
                "enabled": config.musicplayer or config.rivalsapi or config.lolapi or config.welcome,
            },
            "set_prefix": {
                "description": locale.set_prefix_desc,
                "usage": f"<prefix>set_prefix {locale.set_prefix_usage}",
                "aliases": ["sp"],
                "enabled": config.prefixchange,
            },
            "set_welcome_msg": {
                "description": locale.set_welcome_msg_desc,
                "usage": f"<prefix>set_welcome_msg {locale.set_welcome_msg_usage}",
                "aliases": ["swm"],
                "enabled": config.welcome,
            },
            "set_welcome_rls": {
                "description": locale.set_welcome_rls_desc,
                "usage": f"<prefix>set_welcome_rls {locale.set_welcome_rls_usage}",
                "aliases": ["swr"],
                "enabled": config.welcome,
            },
            "system_message": {
                "description": locale.system_message_desc,
                "usage": f"<prefix>system_message {locale.system_message_usage}",
                "aliases": ["sm"],
                "enabled": config.systemmessage,
            },
            "add_restricted": {
                "description": locale.add_restricted_desc,
                "usage": f"<prefix>add_restricted {locale.add_restricted_usage}",
                "aliases": ["ar"],
                "enabled": config.moderation,
            },
            "remove_restricted": {
                "description": locale.remove_restricted_desc,
                "usage": f"<prefix>remove_restricted {locale.remove_restricted_usage}",
                "aliases": ["rr"],
                "enabled": config.moderation,
            },
            "clear_restricted": {
                "description": locale.clear_restricted_desc,
                "usage": f"<prefix>clear_restricted {locale.clear_restricted_usage}",
                "aliases": ["cr"],
                "enabled": config.moderation,
            },
            "set_language": {
                "description": locale.set_language_desc,
                "usage": f'<prefix>set_language {locale.set_language_usage}{lang_options}>',
                "aliases": ["sl"],
                "enabled": config.setlang,
            }
        }

        command_info_list = []
        embed_field = ""
        for command, info in commands_info.items():
            if info["enabled"]:
                embed_field = f"**{command}**\n"
                embed_field += f"{locale.alias}{', '.join(info['aliases'])}\n"
                embed_field += f"{locale.description}{info['description']}\n"
                embed_field += f"{locale.usage}{info['usage']}\n"

                command_info_list.append(embed_field)


        current_embed = None
        char_count = 0
        for command_info in command_info_list:
            if current_embed is None:
                current_embed = discord.Embed(
                    title=locale.bot_commands,
                    description=locale.list_of_commands,
                    color=0x00FF00
                )
            if char_count + len(command_info) < 1024:
                current_embed.add_field(name="_____", value=command_info, inline=False)
                char_count += len(command_info)
            else:
                await self.context.send(embed=current_embed)
                current_embed = discord.Embed(
                    title=locale.bot_commands,
                    description=locale.list_of_commands,
                    color=0x00FF00
                )
                current_embed.add_field(name="_____", value=command_info, inline=False)
                char_count = len(command_info)

        if current_embed:
            await self.context.send(embed=current_embed)