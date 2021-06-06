import discord

import math
import json

import modules.convert_time as ct

def get_args(ctx, combine=False):
    """Splits a message into arguments.

    Args:
        message (class/obj): the ctx class/obj from inside a command function.
        combine (boolean): if true it combines all args into a single long argument - otherwise it gets split into multiple
    Returns:
        If combine==true then it returns a string - otherwise a list with all arguments
    """
    msg = ctx.message.content

    # strip the prefix and command used from the message
    prefix_used = ctx.prefix
    alias_used = ctx.invoked_with
    args = msg[len(prefix_used) + len(alias_used):]

    if combine == True:
        args = args.strip()
    else:
        args = args.split()

    return args

async def is_valid_channel(*, ctx, channel, author_ID=False, command=False, send_message=True):
    """Checks whether a channel is valid and in the current server. Can optionally also send a message replying to the author that the entered channel is invalid.

    Args:
        ctx: message ctx
        channel (channel object): the channel object, likely gotten with client.get_channel()
        author_ID (number): ID of the author, used to @ them (optional if send_message is False)
        command (string): the command used in the message sent (optional if send_message is False)
        send_message (boolean): sends an error message if true (True on default)
    Returns:
        True if valid, False if not
    """
    if channel == None or channel.guild.id != ctx.message.guild.id:
        if send_message == True:
            await ctx.send(content=f"<@!{author_ID}> Channel entered was either invalid or not from this server. Please use `{command}` in the server that has said channel.")
        return False
    return True

async def check_permission(ctx, required, user, author_ID=False, send_message=True):
    """Checks whether a user has the required permission

    Args:
        ctx: message ctx
        required (string): the required permission
        user (list): a list of the users permission (accessed with ctx.author.guild_permissions)
        author_ID (number): ID of the author, used to @ them (optional if send_message is False)
        send_message (boolean): sends an error message if true (sends on default)
    Returns:
        True if valid, False if not
    """
    required = json.load(open('settings/config.json', 'r'))['permissions'][required]

    if getattr(user, required):
        return True
    elif getattr(user, 'administrator'):
        return True

    if send_message == True:
        await ctx.send(content=f'<@!{author_ID}> Not enough permission (required permission: `{required}`).')
    return False

def convert_hex_to_embed_color(color):
    """converts a hex color to a discord embed color

    Args:
        color (string): a hex color like '#ff0000'
    Returns:
        a discord color object
    """
    color = int(color.replace('#', ''), 16)
    return discord.Colour(int(hex(color), 0))

def get_embed_color(default_color):
    """returns the color that the embed should use

    Args:
        default_color (discord.Colour object): the default color that should be used if config.json doesn't overwrite it
    Returns:
        a discord color object
    """
    config_embed_color = json.load(open('settings/config.json', 'r'))['bot']['embedColor']
    if config_embed_color == '':
        return default_color
    else:
        return convert_hex_to_embed_color(config_embed_color)

