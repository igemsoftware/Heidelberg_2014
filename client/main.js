'use strict';

Router.map(function() {
	var type = ko.observable();
	var protocol = ko.observable();
	var experiment = ko.observable();

	this.route('home', { path: '/' });
	this.route('typeList', { path: '/t' });
	this.route('newType', {
		path: '/newType',
		template: 'type',
		data: function () {
			type(null);
			return type;
		},
	});
	this.route('viewType', {
		path: '/t/:id',
		template: 'type',
		data: function () {
			type(Types.findOne(this.params.id));
			return type;
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('protocol', this.params.id); or so once autopublish is removed
			return { ready: function () { return Types.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
	this.route('protocolList', { path: '/p' });
	this.route('newProtocol', {
		path: '/newProtocol',
		template: 'protocol',
		data: function () {
			protocol(null);
			return protocol;
		}
	});
	this.route('viewProtocol', {
		path: '/p/:id',
		template: 'protocol',
		data: function () {
			protocol(Protocols.findOne(this.params.id));
			return protocol;
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('protocol', this.params.id); or so once autopublish is removed
			return { ready: function () { return Protocols.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
	this.route('performProtocol', {
		path: '/perform/:id',
		template: 'experiment',
		data: function () {
			experiment({
				protocol: Protocols.findOne(this.params.id)
			});
			return experiment;
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('protocol', this.params.id); or so once autopublish is removed
			return { ready: function () { return Protocols.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
	this.route('experimentList', { path: '/x' });
	this.route('viewExperiment', {
		path: '/x/:id',
		template: 'experiment',
		data: function () {
			var data = {
				experiment: Experiments.findOne(this.params.id)
			};
			data.protocol = Protocols.findOne(data.experiment.protocol._id);
			experiment(data);
			return experiment;
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('experiment', this.params.id); or so once autopublish is removed
			return { ready: function () { return Experiments.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
});

Router.onBeforeAction('loading');
