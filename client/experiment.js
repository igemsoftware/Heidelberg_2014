'use strict';

function ExperimentsVM(dataContainer) {
	var self = this;
	self.manager = new OMManager();
	self.editMode = dataContainer.editMode;
	self.newMode = dataContainer.newMode;
	var data = dataContainer.data();
	self.DBData = data.experiment;
	self.version = data.experiment && (typeof dataContainer.version() == 'undefined' ? data.experiment.v.length - 1 : dataContainer.version());
	self.oldVersion = data.experiment && typeof dataContainer.version() != 'undefined' && dataContainer.version() != data.experiment.v.length - 1;
	self.performer = ko.observable(data.experiment && data.experiment.v[self.version].performer);

	var experiment = new ExperimentVM(self, data, self.version);
	self.protocol = data.experiment ? experiment.protocol : self.manager.getProtocol(data.protocol._id, undefined, data.protocol);
	self.experiments = ko.observableArray([experiment]);

	self.versions = data.experiment && _.map(data.experiment.v, function(version, index){
		return new VersionVM(version, index, Router.path('viewExperiment', { id: data.experiment._id }, { query: { v: index } }));
	}).reverse();

	self.colspan = ko.computed(function () {
		return self.experiments().length + 1;
	});
};

ExperimentsVM.prototype.addExperiment = function () {
	this.experiments.push(new ExperimentVM(this, { protocol: this.protocol.DBData }));
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
		experiment.save(self.performer(), self.experiments().length == 1);
	});

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
};

ExperimentsVM.prototype.cleanup = function () {
	_.each(this.experiments(), function (experiment) {
		experiment.cleanup();
	});
};

function ExperimentVM(rootVM, data, version) {
	var self = this;
	self.rootVM = rootVM;
	Experiment.call(this, self.rootVM.manager, data, ko.unwrap(data.version), rootVM.editMode());

	self.finishDateUpdate = !data.experiment && setInterval(function () {
		self.finishDate(new Date());
	}, 1000);

	self.searchSuppliesCount = 0;
	self.searchSuppliesComputation = null;

	self.searchExperimentsCount = 0;
	self.searchExperimentsComputation = null;
}
ExperimentVM.prototype = new Experiment();
ExperimentVM.prototype.constructor = ExperimentVM;

ExperimentVM.prototype.getParam = function (param) {
	if (!this.params()[param.name()]) {
		this.params()[param.name()] = param.multi() ? ko.observableArray() : ko.observable(new ExperimentParamSourceNull());
	}
	return this.params()[param.name()];
};

ExperimentVM.prototype.querySourceSupplies = function (param, query, callback) {
	var self = this;
	var currentCount = ++self.searchSuppliesCount;
	Meteor.call('searchSupplies', query, param.type()._id(), function (error, ids) {
		if (!error) {
			if (currentCount !== self.searchSuppliesCount) return;
			if (self.searchSuppliesComputation) self.searchSuppliesComputation.stop();
			self.searchSuppliesComputation = Deps.autorun(function () {
				callback(_.map(ids, function (id) {
					return new ExperimentParamSourceSupply(self.rootVM.manager.getSupply(id));
				}));
			});
		}
	});
};

ExperimentVM.prototype.querySourceExperiments = function (param, query, callback) {
	var self = this;
	var currentCount = ++self.searchExperimentsCount;
	Meteor.call('searchExperiments', query, _.pluck(Protocols.find({ 'products.allTypes._id': param.type()._id() }).fetch(), '_id'), function (error, experimentProducts) {
		if (!error) {
			if (currentCount !== self.searchExperimentsCount) return;
			if (self.searchExperimentsComputation) self.searchExperimentsComputation.stop();
			self.searchExperimentsComputation = Deps.autorun(function () {
				callback(_.map(experimentProducts, function (experimentProduct) {
					var experiment = self.rootVM.manager.getExperiment(experimentProduct.experiment_id);
					return new ExperimentParamSourceExperiment(experiment, _.find(experiment.protocol.products(), function (protocolProduct) {
						return CryptoJS.MD5(protocolProduct.name()).toString() == experimentProduct.productMD5;
					}));
				}));
			});
		}
	});
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
	} else {
		if (!isUnchanged(flat, self.data)) Meteor.call('updateExperiment', self._id, flat);
		if (redirect) Router.go('viewExperiment', { id: self._id() });
	}
};

ExperimentVM.prototype.cleanup = function () {
	if (this.searchSuppliesComputation) this.searchSuppliesComputation.stop();
	if (this.searchExperimentsComputation) this.searchExperimentsComputation.stop();
};

Template.experiment.rendered = function () {
	var self = this;
	self.vm = ko.computed(function () {
		return new ExperimentsVM(self.data);
	});

	self.nodesToClean = [self.find('#knockoutContainer')];
	ko.applyBindings(self.vm, self.nodesToClean[0]);
};

Template.experiment.destroyed = function () {
	_.each(this.nodesToClean, function (node) {
		ko.cleanNode(node);
	});
	this.vm().cleanup();
	this.vm.dispose();
};