def create_embed_from_list(*, client=None, dm=False, guild=None, results, title, messages, page=1, multi_columns=True, pages_used=True, max_items_per_page=12):
    """Creates an embed out of a list

    Messages:
        messages['item_title_type']: A simple string which decides which title is used (gets evaluated in this function further down).
        messages['item_desc_type']: A simple string which decides which description is used (gets evaluated in this function further down).
        messages['no_items_available']: Gets used as a description when no items are available. Best used to explain how to use the command differently so results can be shown.
        messages['no_items_on_page']: Gets used as a description when there are no items on the current page. Best used to explain how to view the previous page.
        messages['and_more']: Gets used as a description when there are more items on later pages. Best used to explain how to view the next page.

    Args:
        client: the discord.py client (likely self.bot)
        dm (boolean): if executed in DMs (defaults to False)
        guild (number): the guild ID used to get the bots color (likely ctx.message.guild.id) -- not needed if dm is True
        results (list): the list of database entries, likely gotten out of a function in modules/feeds.py
        title (string): the title that should be used ("All items from {title}")
        messages (dict): messages used - view above for more info
        page (number): the page number
        multi_columns (boolean): If multiple columns should be used (defaults to True)
        pages_used (boolean): whether pages should even be used (defaults to True)
        max_items_per_page (int): max amount of items that should be displayed per page (max is 12 with columns and 5 without)
    """
    if max_items_per_page < 1:
        max_items_per_page = 1

    #without columns each item takes up a lot more space and as such there should be fewer items per page
    if multi_columns == False:
        if max_items_per_page > 7:
            max_items_per_page = 7
    elif max_items_per_page > 12:
        max_items_per_page = 12

    embed_dict = {}

    #dont ask me about anything discord.py color related, I have absolutely no idea how anything works aside from everything I've written down here - chances are I even forgot about that by the time anyone else reads this because discord.py colors are the biggest pain imaginable and I don't ever wanna work again with them
    #good luck
    #you'll need it

    #get the embed color
    #use #fffffe for DMs as DMs use a transparent color (see below)
    if dm == True:
        #create a color object first in order to then edit it
        embed_dict['color'] = client.user.color
        embed_dict['color'].value = 16777214
    else:
        embed_dict['color'] = get_embed_color(default_color=client.get_guild(guild).me.color)
    
    #a color of #000000 (black) is used as transparent so instead it should use #fffffe (almost white - just almost white because #ffffff is reserved apparently) which is how transparent is displayed for anyone that still has functioning eyes (using dark mode)
    if embed_dict['color'].value == 0:
        embed_dict['color'].value = 16777214

    if pages_used == False:
        embed_dict['description'] = f"{messages['all_items_from']} **{title}**:"
        page = 1
    else:
        #get max amount of pages
        max_page = math.ceil(len(results)/max_items_per_page)
        if max_page < 1:
            max_page = 1

        if page > max_page:
            page = max_page
        embed_dict['description'] = f"{messages['all_items_from']} **{title}** (page {page}/{max_page}):"

    embed = discord.Embed(**embed_dict)
    count = 0

    print(embed.color)

    if len(results) == 0:
        embed.add_field(name=f"No items available.", value=messages['no_items_available'], inline=False)
    else:
        results = results[(max_items_per_page * (page - 1)):]

        if len(results) == 0:
            embed.add_field(name=f"No items on this page.", value=messages['no_items_on_page'], inline=False)

        for r in results:
            count += 1
            if count > max_items_per_page:
                embed.add_field(name=f"...and {len(results) - count + 1} more", value=messages['and_more'], inline=False)
                break

            #get title & descriptions as they have to be evaluated in here
            if messages['item_title_type'] == 'feeds':
                item_title = f"{r['feedName']}"
            elif messages['item_title_type'] == 'reminders':
                item_title = f"ID {r['id']}"

            if messages['item_desc_type'] == 'feeds':
                item_desc = f"<#{r['channelID']}>\n{r['url']}"
            elif messages['item_desc_type'] == 'reminders':
                item_desc = f"`{ct.ms_to_datetime(r['date']).strftime('%Y-%m-%d %H:%M (%I:%M%p) UTC')}`\n{r['message']}"


            #the eval handles the messages like a formatted string
            embed.add_field(name=item_title, value=item_desc, inline=multi_columns)

    return embed

def is_owner(user):
    """Checks if a user is an owner

    Args:
        user (integer/string): user ID either as a number or as a string
    Returns:
        true if user is an owner
    """
    owners = json.load(open('settings/config.json', 'r'))['bot']['owners']

    return str(user) in owners

async def is_dm(ctx, *, reply=True):
    """Checks if the current channel is a DM and optionally

    Args:
        ctx: message ctx
        reply (boolean): If it should automatically reply saying that the command isn't available (defaults to True)
    Returns:
        True if DM, False if not
    """
    if ctx.guild == None:
        if reply == True:
            await ctx.send(content=f"This command cannot be executed in DMs.")
        return True
    else:
        return False