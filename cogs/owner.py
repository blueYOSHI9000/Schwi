from discord.ext import commands
import json
import sys
import os
import time
from scripts.log import log

ownerID = json.load(open('settings/config.json', 'r'))['bot']['owner']

# New - The Cog class must extend the commands.Cog class
class Owner(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        

    @commands.command(
        name='kill',
        description='Kills the bot',
        aliases=['quit', 'shutdown'],
        hidden=True
    )
    async def kill_command(self, ctx):
        authorID = ctx.message.author.id
        if str(authorID) != ownerID:
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return

        user = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'

        await ctx.send(content=f"<@!{authorID}> Shutting down...")

        await log(f'{user} used the command \'schwi.kill\'. Schwi is shutting down...', 'info', client=self.bot)

        # sleep for 1s so the log can be written to file in time
        time.sleep(1)

        sys.exit('Script exited by using \'schwi.kill\'')
        return

    @commands.command(
        name='restart',
        description='Restarts the bot',
        aliases=['reboot'],
        hidden=True
    )
    async def restart_command(self, ctx):
        authorID = ctx.message.author.id
        if str(authorID) != ownerID:
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return

        user = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'

        await ctx.send(content=f"<@!{authorID}> Rebooting...")

        await log(f'{user} used the command \'schwi.restart\'. Schwi is restarting...\n', 'info', client=self.bot)

        # sleep for 1s so the log can be written to file in time
        time.sleep(1)

        os.execl(sys.executable, sys.executable, *sys.argv)
        return

    @commands.command(
        name='logmsg',
        description='Logs a message in the console',
        aliases=['logctx'],
        hidden=True
    )
    async def logmsg_command(self, ctx):
        authorID = str(ctx.message.author.id)
        if authorID != ownerID:
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return

        print(f'\n{ctx}\n\n==============================\n\n{ctx.message}')
        return


def setup(bot):
    bot.add_cog(Owner(bot))
    # Adds the Owner commands to the bot