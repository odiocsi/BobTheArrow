import os
from dotenv import load_dotenv
import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.messages = True 
intents.message_content = True  
bot = commands.Bot(command_prefix=".", intents=intents)
allowed_channel_id = None

@bot.event
async def on_ready():
    print('A bot elindult.')

@bot.command()
async def test(ctx):
    await ctx.send("Hello World!")



@bot.command()
@commands.has_permissions(administrator=True)
async def set_channel(ctx, channel: discord.TextChannel):
    global allowed_channel_id
    allowed_channel_id = channel.id  # Store the channel ID
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


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    raise ValueError("Hiányzik a token.")
    
try:
    bot.run(TOKEN)
except:
    raise ValueError("Hibás token.")