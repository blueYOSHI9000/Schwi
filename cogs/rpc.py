import discord
from discord.ext import commands

import sys
import os
import json
import time

from modules.log import log
from modules.misc import get_args
from modules.misc import is_owner
import modules.convert_time as t

class RPC(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        name='startrpc',
        description='Start RPC',
        usage='<entry name>',
        hidden=True
    )
    async def startrpc_command(self, ctx):
        author_ID = str(ctx.message.author.id)
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return

        name = get_args(ctx, combine=True).strip()
        rpc_entries = json.load(open('settings/database.json', 'r'))['RPC']
        result = False

        for r in rpc_entries:
            # break out of loop if result is found
            if result != False:
                break

            if r['name'] == name:
                result = r
                break
            for a in r['aliases']:
                if a == name:
                    result = r
                    break

        if result == False:
            await ctx.send(content=f'<@!{author_ID}> Could not find a RPC entry with the name "**{name}**".')
            return

        with open('settings/database.json', 'r+') as f:
            db = json.load(f)

            db['general']['lastRPCUsed'] = result['name']
            db['general']['RPCCommands'] = []
            db['general']['RPCStartedAt'] = t.struct_to_ms(t.get_current_time())

            # reset file position to the beginning - stackoverflow copy, dont ask
            f.seek(0)
            json.dump(db, f, indent=4)
            f.truncate()

        if json.load(open('settings/config.json', 'r'))['RPC']['autoRestart'] == True:
            await ctx.send(content=f'<@!{author_ID}> Restarting now to load the RPC entry "**{name}**"...')
            await log(f'{user} loaded the RPC entry "{name}". Schwi is now rebooting...', 'info')

            # sleep for 1s so the log can be written to file in time
            time.sleep(1)

            os.execl(sys.executable, sys.executable, *sys.argv)
        else:
            await ctx.send(content=f'<@!{author_ID}> The RPC entry "**{name}**" will be loaded the next time Schwi is started. Use {prefix}reboot to reboot Schwi now.')
            await log(f'{user} loaded the RPC entry "{name}".', 'info')
        return

    @commands.command(
        name='stoprpc',
        description='Stops RPC',
        hidden=True
    )
    async def stoprpc_command(self, ctx):
        author_ID = str(ctx.message.author.id)
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return

        with open('settings/database.json', 'r+') as f:
            database = json.load(f)

            database['general']['RPCCommands'].append({'type': 'quit'})
            database['general']['lastRPCUsed'] = False

            # reset file position to the beginning - stackoverflow copy, dont ask
            f.seek(0)
            json.dump(database, f, indent=4)
            f.truncate()

        await ctx.send(content=f'<@!{author_ID}> RPC will be quit. RPC can only be updated during every interval so it might take a while.')
        await log(f'{user} quit RPC.', 'info')
        return

    @commands.command(
        name='resetrpctime',
        description='Resets the RPC start time',
        hidden=True
    )
    async def stoprpc_command(self, ctx):
        author_ID = str(ctx.message.author.id)
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        if not is_owner(author_ID):
            await ctx.send(content=f"<@!{author_ID}> Owner commands can only be executed by owners.")
            await log('Owner command cannot be executed by non-owners.', 'warn', client=self.bot)
            return

        with open('settings/database.json', 'r+') as f:
            database = json.load(f)

            db['general']['RPCStartedAt'] = t.struct_to_ms(t.get_current_time())

            # reset file position to the beginning - stackoverflow copy, dont ask
            f.seek(0)
            json.dump(database, f, indent=4)
            f.truncate()

        await ctx.send(content=f'<@!{author_ID}> The time got reset to the current time. RPC can only be updated during every interval so it might take a while to display.')
        await log(f'{user} reset RPC time.', 'spamInfo')
        return


def setup(bot):
    bot.add_cog(RPC(bot))
    # Adds the RPC commands to the bot