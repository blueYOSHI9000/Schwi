import json

import modules.retroachievements as ra

def get_client_id():
    """Gets the RPC client id

    Returns:
        the client id or False if RPC shouldn't be used
    """
    db = json.load(open('settings/database.json', 'r'))
    last_rpc_used = db['general']['lastRPCUsed']

    if last_rpc_used == False:
        return False

    try:
        for r in db['RPC']:
            if r['name'] == last_rpc_used:
                return json.load(open('settings/token.json', 'r'))['RPCClientIDs'][r['client_name']]
    except KeyError:
        return False

    return False

def update_rpc():
    """Updates the rich presence

    This function is needed since the rich presence client (called RPC in main.py) can only be accessed from main.py. That's why, instead of updating it directly we use the 'RPCCommands' list in database.json to save commands which then gets executed in main via exec(). This function exists so instead of doing that in main.py we can do it here by simply passing a string with python code to main.py which gets executed via exec() as this makes the code a lot cleaner (as clean as it gets at least).

    Returns:
        python code in a string to execute within exec()
    """
    with open('settings/database.json', 'r+') as f:
        db = json.load(f)

        config = json.load(open('settings/config.json', 'r'))

        last_rpc_used = db['general']['lastRPCUsed']
        db_entries = db['RPC']
        entry = False

        for e in db_entries:
            if e['name'] == last_rpc_used:
                entry = e
                break

        commands = db['general']['RPCCommands']

        db['general']['RPCCommands'] = []

        # reset file position to the beginning - stackoverflow copy, dont ask
        f.seek(0)
        json.dump(db, f, indent=4)
        f.truncate()

    results = []

    for c in commands:
        if c['type'] == 'quit':
            return 'pypresence_RPC.close()'
        if c['type'] == 'update':
            results.append(f'pypresence_RPC.update(**{c["value"]})')

    # if RPC is off just return it
    if last_rpc_used == False:
        return 'pass'

    if entry == False:
        # add 'pass' in case it's empty since exec() needs to have something
        results.append('pass')
        return '\n'.join(results)


    if entry['RetroAchievements'] == True:
        rich_presence = ra.get_ra_rich_presence(entry)
    else:
        rich_presence = entry['richPresence']

    if config['RPC']['displayStartTime'] == True:
        rich_presence['start'] = json.load(open('settings/database.json', 'r'))['general']['RPCStartedAt']

    results.append(f"pypresence_RPC.update(**{repr(rich_presence)})")

    return '\n'.join(results)