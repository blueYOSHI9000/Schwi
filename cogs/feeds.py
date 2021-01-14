import discord
from discord.ext import commands
from discord import utils

import json

from modules.misc import get_args, is_valid_channel, check_permission
import modules.feeds as feeds

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
            # check if only digits - if yes, use as page number instead
            elif args[0].isdigit():
                page = int(args[0])
            # error
            else:
                await ctx.send(content=f'<@!{author_ID}> Channel entered was invalid. Please use `{prefix}list [channel]`')
                return

        # check if channel is valid
        if await is_valid_channel(ctx=ctx, channel=channel, author_ID=author_ID, command=f'{prefix}list [channel]') == False:
            return

        # make sure page is valid
        if page < 1:
            page = 1

        embed_dict = {}

        embed_dict['color'] = self.bot.user.color

        if list_channel == True:
            results = feeds.get_feed_by_channel(channel.id)
            embed_dict['description'] = f'All feeds from <#{channel.id}> (page {page}):'
        else:
            results = feeds.get_feed_by_guild(ctx.message.guild.id)
            embed_dict['description'] = f'All feeds from **{ctx.message.guild.name}** (page {page}):'

        embed = discord.Embed(**embed_dict)
        count = 0

        results = results[(12 * (page - 1)):]

        if len(results) == 0:
            embed.add_field(name=f'No items on this page', value=f'Use `{prefix}list [channel] {page - 1}` to view the previous page.', inline=False)

        for r in results:
            count += 1
            if count > 12:
                embed.add_field(name=f'...and {len(results) - count} more', value=f'Use `{prefix}list [channel] {page + 1}` to view the next page.', inline=False)
                break
            embed.add_field(name=r['feedName'], value=f'<#{r["channelID"]}> - {r["url"]}')

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
        
        required_permission = json.load(open('settings/config.json', 'r'))['permissions']['editFeeds']
        user_permissions = ctx.author.guild_permissions

        if await check_permission(ctx=ctx, required=required_permission, user=user_permissions, author_ID=author_ID) == False:
            return

        # make sure arguments exists and are valid
        try:
            if args[0].startswith('<#'):
                channel = self.bot.get_channel(int(args[0][2:-1]))
            else:
                await ctx.send(content=f'<@!{author_ID}> Invalid channel. Use `{prefix}add <channel> <url> <name>`')
                return

            # check if channel is valid
            if await is_valid_channel(ctx=ctx, channel=channel, author_ID=author_ID, command=f'{prefix}list [channel]') == False:
                return

            url = args[1]
            name = ' '.join(args[2:])
        except IndexError:
            await ctx.send(content=f'<@!{author_ID}> Invalid arguments. Use `{prefix}add <channel> <url> <name>`')
            return

        result = feeds.add_feed(channel=channel, url=url, name=name)

        if result == 'added':
            await ctx.send(content=f'<@!{author_ID}> **{name}** was successfully added to <#{channel.id}>!')
        elif result == 'exists':
            await ctx.send(content=f'<@!{author_ID}> **{name}** is already registered in <#{channel.id}>. Use `{prefix}edit <name>` to edit the entry.')
        else:
            await ctx.send(content=f'<@!{author_ID}> Something went wrong while adding **{name}**, it might\'ve been added, it might\'ve not. Use {prefix}list <#{channel}> to check whether it has been added or not.')

        return

def setup(bot):
    bot.add_cog(Feeds(bot))
    # Adds the Feeds commands to the bot