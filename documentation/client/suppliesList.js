'use strict';

function SuppliesListVM() {
	var self = this;
	self.manager = new OMManager();

	self.types = ko.observableArray();
	self.allTypesComputedObservable = ko.computed(function () {
		if (self.allTypesComputation) self.allTypesComputation.stop();
		self.allTypesComputation = Deps.autorun(function () {
			self.types(Types.find({ }, { sort: { name: 1 } }).map(function (type) {
				return self.manager.getType(type._id, undefined, type);
			}));
		});
	});
	self.typeFilter = ko.observable();

	self.sortOptions = [{ text: 'A-Z', mongo: { 'types.0.text': 1 } }, { text: 'Z-A', mongo: { 'types.0.text': -1 } }, { text: 'Oldest', mongo: { date: 1 } }, { text: 'Newest', mongo: { date: -1 } }];
	self.sort = ko.observable(self.sortOptions[0]);

	self.supplies = ko.observableArray();
	self.allSuppliesComputedObservable = ko.computed(function () {
		var typeFilter = self.typeFilter();

		if (self.allSuppliesComputation) self.allSuppliesComputation.stop();
		self.allSuppliesComputation = Deps.autorun(function () {
			self.supplies(Supplies.find(typeFilter ? { 'allTypes._id': typeFilter._id() } : { }, { sort: self.sort().mongo }).map(function (supply) {
				return self.manager.getSupply(supply._id, undefined, supply);
			}));
		});
	});

}
SuppliesListVM.prototype.constructor = SuppliesListVM;

SuppliesListVM.prototype.cleanup = function () {
	self.allSuppliesComputation.stop();
	self.allSuppliesComputedObservable.dispose();
	self.allTypesComputation.stop();
	self.allTypesComputedObservable.dispose();
};

SuppliesListVM.prototype.constructor = SuppliesListVM;

SuppliesListVM.prototype.setTypeFilter = function (type) {
	this.typeFilter(type);
};

Template.suppliesList.rendered = function () {
	var self = this;
	self.vm = new SuppliesListVM();

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

Template.suppliesList.destroyed = function () {
	_.each(this.nodesToClean, function (node) {
		ko.cleanNode(node);
	});
	this.vm.cleanup();
};
