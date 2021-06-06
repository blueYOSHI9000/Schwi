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
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]

        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log(f"Owner command cannot be executed by non-owners. ({prefix}shutdown used by {user}", 'warn', client=self.bot)
            return

        user = f"{ctx.message.author.name}#{ctx.message.author.discriminator}"

        await ctx.send(content=f"<@!{author_ID}> Shutting down...")

        await log(f"{user} used the command '{prefix}shutdown'. Schwi is shutting down...", 'info', client=self.bot)

        # sleep for 1s so the log can be written to file in time
        time.sleep(1)

        sys.exit(f"Script exited by using '{prefix}shutdown'")
        return

    @commands.command(
        name='reboot',
        description='Restarts the bot',
        aliases=['restart']
    )
    async def restart_command(self, ctx):
        author_ID = ctx.message.author.id
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]

        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log(f"Owner command cannot be executed by non-owners. ({prefix}reboot used by {user})", 'warn', client=self.bot)
            return

        user = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'

        await ctx.send(content=f"<@!{author_ID}> Rebooting...")

        await log(f"{user} used the command '{prefix}reboot'. Schwi is restarting...\n", 'info', client=self.bot)

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
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]

        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log(f"Owner command cannot be executed by non-owners. ({prefix}setstatus used by {user}", 'warn', client=self.bot)
            return

        args = get_args(ctx)
        status = args[0].lower()

        if status in ('online', 'idle', 'dnd', 'invisible'):
            await activity.change_activity(status=status, client=self.bot)

            await log(f"Online status was updated to '{status}' by {user}", 'info', client=self.bot)
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
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]

        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log(f'Owner command cannot be executed by non-owners. ({prefix}setactivity used by {user}', 'warn', client=self.bot)
            return
            
        args = get_args(ctx)
        atype = args[0].upper()
        name = ' '.join(args[1:])

        if atype in ('PLAYING', 'WATCHING', 'LISTENING', 'STREAMING'):
            await activity.change_activity(atype=atype, name=name, client=self.bot)

            await log(f"Activity was updated to '{atype} {name}' by {user}", 'info', client=self.bot)
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
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]

        if not is_owner(author_ID):
            await ctx.send(content=f'<@!{author_ID}> Owner commands can only be executed by owners.')
            await log(f"Owner command cannot be executed by non-owners. ({prefix}setpresence used by {user}", 'warn', client=self.bot)
            return
            
        args = get_args(ctx)

        if len(args) < 3:
            await ctx.send(content=f"<@!{author_ID}> Not enough arguments. Use `{prefix}setpresence <status> <activity> <activity name>`.")
            return

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

        await log(f"Presence was updated to '{status} - {atype} {name}' by {user}", 'info', client=self.bot)
        await ctx.send(content=f"<@!{author_ID}> Presence was updated to **{status}** - **{atype} {name}**! (Note: If it doesn't update it might've got rate-limited, try again in a couple minutes in that case.)")
        return

    @commands.command(
        name='delayscan',
        description='Delays the next scan by the amount of hours specified',
        usage='<hours>'
    )
    async def delayscan_command(self, ctx):
        author_ID = str(ctx.message.author.id)
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]

        args = get_args(ctx)

        try:
            args[0]
        except IndexError:
            await ctx.send(content=f"<@!{author_ID}> Missing argument. Use `{prefix}delayscan <hours>`.")
            return

        if args[0].isdigit() == False:
            await ctx.send(content=f"<@!{author_ID}> Invalid argument. Use `{prefix}delayscan <hours>`.")
            return

        args[0] = int(args[0])
        
        with open('settings/database.json', 'r+') as f:
            database = json.load(f)
            database['general']['lastChecked'] = database['general']['lastChecked'] + (args[0] * 3600000)

            # reset file position to the beginning - stackoverflow copy, dont ask
            f.seek(0)
            json.dump(database, f, indent=4)
            f.truncate()

        await log(f"Next scan got delayed by {args[0]} hours.", 'info', client=self.bot)
        await ctx.send(content=f"<@!{author_ID}> Next scan successfully delayed by {args[0]} hours.")
        return


def setup(bot):
    bot.add_cog(Owner(bot))
    # Adds the Owner commands to the bot