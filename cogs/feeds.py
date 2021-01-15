import discord
from discord.ext import commands
from discord import utils

import json

from modules.misc import get_args
import modules.misc as misc
import modules.manage_feeds as manage_feeds

class Feeds(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        name='list',
        description='List all feeds in this guild or in the specified channel',
        usage='[channel] [page]'
    )
    async def list_command(self, ctx):
        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]

        # get actual message
        args = get_args(ctx)
        list_channel = False
        client = self.bot
        
        # check if an argument is used
        arg1_available = False
        try:
            args[0]
            arg1_available = True
        except IndexError:
            pass

        page = 0
        try:
            page = int(args[1])
        except IndexError:
            pass

        list_channel = False

        if arg1_available == True:
            # get channel from name
            if args[0].startswith('<#'):
                channel = client.get_channel(int(args[0][2:-1]))
                list_channel = True

                # check if channel is valid
                if await misc.is_valid_channel(ctx=ctx, channel=channel, author_ID=author_ID, command=f'{prefix}list [channel]') == False:
                    return

            # check if only digits - if yes, use as page number instead
            elif args[0].isdigit():
                page = int(args[0])
            # error
            else:
                await ctx.send(content=f'<@!{author_ID}> Channel entered was invalid. Please use `{prefix}list [channel]`')
                return

        # make sure page is valid
        if page < 1:
            page = 1

        messages = {}
        messages['no_items_available'] = f'Use `{prefix}list` to see all items in the entire server.\nUse `{prefix}list [channel]` to view a different channel.\nOr use `{prefix}add <channel> <url> <name>` to add a new feed.'
        messages['no_items_on_page'] = f'Use `{prefix}list [channel] {page - 1}` to view the previous page.'
        messages['and_more'] = f'Use `{prefix}list [channel] {page + 1}` to view the next page.'

        if list_channel == True:
            results = manage_feeds.get_feed_by_channel(channel.id)
            title = f'<#{channel.id}>'
        else:
            results = manage_feeds.get_feed_by_guild(ctx.message.guild.id)
            title = f'**{ctx.message.guild.name}**'

        embed = misc.create_embed_from_list(client=self.bot, guild=ctx.message.guild.id, results=results, title=title, messages=messages, page=page)

        await ctx.send(embed=embed)
        return

    @commands.command(
        name='find',
        description='Find a feed with a certain name',
        usage='<name>'
    )
    async def find_command(self, ctx):
        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        text = get_args(ctx, combine=True)
        
        results = manage_feeds.get_feed_by_name(text, ctx.message.guild.id)

        embed_dict = {}

        embed_dict['color'] = misc.get_embed_color(default_color=self.bot.get_guild(ctx.message.guild.id).me.color)

        embed_dict['description'] = f'All feeds named **{text}**:'

        embed = discord.Embed(**embed_dict)

        if len(results) == 0:
            embed.add_field(name=f'No items available.', value=f'Note: Only exact matches in this server are shown.', inline=False)
        else:
            results_length = len(results)

            count = 0

            for r in results:
                count += 1
                if count > 12:
                    embed.add_field(name=f'...and {len(results) - count} more', value=f'Use {prefix}rmall <name> to remove all feeds matching a certain name.', inline=False)
                    break
                embed.add_field(name=r['feedName'], value=f'<#{r["channelID"]}>\n{r["url"]}')

        await ctx.send(embed=embed)

        return

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
        elif result == 'exists':
            await ctx.send(content=f'<@!{author_ID}> **{name}** is already registered in <#{channel.id}>. Use `{prefix}edit <name>` to edit the entry.')
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
        
        user_permissions = ctx.message.author.guild_permissions
        if await misc.check_permission(ctx=ctx, required='editFeeds', user=user_permissions, author_ID=author_ID) == False:
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
        
        user_permissions = ctx.message.author.guild_permissions
        if await misc.check_permission(ctx=ctx, required='editFeeds', user=user_permissions, author_ID=author_ID) == False:
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
        
        user_permissions = ctx.message.author.guild_permissions
        if await misc.check_permission(ctx=ctx, required='editFeeds', user=user_permissions, author_ID=author_ID) == False:
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
            return
        elif len(results) < 1:
            await ctx.send(content=f'<@!{author_ID}> Could not find any feed with that url in this server. Use `{prefix}list` to list all entries in this server.')
            return

        await ctx.send(content=f'<@!{author_ID}> Something went wrong while trying delete the entry.')

        return

    @commands.command(
        name='move',
        description='Move a feed with a certain name to a different channel',
        usage='<name>'
    )
    async def move_command(self, ctx):
        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        args = get_args(ctx)
        
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