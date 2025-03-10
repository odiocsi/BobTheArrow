import discord
from discord.ext import commands
from discord.ui import Button, View
import config

class MusicView(View):
    def __init__(self, ctx, msg, playlist):
        super().__init__(timeout=None)
        self.__ctx = ctx
        self.__msg = msg
        self.__isPaused = False
        self.__playlist = playlist
        self.__loopstatus = ""

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
        if self.__ctx.voice_client.is_playing():
            self.__ctx.voice_client.pause()
        else:
            self.__ctx.voice_client.resume()
        self.__isPaused = not self.__isPaused

    async def __skip(self, interaction):
        await interaction.response.defer()
        if self.__ctx and self.__ctx.voice_client.is_playing():
            self.__ctx.voice_client.stop()

    async def __shuffle(self, interaction):
        await interaction.response.defer()
        self.__playlist.shuffle()

    async def __loop(self, interaction):
        await interaction.response.defer()
        self.__loopstatus = self.__playlist.loop()

    def __add_buttons(self):
        self.clear_items()
        self.add_item(self.__plpa_button)
        if not self.__playlist.isEmpty():
            self.add_item(self.__shuff_button)
            self.add_item(self.__skip_button)
        self.add_item(self.__loop_button)

    async def edit_message(self):
        embed = discord.Embed(title="Zenelejátszó", color=0xFF0000)

        if self.__playlist.isEmpty() and not self.__ctx.voice_client.is_playing() and not self.__isPaused:
           embed.add_field(name="Státusz", value="Jelenleg nem megy zene.", inline=False)
        else:
            if self.__isPaused:
                embed.add_field(name="Státusz", value=f"⏸️{self.__loopstatus}", inline=False)
            else:
                embed.add_field(name="Státusz", value=f"▶️{self.__loopstatus}", inline=False)

            if self.__playlist.current:
                embed.add_field(name="Jelenlegi zene", value=f"{self.__playlist.current['title']}", inline=False)
            else:
                embed.add_field(name="Jelenlegi zene", value="N/A", inline=False)

            embed.add_field(name="Lejásztási lista", value=f"{self.__playlist.tostring()}", inline=False)

        self.__add_buttons()
        await self.__msg.edit(content=None, embed=embed, view=self)


class ChoosingView(View):
    def __init__(self, msg, response, search_results):
        super().__init__(timeout=None)
        self.__msg = msg
        self.__resp = response
        self.__search_results = search_results
        self.__emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"]

        for i in range(5):
            button = Button(style=discord.ButtonStyle.secondary, label=f"{self.__emojis[i]}")
            button.callback = self.__create_callback(i)
            self.add_item(button)

    def __create_callback(self, i):
        async def callback(interaction: discord.Interaction):
            self.__resp.answer = i
            await interaction.response.defer()
            await self.__msg.delete()
        return callback

    async def edit_message(self):
        embed = discord.Embed(title="Találatok", color=0xFF0000)

        results = ""
        for i, item in enumerate(self.__search_results['entries']):
            results += f"{i+1}. {item['title']}\n"

        embed.add_field(name="Válassz egy zenét a listából:", value=results, inline=False)

        await self.__msg.edit(content=None, embed=embed, view=self)

class RivalsPlayerView(View):
    def __init__(self, msg, data, name, season):
        super().__init__(timeout=None)
        self.__msg = msg
        self.__data = data
        self.__name = name
        self.__season = season

    async def edit_message(self):
        string = f"{self.__name} rangsorolt statisztikái S{self.__season}"
        title = f"{string}{self.__calculate_spaces(string)}"
        embed = discord.Embed(title=title, color=0x800080)

        embed.set_thumbnail(url=self.__data['heroes'][0]['img_url'])

        embed.add_field(name="Rank", value=self.__data['rank'], inline=False)

        embed.add_field(name="Győzelmi arány", value=f"{self.__data['winrate']}%", inline=False)

        heroes_data = ""
        for hero in self.__data['heroes']:
            heroes_data += f"\n**{hero['name'].title()}**\nMeccsek: {hero['matches']}\nGyőzelmi arány: {hero['winrate']}%\nMVP/SVP: {hero['mvpsvp']}\nJátszott idő: {hero['playtime']} óra\n"
        embed.add_field(name=f"Top {len(self.__data['heroes'])} hős", value=heroes_data, inline=False)

        embed.add_field(name="Utoljára frissítve", value=self.__data['update'], inline=False)

        await self.__msg.edit(content=None, embed=embed, view=self)

    def __calculate_spaces(self, title):
        if (70-len(title)>0):
            return (70-len(title))*" \u200b"
        return ""

class RivalsMapView(View):
    def __init__(self, msg, data, name, season):
        super().__init__(timeout=None)
        self.__msg = msg
        self.__data = data
        self.__name = name
        self.__season = season

    async def edit_message(self):
        string = f"{self.__name} pálya statisztikái S{self.__season}"
        title = f"{string}{self.__calculate_spaces(string)}"
        embed = discord.Embed(title=title, color=0x800080)

        for m in self.__data['maps']:
            map_data = f"Meccsek: {m['matches']}\nGyőzelmi arány: {m['winrate']}"
            embed.add_field(name=m['name'], value=map_data, inline=False)

        embed.add_field(name="Utoljára frissítve", value=self.__data['update'], inline=False)

        await self.__msg.edit(content=None, embed=embed, view=self)

    def __calculate_spaces(self, title):
        if (50-len(title)>0):
            return (50-len(title))*" \u200b"
        return ""

