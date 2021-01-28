import discord
from discord.ext import tasks, commands

import logging
#discord.py logging - not my own
logging.basicConfig(level=logging.WARNING)

from pypresence import Presence

import json
import time

import modules.activity as activity
import modules.rss as rss
from modules.log import log, reglog
import modules.richpresence as rpc

config = json.load(open('settings/config.json', 'r'))
token = json.load(open('settings/token.json', 'r'))['token']
rpc_used = rpc.get_client_id()

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

cogs = ['cogs.basic', 'cogs.feeds', 'cogs.owner', 'cogs.rpc', 'cogs.debug']

@bot.event
async def on_ready():
    await log(f'Logged in as {bot.user}', 'info', client=bot)

    await activity.change_activity(client = bot)

    #load all bot commands
    for cog in cogs:
        bot.load_extension(cog)

    background_task()
    return


# Discord Rich Presence

# Can't log because not awaited and can't await because not inside a function ._.
if rpc_used != False:
    reglog('Start Rich Presence...', 'info')

    try:
        pypresence_RPC = Presence(rpc_used, loop=bot.loop)
        pypresence_RPC.connect()
    except:
        reglog('Discord is not open, turning off Rich Presence.', 'warn')
        rpc_used = False
        with open('settings/database.json', 'r+') as f:
            database = json.load(f)

            database['general']['lastRPCUsed'] = False

            # reset file position to the beginning - stackoverflow copy, dont ask
            f.seek(0)
            json.dump(database, f, indent=4)
            f.truncate()
else:
    reglog('Skip starting Rich Presence', 'info')


# Background Tasks

rss_interval = config['rss']['interval'] * 60
# make sure interval is bigger than 10min
if rss_interval < 600:
    rss_interval = 600

rpc_interval = config['RPC']['interval'] * 60
# make sure interval is bigger than 1min
if rpc_interval < 60:
    rpc_interval = 60

class background_task(commands.Cog):
    def __init__(self):
        self.rss_background_task.start()
        if rpc_used != False:
            self.rpc_background_task.start()

    @tasks.loop(seconds=rss_interval)
    async def rss_background_task(self):
        await rss.scan_all_feeds(client=bot)

    @tasks.loop(seconds=rpc_interval)
    async def rpc_background_task(self):
        # use try except as pypresence (or rather asyncio within it) seems to throw an error
        # despite throwing an error, it still updates the RPC perfectly fine though
        try:
            reglog('Update rich presence...', 'spamInfo')

            code = rpc.update_rpc()
            #print(code)
            exec(code)
        except RuntimeError:
            pass

bot.run(token, bot=True, reconnect=True)