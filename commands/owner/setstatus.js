const { Command } = require('discord.js-commando');

const misc = require('../../misc.js');

const config = require('../../settings/config.json');
const db = require('../../settings/database.json');

module.exports = class AddCommand extends Command {
	constructor(client) {
		super(client, {
			name: 'setstatus',
			//aliases: ['kitty-cat'],
			group: 'owner',
			memberName: 'setstatus',
			description: 'Sets the bots online status. Can be "online", "idle", "dnd" (do not disturb) or "invisible". Bot-owner only. This will overwrite config.json.',
			ownerOnly: true,
			args: [
				{
					key: 'status',
					prompt: 'No status has been entered. Please enter a status now.',
					type: 'string',
					oneOf: ['online', 'idle', 'dnd', 'invisible'],
				}
			],
		});
	}

	run(message, {status}) {
		this.client.user.setStatus(status);

		var output = 'Set bot status to ' + status;

		misc.log(this.client, output, 'info', true);

		config.bot.status = status;
		misc.saveConfig(this.client);

		return message.say(output);
	}
};