class RivalsMatchupView(View):
    def __init__(self, msg, data, name, season, half):
        super().__init__(timeout=None)
        self.__msg = msg
        self.__data = data
        self.__name = name
        self.__season = season
        self.__half = half

    async def edit_message(self):
        embed = None
        if self.__half == 1:
            string = f"{self.__name} matchup statisztikái S{self.__season}"
            title = f"{string}{self.__calculate_spaces(string)}"
            embed = discord.Embed(title=title, color=0x800080)

            for h in self.__data['heroes'][:24]:
                map_data = f"Meccsek: {h['matches']}\nGyőzelmi arány: {h['winrate']}"
                embed.add_field(name=h['name'].title(), value=map_data, inline=False)


        elif self.__half == 2:
            string = f"{self.__name} matchup statisztikái S{self.__season}"
            title = f"{string}{self.__calculate_spaces(string)}"
            embed = discord.Embed(title=title, color=0x800080)
            for h in self.__data['heroes'][24:]:
                map_data = f"Meccsek: {h['matches']}\nGyőzelmi arány: {h['winrate']}"
                embed.add_field(name=h['name'].title(), value=map_data, inline=False)

        if len(self.__data['heroes']) < 25 and self.__half == 1:
            embed.add_field(name="Utoljára frissítve", value=self.__data['update'], inline=False)
        elif self.__half == 2:
            embed.add_field(name="Utoljára frissítve", value=self.__data['update'], inline=False)

        await self.__msg.edit(content=None, embed=embed, view=self)

    def __calculate_spaces(self, title):
        if (50-len(title)>0):
            return (50-len(title))*" \u200b"
        return ""

class CustomHelpCommand(commands.HelpCommand):
    async def send_bot_help(self, mapping):
        help_embed = discord.Embed(
            title="Bot Parancsok",
            description="Az elérhető parancsok listája.",
            color=0x00FF00
        )

        commands_info = {
            "play": {
                "description": "Zene lejátszása a csatornában.",
                "usage": "<prefix>play <cím/link/playlist>",
                "aliases": ["p"],
                "enabled": config.musicplayer,
            },
            "league": {
                "description": "League of Legends statisztikák lekérése",
                "usage": "<prefix>league",
                "aliases": ["lol"],
                "enabled": config.lolapi,
            },
            "rivals": {
                "description": "Marvel Rivals statisztikák lekérése",
                "usage": "<prefix>rivals <név> <szezon(0,1,1.5 ...)/update> <típus(üres,map,matchup)>",
                "aliases": ["rv"],
                "enabled": config.rivalsapi,
            },
            "clear": {
                "description": "Chat üzenetek törlése",
                "usage": "<prefix>clear <üzenetszám>",
                "aliases": ["cl"],
                "enabled": config.clear,
            },
            "set_channel": {
                "description": "Csatorna beállítása egy specifikus üzenethez.",
                "usage": "<prefix>set_channel <típus(music,rivals,lol,welcome)>",
                "aliases": ["sc"],
                "enabled": config.musicplayer or config.rivalsapi or config.lolapi or config.welcome,
            },
            "clear_channel": {
                "description": "Csatorna törlése egy specfikus üzenethez.",
                "usage": "<prefix>clear_channel <típus(music,rivals,lol,welcome)>",
                "aliases": ["cc"],
                "enabled": config.musicplayer or config.rivalsapi or config.lolapi or config.welcome,
            },
            "set_prefix": {
                "description": "Bot prefix beállítása.",
                "usage": "<prefix>set_prefix <prefix>",
                "aliases": ["sp"],
                "enabled": config.prefixchange,
            },
            "set_welcome_msg": {
                "description": "Üdvözlő üzenet beállítása.",
                "usage": "<prefix>set_welcome_msg <üzenet>",
                "aliases": ["swm"],
                "enabled": config.welcome,
            },
            "set_welcome_rls": {
                "description": "Csatlakozási rangok beállítása.",
                "usage": "<prefix>set_welcome_rls <rangok>",
                "aliases": ["swr"],
                "enabled": config.welcome,
            },
            "system_message" : {
                "description": "Rendszerüzenet küldése.",
                "usage": "<prefix>system_message <cím> <üzenet>",
                "aliases": ["sm"],
                "enabled": config.systemmessage,
            },
            "add_restricted" : {
                "description": "Tiltott szó hozzáadása.",
                "usage": "<prefix>add_restricted <szavak>",
                "aliases": ["ar"],
                "enabled": config.moderation
            },
            "remove_restricted" : {
                "description": "Tiltott szó törlése.",
                "usage": "<prefix>remove_restricted <szavak>",
                "aliases": ["rr"],
                "enabled": config.moderation
            },
            "clear_restricted" : {
                "description": "Tiltott szavak törlése.",
                "usage": "<prefix>clear_restricted",
                "aliases": ["cr"],
                "enabled": config.moderation
            }
        }

        command_info_list = []
        embed_field = ""
        for command, info in commands_info.items():
            if info["enabled"]:
                embed_field = f"**{command}**\n"
                embed_field += f"Rövidítés: {', '.join(info['aliases'])}\n"
                embed_field += f"Leírás: {info['description']}\n"
                embed_field += f"Használat: {info['usage']}\n"

                command_info_list.append(embed_field)


        current_embed = None
        char_count = 0
        for command_info in command_info_list:
            if current_embed is None:
                current_embed = discord.Embed(
                    title="Bot Parancsok",
                    description="Az elérhető parancsok listája.",
                    color=0x00FF00
                )
            if char_count + len(command_info) < 1024:
                current_embed.add_field(name="_____", value=command_info, inline=False)
                char_count += len(command_info)
            else:
                await self.context.send(embed=current_embed)
                current_embed = discord.Embed(
                    title="Bot Parancsok",
                    description="Az elérhető parancsok listája.",
                    color=0x00FF00
                )
                current_embed.add_field(name="_____", value=command_info, inline=False)
                char_count = len(command_info)

        if current_embed:
            await self.context.send(embed=current_embed)