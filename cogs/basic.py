import discord
from discord.ext import commands
from discord import utils

from dateparser import parse

import json

from modules.misc import get_args
import modules.misc as misc
import modules.manage_feeds as manage_feeds
from modules.log import log

class Basic(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        name='ping',
        description='The ping command'
    )
    async def ping_command(self, ctx):
        start = d.timestamp(d.now())
        # Gets the timestamp when the command was used

        msg = await ctx.send(content='Pinging')
        # Sends a message to the user in the channel the message with the command was received.
        # Notifies the user that pinging has started

        await msg.edit(content=f"Pong!\nOne message round-trip took {( d.timestamp( d.now() ) - start ) * 1000 }ms.")
        # Ping completed and round-trip duration show in ms
        # Since it takes a while to send the messages
        # it will calculate how much time it takes to edit an message.
        # It depends usually on your internet connection speed
        return

    @commands.command(
        name='list',
        description='List all feeds in this guild or in the specified channel',
        usage='[channel] [page]'
    )
    async def list_command(self, ctx):
        if await misc.is_dm(ctx) == True:
            return

        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]

        # get actual message
        args = get_args(ctx)
        list_channel = False
        client = self.bot

        await log(f"{prefix}list executed.", 'spamInfo')
        
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
                await ctx.send(content=f"<@!{author_ID}> Channel entered was invalid. Please use `{prefix}list [channel]`")
                return

        # make sure page is valid
        if page < 1:
            page = 1

        messages = {}
        messages['item_title_type'] = 'feeds'
        messages['item_desc_type'] = 'feeds'
        
        messages['all_items_from'] = 'All feeds from'
        messages['no_items_available'] = f"Use `{prefix}list` to see all items in the entire server.\nUse `{prefix}list [channel]` to view a different channel.\nOr use `{prefix}add <channel> <url> <name>` to add a new feed."
        messages['no_items_on_page'] = f"Use `{prefix}list [channel] {page - 1}` to view the previous page."

        if list_channel == True:
            messages['and_more'] = f"Use `{prefix}list [channel] [page]` to view a different page."
        else:
            messages['and_more'] = f"Use `{prefix}list [page]` to view a different page."

        if list_channel == True:
            results = manage_feeds.get_feed_by_channel(channel.id)
            title = f"<#{channel.id}>"
        else:
            results = manage_feeds.get_feed_by_guild(ctx.message.guild.id)
            title = f"**{ctx.message.guild.name}**"

        embed = misc.create_embed_from_list(client=self.bot, guild=ctx.message.guild.id, results=results, title=title, messages=messages, page=page)

        await ctx.send(embed=embed)
        return

    @commands.command(
        name='find',
        description='Find a feed with a certain name',
        usage='<name>'
    )
    async def find_command(self, ctx):
        if await misc.is_dm(ctx) == True:
            return

        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        text = get_args(ctx, combine=True)

        await log(f"{prefix}find executed.", 'spamInfo')
        
        results = manage_feeds.get_feed_by_name(text, ctx.message.guild.id)

        embed_dict = {}

        embed_dict['color'] = misc.get_embed_color(default_color=self.bot.get_guild(ctx.message.guild.id).me.color)

        embed_dict['description'] = f"All feeds named **{text}**:"

        embed = discord.Embed(**embed_dict)

        if len(results) == 0:
            embed.add_field(name=f"No items available.", value=f"Note: Only exact matches in this server are shown.", inline=False)
        else:
            results_length = len(results)

            count = 0

            for r in results:
                count += 1
                if count > 12:
                    embed.add_field(name=f"...and {len(results) - count} more", value=f"Use {prefix}rmall <name> to remove all feeds matching a certain name.", inline=False)
                    break
                embed.add_field(name=r['feedName'], value=f"<#{r['channelID']}>\n{r['url']}")

        await ctx.send(embed=embed)

        return

    @commands.command(
        name='converttime',
        description='Converts time between timezones and other stuff.',
        aliases=['ct', 'ctime', 'concertdate', 'cd', 'cdate'],
        usage='<time to convert> <timezone>'
    )
    async def converttime_command(self, ctx):
        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get arguments
        args = get_args(ctx)

        await log(f"{prefix}converttime executed.", 'spamInfo')

        if len(args) < 2:
            await ctx.send(content=f"<@!{author_ID}> Missing argument. Please use `{prefix}converttime <time/date to convert> <timezone>` where timezone can be in the format of either `CEST` or `Europe/Berlin`.")
            return

        timezone = args[len(args) - 1]
        date_to_convert = ' '.join(args[:len(args) - 1])

        if timezone == 'local':
            timezone = json.load(open('settings/config.json', 'r'))['reminders']['timezone']

        if timezone == '':
            await ctx.send(content=f"<@!{author_ID}> `local` argument can only be used if a timezone is entered in `config.json`>`reminders`>`timezone`.")
            return

        # Convert time (simply let dateparser handle it)
        date = parse(date_to_convert, settings={'TO_TIMEZONE': timezone, 'RETURN_AS_TIMEZONE_AWARE': False})

        if date == None:
            await ctx.send(content=f"<@!{author_ID}> Something went wrong when trying to convert `{date_to_convert}` to the timezone `{timezone}`. Please use `{prefix}converttime <time/date to convert> <timezone>` where timezone can be in the format of either `CEST` or `Europe/Berlin`.")
            return

        print(date)
        await ctx.send(content=f"<@!{author_ID}> `{date.strftime('%Y-%m-%d %H:%M (%I:%M%p)')}` (converted from `{timezone}`)")
        return

def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot