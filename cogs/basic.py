from discord.ext import commands
from datetime import datetime as d
from modules.misc import get_args

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

        await msg.edit(content=f'Pong!\nOne message round-trip took {( d.timestamp( d.now() ) - start ) * 1000 }ms.')
        # Ping completed and round-trip duration show in ms
        # Since it takes a while to send the messages
        # it will calculate how much time it takes to edit an message.
        # It depends usually on your internet connection speed
        return

    @commands.command(
        name='say',
        description='Make the bot say something',
        aliases=['repeat', 'parrot'],
        usage='<text>'
    )
    async def say_command(self, ctx):
        # get actual message
        text = get_args(ctx, combine=True)
        
        if text == '':
            await ctx.send(content='You need to specify the text!')
            pass

        else:
            await ctx.send(content=f"{text}")
            pass

        return


def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot