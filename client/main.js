'use strict';

Router.map(function() {
	var type = ko.observable();
	var supply = ko.observable();
	var protocol = ko.observable();
	var experiment = ko.observable();

	this.route('home', { path: '/' });
	this.route('typeList', { path: '/t' });
	this.route('newType', {
		path: '/newType',
		template: 'type',
		data: function () {
			type(null);
			return {type: type, editMode: true};
		},
	});
	this.route('viewType', {
		path: '/t/:id',
		template: 'type',
		data: function () {
			type(Types.findOne(this.params.id));
			return {type: type, editMode: this.params.edit ? true : false};
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('protocol', this.params.id); or so once autopublish is removed
			return { ready: function () { return Types.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
	this.route('suppliesList', { path: '/s' });
	this.route('obtainSupply', {
		path: '/obtainSupply',
		template: 'supply',
		data: function () {
			supply(null);
			return {supply: supply, editMode: true};
		},
	});
	this.route('viewSupply', {
		path: '/s/:id',
		template: 'supply',
		data: function () {
			supply(Supplies.findOne(this.params.id));
			return {supply: supply, editMode: this.params.edit ? true : false};
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('protocol', this.params.id); or so once autopublish is removed
			return { ready: function () { return Supplies.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
	this.route('protocolList', { path: '/p' });
	this.route('newProtocol', {
		path: '/newProtocol',
		template: 'protocol',
		data: function () {
			protocol(null);
			return {protocol: protocol, editMode: true};
		}
	});
	this.route('viewProtocol', {
		path: '/p/:id',
		template: 'protocol',
		data: function () {
			protocol(Protocols.findOne(this.params.id));
			return {protocol: protocol, editMode: this.params.edit ? true : false};
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
			return {data: experiment, editMode: true, newMode: true}; 
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
			console.log(experiment());
			return {data: experiment, editMode: this.params.edit ? true : false, newMode: false};
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
