import discord

import json

from modules.log import log
import modules.convert_time as ct

def add_reminder(*, rem_type, author, dt, channel, message, public=False):
    """Adds a new reminder

    Args:
        rem_type (string): what type of reminder it should be (currently just 'reminder')
        author (int): a discord user ID of the person that created the reminder
        public (boolean): if it should be publicly viewable (defaults to False)
        dt (datetime object): a datetime object of the time the user should be reminded at
        channel (int): the channel ID of the channel it should be posted in
        message (string): the message
    Returns:
        the reminder ID as a string
    """
    with open('settings/database.json', 'r+') as f:
        database = json.load(f)
        reminders = database['reminders']

        item_id = database['general']['reminderCount'] + 1
        database['general']['reminderCount'] = item_id

        item = {}
        item['id'] = str(item_id)
        item['type'] = rem_type
        item['author'] = author
        item['public'] = public
        item['date'] = ct.datetime_to_ms(dt)
        item['channel'] = channel
        item['message'] = message

        reminders.append(item)

        # reset file position to the beginning - stackoverflow copy, dont ask
        f.seek(0)
        json.dump(database, f, indent=4)
        f.truncate()

    return str(item_id)

async def scan_all_reminders(*, client):
    """Scans all reminders and posts the ones that should be posted.

    Args:
        client (discord.py client object): the discord.py client needed to post discord messages
    """
    # dirty solution since it only checks for the first author
    await daily_reminder_check(author=json.load(open('settings/config.json', 'r'))['bot']['owners'][0], client=client)

    await log('Start scanning all reminders.', 'spamInfo', client=client)

    reminders = json.load(open('settings/database.json', 'r'))['reminders']

    current_time = ct.struct_to_ms(ct.get_current_time())

    reminders_to_delete = []

    for i in range(len(reminders)):
        if current_time > reminders[i]['date']:
            await post_reminder(reminders[i], client=client)
            reminders_to_delete.append(reminders[i]['id'])

    await delete_reminders(reminders_to_delete, client=client)

    await log(' Done scanning all reminders.', 'spamInfo', client=client)
    return

async def daily_reminder_check(*, force=False, author, client):
    """Checks if there's reminders today and automatically posts it on discord.

    Args:
        force (Boolean): If True it forces to do the check. Otherwise it only checks if it hasn't already today or if it's disable in the config.
        author (Number): The author ID of the discord user to check.
        client (discord.py client object): the discord.py client needed to post discord messages
    """
    last_daily_check = ct.ms_to_struct(json.load(open('settings/database.json', 'r'))['general']['lastDailyRemCheck'])

    current_time = ct.get_current_time()

    if json.load(open('settings/config.json', 'r'))['reminders']['dailyReminderCheck'] != True & force != True:
        await log('Skipped doing daily reminder check as it\'s been disabled in config.', 'spamInfo', client=client)
        return

    if current_time.tm_year == last_daily_check.tm_year & current_time.tm_mon == last_daily_check.tm_mon & current_time.tm_mday == last_daily_check.tm_mday & force != True:
        await log('Skipped doing daily reminder check as it\'s already been done.', 'spamInfo', client=client)
        return

    reminders = json.load(open('settings/database.json', 'r'))['reminders']

    todays_reminders = []

    for i in range(len(reminders)):
        reminder_date = ct.ms_to_struct(reminders[i]['date'])

        # ugly if chain because combining it to a single big if doesn't work for some reason
        if reminders[i]['author'] == author:
            if current_time.tm_year == reminder_date.tm_year:
                if current_time.tm_mon == reminder_date.tm_mon:
                    if current_time.tm_mday == reminder_date.tm_mday:
                        todays_reminders.append(reminders[i]['id'])

    if len(todays_reminders) == 0:
        await log('Skipped posting daily reminders as there\'s no reminders today.', 'spamInfo', client=client)
        return

    try:
        await log('Posting daily reminder check...', 'spamInfo', client=client)
        channel = client.get_channel(json.load(open('settings/config.json', 'r'))['reminders']['dailyReminderCheckChannel'])
        await channel.send(f"There are {len(todays_reminders)} reminders today: `{'`, `'.join(todays_reminders)}`")
    except AttributeError:
        await log('Could not post daily reminder check, likely due to wrong channel ID inside config > reminders > dailyReminderCheckChannel.', 'warn', client=client)


    # update 'lastDailtRemCheck' in database
    with open('settings/database.json', 'r+') as f:
        database = json.load(f)
        database['general']['lastDailyRemCheck'] = ct.struct_to_ms(current_time)

        # reset file position to the beginning - stackoverflow copy, dont ask
        f.seek(0)
        json.dump(database, f, indent=4)
        f.truncate()
    return

async def post_reminder(reminder, *, client):
    """Posts the reminder on discord.

    Args:
        reminder (database object): the database entry of the reminder to be posted
        client (discord.py client object): the discord.py client needed to post discord messages
    """
    channel = client.get_channel(reminder['channel'])
    await channel.send(f"<@{reminder['author']}> {reminder['message']}")
    await log(f"Posted reminder '{reminder['id']}'.", 'spamInfo', client=client)
    return

async def delete_reminders(reminders_to_delete, *, client):
    """Deletes several specified reminders.

    Args:
        reminders_to_delete (string/array of strings): A single ID string or an array of ID strings
        client (discord.py client object): the discord.py client needed to post discord messages
    """
    if type(reminders_to_delete) == str:
        reminders_to_delete = [reminders_to_delete]

    with open('settings/database.json', 'r+') as f:
        database = json.load(f)
        reminders = database['reminders']
 
        #this creates a for loop that iterates through all reminders starting at the last one and going backwards through until the first one
        #this is needed as entries are deleted and if not for this it would just keep iterating as if the deleted entry still existed
        for i in reversed(range(len(reminders))):
            if reminders[i]['id'] in reminders_to_delete:
                await log(f"Deleted reminder with the ID '{reminders[i]['id']}'.", 'spamInfo', client=client)
                del reminders[i]
 
        database['reminders'] = reminders
        # reset file position to the beginning - stackoverflow copy, dont ask
        f.seek(0)
        json.dump(database, f, indent=4)
        f.truncate()
    return

async def get_reminder_from_id(rem_id):
    """Finds the reminder with the specified ID.

    Args:
        rem_id (string): The ID
    Returns:
        The database entry of the reminder. Returns False if reminder doesn't exist.
    """
    reminders = json.load(open('settings/database.json', 'r'))['reminders']

    for i in reminders:
        if i['id'] == rem_id:
            return i

    return False

async def get_all_reminders_from_user(author_ID):
    """Gets all reminders from a user.

    Args:
        author_ID (int): the discord user ID
    Returns:
        A list of all reminders of the specified person.
    """
    reminders = json.load(open('settings/database.json', 'r'))['reminders']

    matches = []

    for i in reminders:
        if i['author'] == author_ID:
            matches.append(i)

    return matches