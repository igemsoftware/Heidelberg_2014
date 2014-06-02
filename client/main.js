'use strict';

Router.map(function() {
	this.route('home', { path: '/' });
	this.route('classList', { path: '/c' });
	this.route('protocolList', { path: '/p' });
	this.route('newProtocol', { path: '/new' });
});
