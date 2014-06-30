'use strict';

Template.masterTemplate.events({
	'click #loginNag': function (ev, tmpl) {
		setTimeout(function () {
			$('#login-dropdown-list').addClass('open');
		}, 0);
	}
});
/* Workaround for Iron router */


Router.map(function() {
	var type = ko.observable();
	var typeVersion = ko.observable();
	var supply = ko.observable();
	var supplyVersion = ko.observable();
	var protocol = ko.observable();
	var protocolVersion = ko.observable();
	var experiment = ko.observable();
	var experimentVersion = ko.observable();

	var newMode = ko.observable();
	var editMode = ko.observable();

	/* Workaround for Iron router */
	var basepath = '/' + Meteor.absoluteUrl().replace(/http:\/\/.*?\//,"", ""); 

	console.log(basepath);

	this.route('home', { path: basepath });
	this.route('typeList', { path: basepath+'t' });
	this.route('newType', {
		path: basepath+'newType',
		template: 'type',
		data: function () {
			type(null);
			editMode(true);
			return { type: type, editMode: editMode, version: typeVersion };
		},
	});
	this.route('viewType', {
		path: basepath+'t/:id',
		template: 'type',
		data: function () {
			type(Types.findOne(this.params.id));
			editMode(!!this.params.edit);
			typeVersion(this.params.v);
			return { type: type, editMode: editMode, version: typeVersion };
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('protocol', this.params.id); or so once autopublish is removed
			return { ready: function () { return Types.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
	this.route('suppliesList', { path: basepath+'s' });
	this.route('obtainSupply', {
		path: basepath+'obtainSupply',
		template: 'supply',
		data: function () {
			supply(null);
			editMode(true);
			return { supply: supply, editMode: editMode, version: supplyVersion };
		},
	});
	this.route('viewSupply', {
		path: basepath+'s/:id',
		template: 'supply',
		data: function () {
			supply(Supplies.findOne(this.params.id));
			editMode(this.params.edit);
			supplyVersion(this.params.v);
			return { supply: supply, editMode: editMode, version: supplyVersion };
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('protocol', this.params.id); or so once autopublish is removed
			return { ready: function () { return Supplies.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
	this.route('protocolList', { path: basepath+'p' });
	this.route('newProtocol', {
		path: basepath+'newProtocol',
		template: 'protocol',
		data: function () {
			protocol(null);
			editMode(true);
			return { protocol: protocol, editMode: editMode, version: protocolVersion };
		}
	});
	this.route('viewProtocol', {
		path: basepath+'p/:id',
		template: 'protocol',
		data: function () {
			protocol(Protocols.findOne(this.params.id));
			editMode(this.params.edit);
			protocolVersion(this.params.v);
			return { protocol: protocol, editMode: editMode, version: protocolVersion };
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('protocol', this.params.id); or so once autopublish is removed
			return { ready: function () { return Protocols.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
	this.route('performProtocol', {
		path: basepath+'perform/:id',
		template: 'experiment',
		data: function () {
			experiment({
				protocol: Protocols.findOne(this.params.id)
			});
			newMode(true);
			editMode(true);
			return { data: experiment, newMode: newMode, editMode: editMode, version: experimentVersion }; 
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('protocol', this.params.id); or so once autopublish is removed
			return { ready: function () { return Protocols.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
	this.route('experimentList', { path: basepath+'x' });
	this.route('viewExperiment', {
		path: basepath+'x/:id',
		template: 'experiment',
		data: function () {
			var data = {
				experiment: Experiments.findOne(this.params.id)
			};
			data.protocol = Protocols.findOne(data.experiment.protocol._id);
			experiment(data);
			newMode(false);
			editMode(this.params.edit);
			experimentVersion(this.params.v);
			return { data: experiment, newMode: newMode, editMode: editMode, version: experimentVersion };
		},
		waitOn: function () {
			var self = this;
			// TODO: just return Meteor.subscribe('experiment', this.params.id); or so once autopublish is removed
			return { ready: function () { return Experiments.findOne(self.params.id) != undefined; } };
		},
		loadingTemplate: 'loading'
	});
	this.route('options', {
		path: basepath+'options',
		template: 'options'
	});
});

Router.onBeforeAction('loading');
Router.configure({layoutTemplate: 'masterTemplate'});
if(Meteor.isClient){
	Template.navItems.helpers({
		activeIfInPath: function (path) {			
			var currentRoute = Router.current();
			return currentRoute && (currentRoute.path.indexOf(path) == 0) ? 'active' : '';
			}
	});
}

Accounts.ui.config({passwordSignupFields: 'USERNAME_AND_EMAIL'});

Meteor.subscribe('Everything');