'use strict';

Router.map(function() {
	this.route('home', { path: '/' });
	this.route('typeList', { path: '/t' });
	this.route('newType', { path: '/newType' });
	this.route('protocolList', { path: '/p' });
	this.route('newProtocol', { path: '/newProtocol' });
	this.route('performProtocolWrapper', { path: '/p/:id/perform', data: function () {
		return Protocols.findOne(this.params.id);
	} });
});
