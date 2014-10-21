'use strict';

UI.registerHelper('protocols', function () {
	return Protocols.find();
});

UI.registerHelper('featuredProtocols', function () {
	return Protocols.find({ }, { limit: 10 });
});
