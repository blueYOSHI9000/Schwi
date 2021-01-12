import json
import discord
from discord.ext import commands
import logging
import modules.activity as activity

#discord.py logging - not my own
logging.basicConfig(level=logging.WARNING)

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
    return

bot.run(token, bot=True, reconnect=True)