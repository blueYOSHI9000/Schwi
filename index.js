const { CommandoClient } = require('discord.js-commando');
const path = require('path');

const misc = require('./misc.js');
const rss = require('./rss.js');

const config = require('./settings/config.json');
const {token} = require('./settings/token.json');
const db = require('./settings/database.json');

const client = new CommandoClient({
	commandPrefix: config.bot.prefix,
	owner: config.bot.owners,
});

client.registry
	.registerDefaultTypes()
	.registerGroups([
		['rss', 'RSS Commands'],
		['owner', 'Bot-Owner commands'],
	])
	.registerDefaultGroups()
	.registerDefaultCommands()
	.registerCommandsIn(path.join(__dirname, 'commands'));


client.once('ready', () => {
	misc.log(client, 'info', `Logged in as ${client.user.tag}! (${client.user.id})`);

	client.user.setPresence({
		status: config.bot.status,
		activity: {
			name: config.bot.activityName,
			type: config.bot.activityType.toUpperCase()
		}
	})
	.then(misc.log(client, 'spamInfo', 'Activity updated to "' + config.bot.activityType + ' ' + config.bot.activityName + '" on boot.'))
	.catch(console.error);

	var interval = config.rss.interval; //make sure interval is at least 10 minutes
	if (interval < 10) {
		interval = 10;
	}

	rss.parseAllFeeds(client);
	setInterval(rss.parseAllFeeds, interval * 60000); //convert minutes to milliseconds
});

client.on('error', console.error);

client.login(token);