console.log('loaded')

var test5 = 1;

function rss_parseAllFeeds (guild) {
	//var test = parseInt(db.general.rss.lastChecked) + 1800000; //1598445307526 1800000
	if (Date.now() > db.general.rss.lastChecked + 1800000) {
		var feeds = db.g431975254525739008.rss.feeds;
		for (var num = 0; num < feeds.length; num++) {
			//await parseFeed(feeds[num]);
		}

		db.general.rss.lastChecked = Date.now();
		saveGuilds();
		console.log('Last checked date has been updated to ' + new Date(Date.now()).toISOString() + '.');
	} else {
		console.log('Skipped parsing RSS feeds as 30mins haven\'t passed yet.');
	}
}

async function rss_parseFeed (feedObj) {
	var url = feedObj.url;
	var channel = feedObj.channel;
	var name = feedObj.name;

	console.log('Parsing ' + name + '...');

	var feed = await parser.parseURL(url);

	var result = [];

	for (var num = 0; num < feed.items.length; num++) {
		var item = feed.items[num];
		if (Date.parse(item.pubDate) > db.general.rss.lastChecked) {
			result.push(item);
		}
	}

	if (result.length > 0) {
		sendMessage(channel, ':newspaper: | **' + result[0].title + '**\n\n' + result[0].link);
	}
	if (result.length === 2) {
		sendMessage(channel, ':newspaper: | **' + result[1].title + '**\n\n' + result[1].link);
	} else if (result.length > 2) {
		sendMessage(channel, '...and ' + (parseInt(result.length) - 1) + ' more entries from **' + name + '**: ' + url);
	}
	console.log('Finished parsing ' + name + '.');
}