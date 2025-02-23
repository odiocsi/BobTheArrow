import discord
from discord.ui import Button, View

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