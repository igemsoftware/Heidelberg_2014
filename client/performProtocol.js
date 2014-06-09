'use strict';

function performProtocolVM(protocol) {
	var self = this;
	self.protocol = protocol;
	self.experiments = ko.observableArray([ new performProtocolExperimentVM(protocol) ]);
	self.colspan = ko.computed(function () {
		return self.experiments().length + 1;
	});
}

performProtocolVM.prototype.addExperiment = function () {
	this.experiments.push(new performProtocolExperimentVM(this.protocol));
};

performProtocolVM.prototype.removeExperiment = function (experiment) {
	this.experiments.remove(experiments);
};

performProtocolVM.prototype.save = function () {
	_.each(this.experiments(), function (experiment) {
		Experiments.insert(experiment.flatten());
	});
};

function performProtocolExperimentVM(protocol) {
	var self = this;
	self.protocol = protocol;
	self.params = { };
	self.values = { };
}

performProtocolExperimentVM.prototype.possibleSources = function (param) {
	return ko.computed(function () {
		var ps = ko.meteor.find(Protocols, { 'products.allTypes._id': param.type });
		var pproducts = { };
		_.each(ps(), function (sourceProtocol) {
			pproducts[sourceProtocol._id()] = { name: sourceProtocol.name, products: [ ] };
			_.each(sourceProtocol.products(), function (product) {
				if (_.contains(ko.toJS(_.pluck(product.allTypes(), '_id')), param.type)) {
					pproducts[sourceProtocol._id()].products.push(product);
				}
			});
		});

		var xs = ko.meteor.find(Experiments, { protocol: { $in: _.keys(pproducts) } });

		return _.flatten(_.map(xs(), function (experiment) {
			return _.map(pproducts[experiment.protocol()].products, function (product) {
				return {
					experiment: experiment,
					product: product,
					text: product.name() + ' from ' + pproducts[experiment.protocol()].name() + ' performed on ' + experiment.date/*()*/
				};
			});
		}));
	});
};

performProtocolExperimentVM.prototype.singleParam = function (param) {
	if (!this.params[param.name]) {
		this.params[param.name] = ko.observable();
	}
	return this.params[param.name];
};

performProtocolExperimentVM.prototype.input = function (step, input) {
	if (!this.values[step]) this.values[step] = { };
	if (!this.values[step][input]) this.values[step][input] = ko.observable();
	return this.values[step][input];
};

performProtocolExperimentVM.prototype.flatten = function () {
	var params = { };
	_.each(this.params, function (paramValue, paramName) {
		params[paramName] = {
			experiment: paramValue().experiment._id(),
			product: paramValue().product.name(),
		};
	});

	var values = { };
	_.each(this.values, function (stepValues, stepKey) {
		values[stepKey] = { };
		_.each(stepValues, function (input, inputKey) {
			values[stepKey][inputKey] = input();
		});
	});

	return {
		protocol: this.protocol._id,
		values: values,
		params: params
	};
};

Template.performProtocol.rendered = function () {
	console.log('performProtocol.rendered', this);
	this.vm = new performProtocolVM(this.data);
	var node = this.firstNode;
	do {
		// apply bindings to each direct child element of the template
		// this does not apply to comments, i. e. containerless binding syntax!
		// to enable both, we'd need to parse the comments ourselves
		if (node.nodeType == Node.ELEMENT_NODE) ko.applyBindings(this.vm, node);
	} while (node = node.nextSibling);
};

Template.performProtocol.destroyed = function () {
	console.log('performProtocol.destroyed', this);
	var node = this.firstNode;
	do {
		if (node.nodeType == Node.ELEMENT_NODE) ko.cleanNode(node);
	} while (node = node.nextSibling);
};
