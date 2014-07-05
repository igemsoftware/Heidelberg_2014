'use strict';

Template.experiment.rendered = function () {
	var self = this;
	self.vm = ko.computed(function () {
		$('#container').width('');
		return new experimentsVM(self.data);
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
