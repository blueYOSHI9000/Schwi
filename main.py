import discord
from discord.ext import tasks, commands

import logging
#discord.py logging - not my own
logging.basicConfig(level=logging.WARNING)

import threading
import asyncio
import json
import time

import modules.activity as activity
import modules.rss as rss
from modules.log import log

config = json.load(open('settings/config.json', 'r'))
token = json.load(open('settings/token.json', 'r'))['token']

def get_prefix(client, message):
    prefixes = config['bot']['prefix']

    # Allow users to @mention the bot instead of using a prefix when using a command.
    # copy-paste from tutorial, no idea what it actually does
    return commands.when_mentioned_or(*prefixes)(client, message)

bot = commands.Bot(
    command_prefix=get_prefix,
    description=' *   .  *  .  \'  * . *   \' .  * \'  . *\n \'  *  .  -= a dumb RSS bot =-  .  * .\n* .   *  \' .  * .  \' .  *  \' *  .  .  \n',
    owner_ids=config['bot']['owners'],
    case_insensitive=True
)
"""original for easy editing - I hope this is only used for the help command...
 *   .  *  .  '  * . *   ' .  * '  . *
 '  *  .  -= a dumb RSS bot =-  .  * .
* .   *  ' .  * .  ' .  *  ' *  .  .  
"""

cogs = ['cogs.basic', 'cogs.owner', 'cogs.debug']

@bot.event
async def on_ready():
    await log(f'Logged in as {bot.user}', 'info', client=bot)

    await activity.change_activity(client = bot)

    #load all bot commands
    for cog in cogs:
        bot.load_extension(cog)

    background_task()
    return

interval = config['rss']['interval'] * 60
# make sure interval is bigger than 10min
if interval < 600:
    interval = 600

class background_task(commands.Cog):
    def __init__(self):
        self.set_interval.start()

    @tasks.loop(seconds=interval)
    async def set_interval(self):
        await rss.scan_all_feeds(client=bot)

bot.run(token, bot=True, reconnect=True)