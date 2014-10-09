'use strict';

UI.registerHelper('experiments', function () {
	return Experiments.find({ }, { sort: { finishDate: -1 } });
});

function ExperimentsListVM() {
	var self = this;
	self.manager = new OMManager();

	self.protocols = ko.observableArray();
	self.allProtocolsComputedObservable = ko.computed(function () {
		if (self.allProtocolsComputation) self.allProtocolsComputation.stop();
		self.allProtocolsComputation = Deps.autorun(function () {
			self.protocols(Protocols.find({ }, { sort: { name: 1 } }).map(function (protocol) {
				return self.manager.getProtocol(protocol._id, undefined, protocol);
			}));
		});
	});
	self.protocolFilter = ko.observable();

	self.sortOptions = [{ text: 'A-Z', mongo: { 'protocol.name': 1 } }, { text: 'Z-A', mongo: { 'protocol.name': -1 } }, { text: 'Oldest', mongo: { finishDate: 1 } }, { text: 'Newest', mongo: { finishDate: -1 } }];
	self.sort = ko.observable(self.sortOptions[3]);

	self.experiments = ko.observableArray();
	self.allExperimentsComputedObservable = ko.computed(function () {
		var protocolFilter = self.protocolFilter();

		if (self.allExperimentsComputation) self.allExperimentsComputation.stop();
		self.allExperimentsComputation = Deps.autorun(function () {
			self.experiments(Experiments.find(protocolFilter ? { 'protocol._id': protocolFilter._id() } : { }, { sort: self.sort().mongo }).map(function (experiment) {
				return self.manager.getExperiment(experiment._id, undefined, experiment);
			}));
		});
	});

}
ExperimentsListVM.prototype.constructor = ExperimentsListVM;

ExperimentsListVM.prototype.cleanup = function () {
	this.allExperimentsComputation.stop();
	this.allExperimentsComputedObservable.dispose();
	this.allProtocolsComputation.stop();
	this.allProtocolsComputedObservable.dispose();
};

Template.experimentList.rendered = function () {
	var self = this;
	self.vm = new ExperimentsListVM();

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

Template.experimentList.destroyed = function () {
	_.each(this.nodesToClean, function (node) {
		ko.cleanNode(node);
	});
	this.vm.cleanup();
};
