import discord
from discord.ext import commands

from dateparser import parse

import json
import datetime as dt

import modules.manage_reminders as mrem
from modules.log import log
from modules.misc import get_args
import modules.misc as misc
import modules.convert_time as ct

class Reminders(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(
        name='addreminder',
        description='Adds a reminder',
        aliases=['rem', 'addrem', 'reminder'],
        usage='[type] <date & time> [public/private] <channel> <text>'
    )
    async def addreminder_command(self, ctx):
        if await misc.is_dm(ctx) == True:
            return

        author_ID = ctx.message.author.id
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        args = get_args(ctx)

        reminder_interval = json.load(open('settings/config.json', 'r'))['reminders']['interval']
        current_time = ct.struct_to_datetime(ct.get_current_time())

        timezone = json.load(open('settings/config.json', 'r'))['reminders']['timezone']

        public = None
        public_aliases = ['p', 'pc', 'pub', 'public', 'open', 'privatent']
        private_aliases = ['pv', 'priv', 'private', 'unlisted', 'publicnt']

        #aliases used to specify 'use this channel'
        this_channel_aliases = ['_']

        channel = None
        channel_arg = 0

        rem_type = None

        #everything in this try except is based around figuring out where the date & time string starts and ends as it doesn't follow any easy to follow rules
        #this is mainly because relative time inputs are allowed like "tomorrow" or "in 5 minutes", this is also the whole reason why channel has to be input
        #as the channel plays the biggest part in figuring out where the date & time string ends
        try:
            if args[0] in ['reminder']:
                rem_type = 'reminder'

            #check which arg is the channel
            for i in range(len(args)):
                if args[i].startswith('<#'):
                    if await misc.is_valid_channel(ctx=ctx, channel=self.bot.get_channel(int(args[i][2:-1])), send_message=False) == True:
                        channel = self.bot.get_channel(int(args[i][2:-1]))
                        channel_arg = i
                        break

            #check if user simply wanted to use the current channel by entering _
            if channel == None:
                for i in range(len(args)):
                    if args[i] in this_channel_aliases:
                        channel = ctx.message.channel
                        channel_arg = i
                        break

            if channel == None:
                #throw error so try except catches it and sends the 'invalid arguments' message
                raise IndexError()
                return

            # private/public always has to be specified before channel so that's where were checking if it exists
            if args[channel_arg - 1] in public_aliases:
                public = True
            elif args[channel_arg - 1] in private_aliases:
                public = False

            #get the date string
            #this checks if type or public/private or both got specified in order to figure out where the date string starts and ends
            if rem_type != None:
                if public == None:
                    rem_date_input = ' '.join(args[1:channel_arg])
                else:
                    rem_date_input = ' '.join(args[1:(channel_arg - 1)])
            else:
                if public == None:
                    rem_date_input = ' '.join(args[0:channel_arg])
                else:
                    rem_date_input = ' '.join(args[0:(channel_arg - 1)])

            #print(f"Date string to parse: '{rem_date_input}'")

            #TO_TIMEZONE makes sure it converts the time to UTC which is what the bot uses
            if timezone != "":
                rem_date = parse(rem_date_input, settings={'TO_TIMEZONE': 'etc/UTC', 'TIMEZONE': timezone})
            else:
                rem_date = parse(rem_date_input, settings={'TO_TIMEZONE': 'etc/UTC'})

            if rem_date == None:
                await ctx.send(content=f"<@!{author_ID}> Could not parse date `{rem_date_input}`. This might also be caused by using the command wrong (or the bot being broken), try using `{prefix}add {self.addreminder_command.usage}`")
                await log(f"Failed to create a reminder as the date '{rem_date_input}' could not be parsed (timezone: '{timezone}').", 'spamInfo', client=self.bot)
                return

            if rem_date <= (current_time + dt.timedelta(minutes = 1)):
                await ctx.send(content=f"<@!{author_ID}> Reminder has to be more than 1 minute in the future.")
                await log(f"Failed to create a reminder on '{rem_date.strftime('%Y-%m-%d %H:%M')}' (current time: '{current_time.strftime('%Y-%m-%d %H:%M')}' | parsed string: '{rem_date_input}').", 'spamInfo', client=self.bot)
                return

            #use defaults if not specified by the user
            if rem_type == None:
                rem_type = 'reminder'

            if public == None:
                public = False

            message = ' '.join(args[channel_arg + 1:])

        except IndexError:
            await ctx.send(content=f"<@!{author_ID}> Invalid arguments. Use `{prefix}add {self.addreminder_command.usage}`")
            return

        # create actual reminder and get the ID of the created reminder
        reminder_id = mrem.add_reminder(rem_type='reminder', author=author_ID, dt=rem_date, channel=channel.id, message=message, public=public)

        if public != True:
            await ctx.message.delete()

        await log(f"Created a reminder on '{rem_date.strftime('%Y-%m-%d %H:%M')}' (string parsed: '{rem_date_input}' | timezone: '{timezone}') with the ID '{reminder_id} by user {user}", 'spamInfo', client=self.bot)

        if type(reminder_id) == str:
            await ctx.send(content=f"<@!{author_ID}> A reminder has been created with the ID `{reminder_id}` and will be posted on `{rem_date.strftime('%Y-%m-%d %H:%M (%I:%M%p) UTC')}`.")
            return
        
        await ctx.send(content=f"<@!{author_ID}> Something has gone wrong while creating a reminder. The reminder might've still been created though, check `[insert command here]` to see if it exists.")
        return
        
    @commands.command(
        name='deletereminder',
        description='Deletes a reminder',
        aliases=['delrem', 'removereminder', 'remrem'],
        usage='<reminder ID>'
    )
    async def deletereminder_command(self, ctx):
        if await misc.is_dm(ctx) == True:
            return

        author_ID = ctx.message.author.id
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        args = get_args(ctx)

        rem_id = args[0]

        reminder = await mrem.get_reminder_from_id(rem_id)

        if reminder == False:
            await ctx.send(content=f"<@!{author_ID}> There's no reminder with the ID `{rem_id}`. Use [insert command here] to view all reminders created by you.")
            return

        if author_ID != reminder['author']:
            await ctx.send(content=f"<@!{author_ID}> Could not delete reminder with ID `{rem_id}` as you are not the creator of said reminder.")
            return

        await mrem.delete_reminders(rem_id, client=self.bot)
        await ctx.send(content=f"<@!{author_ID}> Reminder with ID `{rem_id}` got successfully deleted.")
        return

    @commands.command(
        name='listreminders',
        description='Lists all reminders of the user that uses this command',
        aliases=['lrem', 'listrem', 'listrems'],
        usage='[page]'
    )
    async def listreminders_command(self, ctx):
        author_ID = ctx.message.author.id
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]

        # get actual message
        args = get_args(ctx)

        await log(f"{prefix}listreminders executed.", 'spamInfo')

        page = 0
        try:
            page = int(args[0])
        except IndexError:
            pass

        # make sure page is valid
        if page < 1:
            page = 1

        messages = {}
        messages['item_title_type'] = 'reminders'
        messages['item_desc_type'] = 'reminders'

        messages['all_items_from'] = 'All reminders from'
        messages['no_items_available'] = f"Use `{prefix}addrem` to add a new reminder"
        messages['no_items_on_page'] = f"Use `{prefix}listrem {page - 1}` to view the previous page."
        messages['and_more'] = f"Use `{prefix}listrem [page]` to view a different page."

        results = await mrem.get_all_reminders_from_user(author_ID)
        title = f"**{ctx.message.author.name}**"

        embed = misc.create_embed_from_list(client=self.bot, dm=True, results=results, title=title, messages=messages, page=page, multi_columns=False)

        await ctx.send(embed=embed)
        return
        
    @commands.command(
        name='viewreminder',
        description='Shows a reminder',
        aliases=['vrem', 'viewrem', 'srem', 'showrem', 'showreminder'],
        usage='<reminder ID>'
    )
    async def viewreminder_command(self, ctx):
        author_ID = ctx.message.author.id
        user = ctx.message.author.name + '#' + ctx.message.author.discriminator
        prefix = json.load(open('settings/config.json', 'r'))['bot']['prefix'][0]
        # get actual message
        args = get_args(ctx)

        rem_id = args[0]

        reminder = await mrem.get_reminder_from_id(rem_id)

        if reminder == False:
            await ctx.send(content=f"<@!{author_ID}> There's either no reminder with the ID `{rem_id}` or you are not the author of that reminder. Use [insert command here] to view all reminders created by you.")
            return

        if author_ID != reminder['author']:
            await ctx.send(content=f"<@!{author_ID}> There's either no reminder with the ID `{rem_id}` or you are not the author of that reminder. Use [insert command here] to view all reminders created by you.")
            return

        rem_date = ct.ms_to_datetime(reminder['date'])

        await ctx.send(content=f"<@!{author_ID}> Reminder with the ID `{reminder['id']}` will be posted on `{rem_date.strftime('%Y-%m-%d %H:%M (%I:%M%p) UTC')}` with the following text:\n{reminder['message']}")
        return

def setup(bot):
    bot.add_cog(Reminders(bot))
    # Adds the Reminders commands to the bot