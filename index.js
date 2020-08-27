const { CommandoClient } = require('discord.js-commando');
const path = require('path');

const misc = require('./misc.js');
const rss = require('./rss.js');

const config = require('./config.json');
const {token} = require('./token.json');

const client = new CommandoClient({
	commandPrefix: 'schwi.',
	owner: '183281735700578304',
});

client.registry
	.registerDefaultTypes()
	.registerGroups([
		['rss', 'RSS Commands'],
	])
	.registerDefaultGroups()
	.registerDefaultCommands()
	.registerCommandsIn(path.join(__dirname, 'commands'));


client.once('ready', () => {
	misc.log(client, `Logged in as ${client.user.tag}! (${client.user.id})`);
	client.user.setActivity('with Commando');

	rss.parseAllFeeds(client);
	setInterval(rss.parseAllFeeds, config.interval * 60000); //convert minutes to milliseconds
});

client.on('error', console.error);

client.login(token);