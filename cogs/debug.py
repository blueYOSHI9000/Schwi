import discord
from discord.ext import commands

import json
import sys
import os
import time

from modules.log import log
import modules.activity as activity
from modules.misc import get_args
from modules.misc import is_owner

class Debug(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        name='logmsg',
        description='Logs a message in the console',
        aliases=['logctx'],
        hidden=True
    )
    async def logmsg_command(self, ctx):
        author_ID = str(ctx.message.author.id)
        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return

        print(f'\n{ctx}\n\n==============================\n\n{ctx.message}')

        #print(f'\n\n{dir(ctx.author)}\n\n')
        return


def setup(bot):
    bot.add_cog(Debug(bot))
    # Adds the Debug commands to the bot