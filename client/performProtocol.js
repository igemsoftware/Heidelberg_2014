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
	this.experiments.remove(experiment);
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
	self.possibleSourcesCache = { };
}

function resolvePropertyReference(product, property, sourceExperiment) {
	var source = product.propertyBindings[property].source;
	switch (ko.utils.unwrapObservable(source.type)) {
		case 'input':
			return ko.utils.unwrapObservable(sourceExperiment.values[ko.utils.unwrapObservable(source.input.step)][ko.utils.unwrapObservable(source.input.input)]);
		case 'paramProperty':
			var sourceSourceExperiment = Experiments.findOne(ko.utils.unwrapObservable(sourceExperiment.params[ko.utils.unwrapObservable(source.param)].experiment));
			var sourceSourceProtocol = Protocols.findOne(sourceSourceExperiment.protocol);
			var sourceProducts = { };
			_.each(sourceSourceProtocol.products, function (sourceProduct) {
				sourceProducts[sourceProduct.name] = sourceProduct;
			});
			return resolvePropertyReference(sourceProducts[ko.utils.unwrapObservable(sourceExperiment.params[ko.utils.unwrapObservable(source.param)].product)], ko.utils.unwrapObservable(source.paramProperty.name), sourceSourceExperiment);
	}
}

performProtocolExperimentVM.prototype.possibleSources = function (param) {
	if (!this.possibleSourcesCache[param.name]) {
		this.possibleSourcesCache[param.name] = ko.computed(function () {
			var ps = ko.meteor.find(Protocols, { 'products.allTypes._id': param.type });
			var pproducts = { };
			_.each(ps(), function (sourceProtocol) {
				pproducts[sourceProtocol._id()] = { name: sourceProtocol.name, products: [] };
				_.each(sourceProtocol.products(), function (product) {
					if (_.contains(ko.toJS(_.pluck(product.allTypes(), '_id')), param.type)) {
						pproducts[sourceProtocol._id()].products.push(product);
					}
				});
			});

			var xs = ko.meteor.find(Experiments, { protocol: { $in: _.keys(pproducts) } });

			return _.flatten(_.map(xs(), function (sourceExperiment) {
				return _.map(pproducts[sourceExperiment.protocol()].products, function (product) {
					var origin = product.name() + ' from ' + pproducts[sourceExperiment.protocol()].name() + ' performed on ' + sourceExperiment.date/*()*/;

					var texts = [];
					_.each(product.types(), function (productType) {
						productType = Types.findOne(productType._id());
						var text = '';
						_.each(productType.text, function (part) {
							switch (part.type) {
								case 'text':
									text = text + part.text;
									break;
								case 'propertyReference':
									text = text + resolvePropertyReference(product, part.property, sourceExperiment);
							}
						});

						if (text) texts.push(text);
					});

					return {
						experiment: sourceExperiment,
						product: product,
						text: texts.length ? texts.join('/') + ' (' + origin + ')' : origin
					};
				});
			}));
		});
	}
	return this.possibleSourcesCache[param.name];
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
		console.log(node);
		if (node.nodeType == Node.ELEMENT_NODE) ko.cleanNode(node);
	} while (node = node.nextSibling);
};
