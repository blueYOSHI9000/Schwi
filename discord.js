function sendMessage (channel, text) {
	client.channels.cache.get(channel).send(text);
}

function parseMessage (message) {
	if (message.author.bot === true) {
		return;
	}

	var args = message.content.slice(prefix.length).trim().split(/ +/);
	var command = args.shift().toLowerCase();






	//message.channel.send(prefix);
}