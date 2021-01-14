import discord
from discord.ext import commands
from discord import utils

from modules.misc import get_args
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
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator

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
                await ctx.send(content=f"<@!{author_ID}> Channel entered was invalid. Please use `schwi.list [channel]`")
                return

        if channel == None or channel.guild.id != ctx.message.guild.id:
            await ctx.send(content=f"<@!{author_ID}> Channel entered was either invalid or not from this server. Please use `schwi.list [channel]` in the server that has said channel.")
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
            embed.add_field(name=f'No items on this page', value=f'Use `schwi.list [channel] {page - 1}` to view the previous page.', inline=False)

        for r in results:
            count += 1
            if count > 12:
                embed.add_field(name=f'...and {len(results) - count} more', value=f'Use `schwi.list [channel] {page + 1}` to view the next page.', inline=False)
                break
            embed.add_field(name=r['feedName'], value=f'<#{r["channelID"]}> - {r["url"]}')

        await ctx.send(embed=embed)
        return


def setup(bot):
    bot.add_cog(Feeds(bot))
    # Adds the Feeds commands to the bot