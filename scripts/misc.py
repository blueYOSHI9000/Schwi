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

    if combine:
        args = args.split()

    return args