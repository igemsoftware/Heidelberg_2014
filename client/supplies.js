'use strict';

UI.registerHelper('supplies', function () {
	return Supplies.find({ }, { sort: { date: -1 } });
});

Template.suppliesList.text = function () {
	return _.pluck(this.types, 'text').join('/');
};

function SupplyVM(data) {
	var self = this;
	self.editMode = data.editMode;
	Supply.call(this, data.supply(), ko.unwrap(data.version), self.editMode());

	self.versions = self.DBData ? _.map(self.DBData.v, function (version, index) {
		return new VersionVM(version, index, Router.path('viewSupply', { id: self._id() }, { query: { v: index } }));
	}).reverse() : [];

	self.dateUpdate = !self.DBData && setInterval(function () {
		self.date(new Date());
	}, 1000);
}
SupplyVM.prototype = new Supply();
SupplyVM.prototype.constructor = SupplyVM;

SupplyVM.prototype.edit = function () {
	Router.go('viewSupply', { id: this._id() }, { query: { edit: 1 } });
};

SupplyVM.prototype.save = function () {
	var self = this;
	clearInterval(self.dateUpdate);
	var flat;
	try {
		flat = self.flatten();
	} catch (e) {
		// The result being thrown as an exception signals a failed cascading update, but this doesn't matter here
		// Check if the exception really is the result first
		if (e instanceof Error) throw e;
		flat = e;
	}

	if (!this._id()) {
		Meteor.call('insertSupply', flat, function (error, result) {
			if (!error) {
				self._id(result);
				Router.go('viewSupply', { id: self._id() });
			}
		});
	} else {
		if (!isUnchanged(flat, this.DBData)) Meteor.call('updateSupply', this._id(), flat);
		Router.go('viewSupply', { id: this._id() });
	}
};

SupplyVM.prototype.cancel = function () {
	if (this._id()) {
		Router.go('viewSupply', { id: this._id() });
	} else {
		Router.go('suppliesList');
	}
};

SupplyVM.prototype.displayVersions = function() {
	$("#versionModal").modal();
};

Template.supply.rendered = function () {
	var self = this;
	self.vm = ko.computed(function () {
		return new SupplyVM(self.data);
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

Template.supply.destroyed = function () {
	_.each(this.nodesToClean, function (node) {
		ko.cleanNode(node);
	});
	this.vm.dispose();
};
