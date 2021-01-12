import json

def get_args(ctx, combine=False):
    """Splits a message into arguments.

    message (class/obj): the ctx class/obj from inside a command function.
    [combine] (boolean): if true it combines all args into a single long
            argument - otherwise it gets split into multiple
    """
    msg = ctx.message.content

    # strip the prefix and command used from the message
    prefix_used = ctx.prefix
    alias_used = ctx.invoked_with
    args = msg[len(prefix_used) + len(alias_used):]

    if combine != True:
        args = args.split()

    return args

def is_owner(user):
    """return True if user is (one of) the owner(s) - otherwise return False

    user (integer/string): user ID either as a number or as a string
    """
    owners = json.load(open('settings/config.json', 'r'))['bot']['owners']

    print(repr(owners))
    print(repr(str(user)))
    print(str(user) in owners)

    return str(user) in owners