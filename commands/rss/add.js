const { Command } = require('discord.js-commando');

const misc = require('../../misc.js');

const config = require('../../settings/config.json');
const db = require('../../settings/database.json');

module.exports = class AddCommand extends Command {
	constructor(client) {
		super(client, {
			name: 'add',
			//aliases: ['kitty-cat'],
			group: 'rss',
			memberName: 'add',
			description: 'Adds an RSS feed.',
			guildOnly: true,
			clientPermissions: ['MANAGE_CHANNELS'],
			args: [
				{
					key: 'url',
					prompt: 'No URL has been entered. Please enter a URL now.',
					type: 'string',
					validate: url => misc.validUrl(url),
				},
				{
					key: 'channel',
					prompt: 'No channel has been entered. Please enter a channel now.',
					type: 'channel',
				},
				{
					key: 'name',
					prompt: 'No name has been entered. Please enter a name now.',
					type: 'string',
				},
			],
		});
	}

	run(message, {url, channel, name}) {
		var feed = {
			name: name,
			url: url,
			channel: channel.id
		}

		db.g431975254525739008.rss.feeds.push(feed);

		var output = 'Added **' + name + '** to <#' + channel + '>.';
		misc.log(this.client, output, 'info', true);

		misc.saveDB(this.client);

		return message.say(output);
	}
};