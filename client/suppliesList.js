'use strict';

function SuppliesListVM() {
	var self = this;
	self.manager = new OMManager();

	self.sortOptions = [{ text: 'A-Z', mongo: { 'types.0.text': 1 } }, { text: 'Z-A', mongo: { 'types.0.text': -1 } }, { text: 'Oldest', mongo: { date: 1 } }, { text: 'Newest', mongo: { date: -1 } }];
	self.sort = ko.observable(self.sortOptions[0]);

	var supplies = ko.computed(function () {
		console.log(self.sort().mongo);
		return ko.meteor.find(Supplies, { }, { sort: self.sort().mongo })();
	});
	self.supplies = ko.computed(function () {
		return _.map(supplies(), function (supply) {
			return self.manager.getSupply(supply._id(), undefined, ko.toJS(supply));
		});
	});
}
SuppliesListVM.prototype.constructor = SuppliesListVM;

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
};
