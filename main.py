import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import urllib.request


#run load_dotenv and provide discord token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename="moonbot.log", encoding='utf-8', mode='w')

# edits the 'intents' variable from 'discord' and enables intents
intents = discord.Intents.default()
intents.members = True
intents.message_content= True

# edits the 'Bot' variable under 'commands' and saves it to bot
bot = commands.Bot(command_prefix='*', intents=intents)

@bot.event
async def on_ready():
    print(f"'Moonbot' connected to discord and online.")

@bot.command()
async def commands(ctx):
    await ctx.send(f"These are Moonbots enabled commands | "
                   f"**gameservers:** outputs all hosted server names | "
                   f"**gameservers name:** outputs connection IP and port | "
                   f"**commands:** lists all enabled commands")

@bot.command()
async def gameservers(ctx):
    await ctx.send(f"Game servers: Valheim, tModLoader")

external_ip = urllib.request.urlopen('https://api.ipify.org').read().decode('utf8')
@bot.command()
async def valheim(ctx):
    await ctx.send(f"Valheim server connection info: **IP:** {external_ip} | **Port:** 2456")

@bot.command()
async def tModLoader(ctx):
    await ctx.send(f"tModLoader server connection info: **IP:** {external_ip} | **Port:** 7777")





#runs the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)


