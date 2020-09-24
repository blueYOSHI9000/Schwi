const { Command } = require('discord.js-commando');

const misc = require('../../misc.js');

const config = require('../../settings/config.json');

module.exports = class AddCommand extends Command {
	constructor(client) {
		super(client, {
			name: 'kill',
			//aliases: ['kitty-cat'],
			group: 'owner',
			memberName: 'kill',
			description: 'Immediately stop executing the bot.',
			ownerOnly: true,
		});
	}

	run(message) {
		misc.log(this.client, 'info', 'Schwi was shut down by ' + message.author.username + '#' + message.author.discriminator + ' by using `schwi.kill`.');
		message.say('<@' + message.author.id + '> Shutting down...');
		setTimeout(function () {process.exit(0);}, 50); //small delay needed as the message wouldn't be sent otherwise.
	}
};