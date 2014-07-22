'use strict';

function ExperimentsVM(dataContainer) {
	var self = this;
	self.editMode = dataContainer.editMode;
	self.newMode = dataContainer.newMode;
	var data = dataContainer.data();
	self.DBData = data.experiment;
	self.version = data.experiment && (typeof dataContainer.version() == 'undefined' ? data.experiment.v.length - 1 : dataContainer.version());
	self.oldVersion = data.experiment && typeof dataContainer.version() != 'undefined' && dataContainer.version() != data.experiment.v.length - 1;
	self.performer = ko.observable(data.experiment && data.experiment.v[self.version].performer);

	self.protocol = new Protocol(data.protocol, data.experiment && data.experiment.v[self.version].protocol.v);
	self.experiments = ko.observableArray([ new ExperimentVM(self, data, self.version) ]);

	self.versions = data.experiment && _.map(data.experiment.v, function(version, index){
		return new VersionVM(version, index, Router.path('viewExperiment', { id: data.experiment._id }, { query: { v: index } }));
	}).reverse();

	self.colspan = ko.computed(function () {
		return self.experiments().length + 1;
	});
};

ExperimentsVM.prototype.addExperiment = function () {
	this.experiments.push(new ExperimentVM(this, { protocol: this.protocol }));
};

ExperimentsVM.prototype.removeExperiment = function (experiment) {
	this.experiments.remove(experiment);
};

ExperimentsVM.prototype.edit = function () {
	Router.go('viewExperiment', { id: this.experiments()[0]._id() }, { query: { edit: 1 } });
};


ExperimentsVM.prototype.save = function () {
	var self = this;
	_.each(this.experiments(), function (experiment) {
		experiment.save(self.performer(), undefined, self.experiments().length == 1);
	});

	self.editMode(false);
	self.newMode(false);

	if (self.experiments().length != 1) {
		Router.go('experimentList');
	}
};

ExperimentsVM.prototype.cancel = function () {
	if (this.newMode()) {
		Router.go('viewProtocol', { id: this.protocol._id });
	} else {
		Router.go('viewExperiment', { id: this.experiments()[0]._id() });
	}
};

ExperimentsVM.prototype.displayVersions = function() {
	$("#versionModal").modal();
}

function ExperimentVM(rootVM, data, version) {
	var self = this;
	Experiment.call(this, data, ko.unwrap(data.version), rootVM.editMode());

	self.finishDateUpdate = !data.experiment && setInterval(function () {
		self.finishDate(new Date());
	}, 1000);
}
ExperimentVM.prototype = new Experiment();
ExperimentVM.prototype.constructor = ExperimentVM;

ExperimentVM.prototype.getParam = function (param, array) {
	if (!this.params()[param.name()]) {
		this.params()[param.name()] = array ? ko.observableArray() : ko.observable({ editable: ko.observable(true) });
	}
	return this.params()[param.name()];
};

ExperimentVM.prototype.input = function (step, input) {
	if (!this.values[step]) this.values[step] = { };
	if (!this.values[step][input]) this.values[step][input] = ko.observable();
	return this.values[step][input];
};

ExperimentVM.prototype.save = function (performer, redirect) {
	var self = this;
	clearInterval(self.finishDateUpdate);
	self.performer(performer);
	var flat = self.flatten();
	if (!self._id()) {
		Meteor.call('insertExperiment', flat, function (error, result) {
			if (!error) {
				self._id(result);
				if (redirect) Router.go('viewExperiment', { id: self._id() });
			}
		});
	} else if (!isUnchanged(flat, self.data)) {
		Meteor.call('updateExperiment', self._id, flat);
	}
};

Template.experiment.rendered = function () {
	var self = this;
	self.vm = ko.computed(function () {
		return new ExperimentsVM(self.data);
	});

	self.nodesToClean = [];
	setTimeout(function () {
		for (var node = self.firstNode; node; node = node.nextSibling) {
			// apply bindings to each direct child element of the template
			// this does not apply to comments, i. e. containerless binding syntax!
			// to enable both, we'd need to parse the comments ourselves
			if (node.nodeType == Node.ELEMENT_NODE) {
				ko.applyBindings(self.vm, node);
				self.nodesToClean.push(node);
			}
		}
	}, 0);
};

Template.experiment.destroyed = function () {
	_.each(this.nodesToClean, function (node) {
		ko.cleanNode(node);
	});
	this.vm.dispose();
};
