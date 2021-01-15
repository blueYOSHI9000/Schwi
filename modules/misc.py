import discord

import math
import json

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
    """Checks whether a channel is valid and in the current server.

    Args:
        ctx: message ctx
        channel (channel object): the channel object, likely gotten with client.get_channel()
        author_ID (number): ID of the author, used to @ them (optional if send_message is False)
        command (string): the command used in the message sent (optional if send_message is False)
        send_message (boolean): sends an error message if true (sends on default)
    Returns:
        True if valid, False if not
    """
    if channel == None or channel.guild.id != ctx.message.guild.id:
        if send_message == True:
            await ctx.send(content=f'<@!{author_ID}> Channel entered was either invalid or not from this server. Please use `{command}` in the server that has said channel.')
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
    color = int(color.replace("#", ""), 16)
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

def create_embed_from_list(*, client, guild, results, title, messages, page=1, pages_used=True):
    """Creates an embed out of a list

    Args:
        client: the discord.py client (likely self.bot)
        guild (number): the guild ID used to get the bots color (likely ctx.message.guild.id)
        results (list): the list of database entries, likely gotten out of a function in modules/feeds.py
        title (string): the title that should be used ("All feeds from {title}")
        messages (dict): messages used - messages['no_items_available'] - messages['no_items_on_page'] - messages['and_more']
        page (number): the page number
        pages_used (boolean): whether pages should even be used (defaults to True)
    """

    embed_dict = {}

    embed_dict['color'] = get_embed_color(default_color=client.get_guild(guild).me.color)

    if pages_used == False:
        embed_dict['description'] = f'All feeds from **{title}**:'
        page = 1
    else:
        max_page = math.ceil(len(results)/12)
        if max_page < 1:
            max_page = 1

        if page > max_page:
            page = max_page
        embed_dict['description'] = f'All feeds from **{title}** (page {page}/{max_page}):'

    embed = discord.Embed(**embed_dict)
    count = 0

    if len(results) == 0:
        embed.add_field(name=f'No items available.', value=messages['no_items_available'], inline=False)
    else:
        results = results[(12 * (page - 1)):]

        if len(results) == 0:
            embed.add_field(name=f'No items on this page', value=messages['no_items_on_page'], inline=False)

        for r in results:
            count += 1
            if count > 12:
                embed.add_field(name=f'...and {len(results) - count + 1} more', value=messages['and_more'], inline=False)
                break
            embed.add_field(name=r['feedName'], value=f'<#{r["channelID"]}>\n{r["url"]}')

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