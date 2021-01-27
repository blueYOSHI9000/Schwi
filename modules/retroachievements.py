import urllib.request
import json
import re

ra_user = json.load(open('settings/token.json', 'r'))['retroachievements']['username']
ra_api_key = json.load(open('settings/token.json', 'r'))['retroachievements']['APIkey']

def get_ra_rich_presence(db_entry):
    """Gets the RetroAchievements rich presence

    Note: time started gets added in update_rpc() in richpresence.py

    Args:
        db_entry: the database entry that includes name, aliases etc

    Returns:
        dict with all arguments needed to update it with pypresence directly
    """
    with urllib.request.urlopen(f"https://retroachievements.org/API/API_GetUserSummary.php?z={ra_user}&y={ra_api_key}&u={ra_user}&g=1&a=5") as url:
        data = json.loads(url.read().decode())

        config = json.load(open('settings/config.json', 'r'))

        last_game = data['LastGameID']
        per_game_options = db_entry['perGameOptions']

        game_name = data['LastGame']['Title']

        # check per game options and apply them
        if last_game in per_game_options:
            game_options = per_game_options[last_game]

            if 'gameName' in game_options:
                game_name = game_options['gameName']
        
        rich_presence = {}

        if config['RPC']['RetroAchievements']['displayGameName'] == True:
            rich_presence['details'] = game_name

        rich_presence['state'] = data['RichPresenceMsg']

        rich_presence['large_image'] = data['LastGameID']
        rich_presence['large_text'] = game_name

        if config['RPC']['RetroAchievements']['displaySmallImage'] == True:
            rich_presence['small_image'] = 'ra'
            rich_presence['small_text'] = config['RPC']['RetroAchievements']['smallImageText']

        # check per game options and apply them
        if last_game in per_game_options:
            game_options = per_game_options[last_game]

            if 'replaceRegex' in game_options:
                # delete the regex match
                rich_presence['state'] = re.sub(game_options['replaceRegex'], '', rich_presence['state'])
            elif 'useRegex' in game_options:
                # only use the regex matches
                rich_presence['state'] = ''.join(re.findall(game_options['replaceRegex'], rich_presence['state']))

        return rich_presence