from discord.ext import commands
from discord import utils

import json

from modules.misc import get_args
import modules.misc as misc
import modules.manage_feeds as manage_feeds
from modules.log import log

class Feeds(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        name='add',
        description='Add a feed',
        usage='<channel> <url> <name>'
    )
    async def add_command(self, ctx):
        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        args = get_args(ctx)

        await log(f'{prefix}add executed.', 'spamInfo')
        
        user_permissions = ctx.message.author.guild_permissions
        if await misc.check_permission(ctx=ctx, required='editFeeds', user=user_permissions, author_ID=author_ID) == False:
            return

        # make sure arguments exists and are valid
        try:
            if args[0].startswith('<#'):
                channel = self.bot.get_channel(int(args[0][2:-1]))
            else:
                await ctx.send(content=f'<@!{author_ID}> Invalid channel. Use `{prefix}add <channel> <url> <name>`')
                return

            # check if channel is valid
            if await misc.is_valid_channel(ctx=ctx, channel=channel, author_ID=author_ID, command=f'{prefix}list [channel]') == False:
                return

            url = args[1]
            name = ' '.join(args[2:])
        except IndexError:
            await ctx.send(content=f'<@!{author_ID}> Invalid arguments. Use `{prefix}add <channel> <url> <name>`')
            return

        result = manage_feeds.add_feed(channel=channel, url=url, name=name)

        if result == 'added':
            await ctx.send(content=f'<@!{author_ID}> **{name}** was successfully added to <#{channel.id}>!')
            await log(f'**{name}** was added to <#{channel.id}>.', 'info', client=self.bot)
        elif result == 'exists':
            await ctx.send(content=f'<@!{author_ID}> **{name}** is already registered in <#{channel.id}>. Use `{prefix}edit <name>` to edit the entry.')
            await log(f'**{name}** was already added to <#{channel.id}>.', 'spamInfo', client=self.bot)
        else:
            await ctx.send(content=f'<@!{author_ID}> Something went wrong while adding **{name}**, it might\'ve been added, it might\'ve not. Use {prefix}list <#{channel}> to check whether it has been added or not.')

        return

    @commands.command(
        name='remove',
        description='Remove a feed with a certain name',
        aliases=['rm'],
        usage='<name>'
    )
    async def remove_command(self, ctx):
        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        text = get_args(ctx, combine=True)

        await log(f'{prefix}remove executed.', 'spamInfo')
        
        user_permissions = ctx.message.author.guild_permissions
        if await misc.check_permission(ctx=ctx, required='editFeeds', user=user_permissions, author_ID=author_ID) == False:
            return

        if text == '':
            await ctx.send(content=f'<@!{author_ID}> Invalid or missing arguments. Use `{prefix}rmurl <url>`.')
            return
        
        results = manage_feeds.get_feed_by_name(text, ctx.message.guild.id, return_path=True)

        if len(results) == 1:
            with open('settings/database.json', 'r+') as f:
                database = json.load(f)
                feeds = database['feeds']

                feed_entry = int(results[0].split('-')[0])
                channels_entry = int(results[0].split('-')[1])

                del feeds[feed_entry]['channels'][channels_entry]

                if len(feeds[feed_entry]['channels']) == 0:
                    del feeds[feed_entry]

                # reset file position to the beginning - stackoverflow copy, dont ask
                f.seek(0)
                json.dump(database, f, indent=4)
                f.truncate()

            await ctx.send(content=f'<@!{author_ID}> Successfully deleted the entry **{text}**!')
            await log(f'**{text}** was removed.', 'info', client=self.bot)
            return
        elif len(results) > 1:
            await ctx.send(content=f'<@!{author_ID}> There are more results than one.\nUse `{prefix}removeall <name>` to remove all entries with a certain name.\nUse `{prefix}removeurl <url>` to remove all feeds with a certain url.\nUse `{prefix}find <name>` to find all entries with a certain name.')
            return
        elif len(results) < 1:
            await ctx.send(content=f'<@!{author_ID}> Could not find any feed with that name in this server. Use `{prefix}list` to list all entries in this server.')
            return

        await ctx.send(content=f'<@!{author_ID}> Something went wrong while trying delete the entry.')

        return

    @commands.command(
        name='removeall',
        description='Remove all feeds with a certain name',
        aliases=['rmall'],
        usage='<name>'
    )
    async def removeall_command(self, ctx):
        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        text = get_args(ctx, combine=True)

        await log(f'{prefix}removeall executed.', 'spamInfo')
        
        user_permissions = ctx.message.author.guild_permissions
        if await misc.check_permission(ctx=ctx, required='editFeeds', user=user_permissions, author_ID=author_ID) == False:
            return

        if text == '':
            await ctx.send(content=f'<@!{author_ID}> Invalid or missing arguments. Use `{prefix}rmurl <url>`.')
            return
        
        results = manage_feeds.get_feed_by_name(text, ctx.message.guild.id, return_path=True)

        if len(results) >= 1:
            with open('settings/database.json', 'r+') as f:
                database = json.load(f)
                feeds = database['feeds']

                # reverse results
                # this is import because if entry #12 and #13 both have to be removed and entry #12 is removed first then the old #13 would be #12 now so it's important to start with #13 first and then go to #12
                results = results[::-1]

                for r in results:

                    feed_entry = int(r.split('-')[0])
                    channels_entry = int(r.split('-')[1])

                    del feeds[feed_entry]['channels'][channels_entry]

                    if len(feeds[feed_entry]['channels']) == 0:
                        del feeds[feed_entry]

                # reset file position to the beginning - stackoverflow copy, dont ask
                f.seek(0)
                json.dump(database, f, indent=4)
                f.truncate()

            await ctx.send(content=f'<@!{author_ID}> Successfully deleted all entries named **{text}**!')
            await log(f'All entries named **{text}** were removed.', 'info', client=self.bot)
            return
        elif len(results) < 1:
            await ctx.send(content=f'<@!{author_ID}> Could not find any feed with that name in this server. Use `{prefix}list` to list all entries in this server.')
            return

        await ctx.send(content=f'<@!{author_ID}> Something went wrong while trying delete the entry.')

        return

    @commands.command(
        name='removeurl',
        description='Remove all feeds with a certain url',
        aliases=['rmurl'],
        usage='<url>'
    )
    async def removeurl_command(self, ctx):
        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        text = get_args(ctx, combine=True)

        await log(f'{prefix}removeurl executed.', 'spamInfo')
        
        user_permissions = ctx.message.author.guild_permissions
        if await misc.check_permission(ctx=ctx, required='editFeeds', user=user_permissions, author_ID=author_ID) == False:
            return

        if text == '':
            await ctx.send(content=f'<@!{author_ID}> Invalid or missing arguments. Use `{prefix}rmurl <url>`.')
            return
        
        results = manage_feeds.get_feed_by_url(text, ctx.message.guild.id, return_path=True)

        if len(results) >= 1:
            with open('settings/database.json', 'r+') as f:
                database = json.load(f)
                feeds = database['feeds']

                # reverse results
                # this is import because if entry #12 and #13 both have to be removed and entry #12 is removed first then the old #13 would be #12 now so it's important to start with #13 first and then go to #12
                results = results[::-1]

                for r in results:

                    feed_entry = int(r.split('-')[0])
                    channels_entry = int(r.split('-')[1])

                    del feeds[feed_entry]['channels'][channels_entry]

                    if len(feeds[feed_entry]['channels']) == 0:
                        del feeds[feed_entry]

                # reset file position to the beginning - stackoverflow copy, dont ask
                f.seek(0)
                json.dump(database, f, indent=4)
                f.truncate()

            await ctx.send(content=f'<@!{author_ID}> Successfully deleted all entries with the url {text}!')
            await log(f'All entries with the url **{text}** were removed.', 'info', client=self.bot)
            return
        elif len(results) < 1:
            await ctx.send(content=f'<@!{author_ID}> Could not find any feed with that url in this server. Use `{prefix}list` to list all entries in this server.')
            return

        await ctx.send(content=f'<@!{author_ID}> Something went wrong while trying delete the entry.')

        return

    @commands.command(
        name='move',
        description='Move a feed with a certain name to a different channel',
        usage='<name> <new channel>'
    )
    async def move_command(self, ctx):
        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        args = get_args(ctx)

        await log(f'{prefix}move executed.', 'spamInfo')
        
        user_permissions = ctx.message.author.guild_permissions
        if await misc.check_permission(ctx=ctx, required='editFeeds', user=user_permissions, author_ID=author_ID) == False:
            return

        try:
            name = ' '.join(args[0:-1])
            channel = args[-1]

            if channel.startswith('<#'):
                channel = self.bot.get_channel(int(channel[2:-1]))
            else:
                await ctx.send(content=f'<@!{author_ID}> Invalid channel. Use `{prefix}move <name> <new channel>`.')
                return
        except IndexError:
            await ctx.send(content=f'<@!{author_ID}> Invalid or missing arguments. Use `{prefix}move <name> <new channel>`.')
            return
        
        results = manage_feeds.get_feed_by_name(name, ctx.message.guild.id, return_path=True)

        if len(results) == 1:
            with open('settings/database.json', 'r+') as f:
                database = json.load(f)
                feeds = database['feeds']

                feed_entry = int(results[0].split('-')[0])
                channels_entry = int(results[0].split('-')[1])

                for c in feeds[feed_entry]['channels']:
                    if c['channelID'] == channel.id:
                        await ctx.send(content=f'<@!{author_ID}> **{name}** is already registered in <#{c["channelID"]}>. Use `{prefix}remove <name>` to remove the entry.')
                        return

                feeds[feed_entry]['channels'][channels_entry]['channelID'] = channel.id

                # reset file position to the beginning - stackoverflow copy, dont ask
                f.seek(0)
                json.dump(database, f, indent=4)
                f.truncate()

            await ctx.send(content=f'<@!{author_ID}> Successfully moved the entry **{name}** to <#{channel.id}>!')
            await log(f'**{name}** was moved to <#{channel.id}>.', 'info', client=self.bot)
            return
        elif len(results) > 1:
            await ctx.send(content=f'<@!{author_ID}> There are more results than one.')
            return
        elif len(results) < 1:
            await ctx.send(content=f'<@!{author_ID}> Could not find any feed with that name in this server. Use `{prefix}list` to list all entries in this server.')
            return

        await ctx.send(content=f'<@!{author_ID}> Something went wrong while trying to move the entry.')

        return

def setup(bot):
    bot.add_cog(Feeds(bot))
    # Adds the Feeds commands to the bot