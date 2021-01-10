import json
import discord
from discord.ext import commands
import logging

#discord.py logging - not my own
logging.basicConfig(level=logging.WARNING)

from scripts.log import log

config = json.load(open('settings/config.json', 'r'))
token = json.load(open('settings/token.json', 'r'))['token']

def get_prefix(client, message):
    prefixes = config['bot']['prefix']

    # Allow users to @mention the bot instead of using a prefix when using a command.
    # copy-paste from tutorial, no idea what it actually does
    return commands.when_mentioned_or(*prefixes)(client, message)

bot = commands.Bot(
    command_prefix=get_prefix,
    description='-= A dumb RSS bot =-',
    owner_id=config['bot']['owner'],
    case_insensitive=True
)

cogs = ['cogs.basic']
cogs = ['cogs.owner']

@bot.event
async def on_ready():
    await log(f'Logged in as {bot.user} - {bot.user.id}', 'info', client=bot)
    #load all bot commands
    for cog in cogs:
        bot.load_extension(cog)
    return

bot.run(token, bot=True, reconnect=True)