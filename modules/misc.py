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

    if combine != True:
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
    if getattr(user, required):
        return True
    elif getattr(user, 'administrator'):
        return True

    if send_message == True:
        await ctx.send(content=f'<@!{author_ID}> Not enough permission (required permission: `{required}`).')
    return False

def is_owner(user):
    """Checks if a user is an owner

    Args:
        user (integer/string): user ID either as a number or as a string
    Returns:
        true if user is an owner
    """
    owners = json.load(open('settings/config.json', 'r'))['bot']['owners']

    return str(user) in owners