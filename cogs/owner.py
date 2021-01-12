from discord.ext import commands

import json
import sys
import os
import time

from modules.log import log
import modules.activity as activity
from modules.misc import get_args
from modules.misc import is_owner

class Owner(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command(
        name='shutdown',
        description='Kills the bot',
        aliases=['quit', 'kill']
    )
    async def shutdown_command(self, ctx):
        author_ID = ctx.message.author.id
        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return

        user = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'

        await ctx.send(content=f"<@!{author_ID}> Shutting down...")

        await log(f'{user} used the command \'schwi.shutdown\'. Schwi is shutting down...', 'info', client=self.bot)

        # sleep for 1s so the log can be written to file in time
        time.sleep(1)

        sys.exit('Script exited by using \'schwi.shutdown\'')
        return

    @commands.command(
        name='reboot',
        description='Restarts the bot',
        aliases=['restart']
    )
    async def restart_command(self, ctx):
        author_ID = ctx.message.author.id
        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return

        user = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'

        await ctx.send(content=f"<@!{author_ID}> Rebooting...")

        await log(f'{user} used the command \'schwi.reboot\'. Schwi is restarting...\n', 'info', client=self.bot)

        # sleep for 1s so the log can be written to file in time
        time.sleep(1)

        os.execl(sys.executable, sys.executable, *sys.argv)
        return

    @commands.command(
        name='setstatus',
        description='Changes the bot\'s online status',
        aliases=['changestatus', 'updatestatus'],
        usage='<status (can be \'online\', \'idle\', \'dnd\', \'invisible\')>'
    )
    async def setstatus_command(self, ctx):
        author_ID = str(ctx.message.author.id)
        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return

        args = get_args(ctx)
        status = args[0].lower()

        if status in ('online', 'idle', 'dnd', 'invisible'):
            await activity.change_activity(status=status, client=self.bot)
            await ctx.send(content=f"<@!{author_ID}> Status was updated to **{status}**! (Note: If it doesn't update it might've got rate-limited, try again in a couple minutes in that case.)")
        else:
            await ctx.send(content=f"<@!{author_ID}> **{status}** was not a valid argument. Please use one of the following: 'online', 'idle', 'dnd', 'invisible' (without the apostrophes).")
        return

    @commands.command(
        name='setactivity',
        description='Changes the bot\'s activity',
        aliases=['changeactivity', 'updateactivity'],
        usage='<activity (can be \'PLAYING\', \'WATCHING\', \'LISTENING\', \'STREAMING\')> <activity name>'
    )
    async def setactivity_command(self, ctx):
        author_ID = str(ctx.message.author.id)
        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return
            
        args = get_args(ctx)
        atype = args[0].upper()
        name = ' '.join(args[1:])

        if atype in ('PLAYING', 'WATCHING', 'LISTENING', 'STREAMING'):
            await activity.change_activity(atype=atype, name=name, client=self.bot)
            await ctx.send(content=f"<@!{author_ID}> Activity was updated to **{atype} {name}**! (Note: If it doesn't update it might've got rate-limited, try again in a couple minutes in that case.)")
        else:
            await ctx.send(content=f"<@!{author_ID}> **{atype}** was not a valid argument. Please use one of the following: 'PLAYING', 'WATCHING', 'LISTENING', 'STREAMING' (without the apostrophes).")
        return

    @commands.command(
        name='setpresence',
        description='Changes the bot\'s presence (online status & activity)',
        aliases=['changepresence', 'updatepresence'],
        usage='<status (can be \'online\', \'idle\', \'dnd\', \'invisible\')> <activity (can be \'PLAYING\', \'WATCHING\', \'LISTENING\', \'STREAMING\')> <activity name>'
    )
    async def setpresence_command(self, ctx):
        author_ID = str(ctx.message.author.id)
        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return
            
        args = get_args(ctx)
        status = args[0].lower()
        atype = args[1].upper()
        name = ' '.join(args[2:])

        if (status not in ('online', 'idle', 'dnd', 'invisible')):
            await ctx.send(content=f"<@!{author_ID}> **{status}** was not a valid argument. Please use one of the following: 'online', 'idle', 'dnd', 'invisible' (without the apostrophes).")
            return

        if (atype not in ('PLAYING', 'WATCHING', 'LISTENING', 'STREAMING')):
            await ctx.send(content=f"<@!{author_ID}> **{atype}** was not a valid argument. Please use one of the following: 'PLAYING', 'WATCHING', 'LISTENING', 'STREAMING' (without the apostrophes).")
            return

        await activity.change_activity(status=status, atype=atype, name=name, client=self.bot)
        await ctx.send(content=f"<@!{author_ID}> Presence was updated to **{status}** - **{atype} {name}**! (Note: If it doesn't update it might've got rate-limited, try again in a couple minutes in that case.)")
        return


def setup(bot):
    bot.add_cog(Owner(bot))
    # Adds the Owner commands to the bot