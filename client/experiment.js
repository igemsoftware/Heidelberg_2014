'use strict';

function experimentsVM(data) {
	var self = this;
	if (data.experiment) {
		self.editMode = ko.observable(false);
		self.newMode = ko.observable(false);
	} else {
		self.editMode = ko.observable(true);
		self.newMode = ko.observable(true);
	}
	self.protocol = data.protocol;
	self.experiments = ko.observableArray([ new experimentVM(data) ]);
	self.colspan = ko.computed(function () {
		return self.experiments().length + 1;
	});
}

experimentsVM.prototype.addExperiment = function () {
	this.experiments.push(new experimentVM(this.protocol));
};

experimentsVM.prototype.removeExperiment = function (experiment) {
	this.experiments.remove(experiment);
};

experimentsVM.prototype.save = function () {
	_.each(this.experiments(), function (experiment) {
		experiment.save();
	});
	this.editMode(false);
};

function experimentVM(data) {
	var self = this;
	self.id = data.experiment && data.experiment._id;
	self.protocol = data.protocol;
	self.params = { };
	self.possibleSourcesCache = { };
	if (data.experiment) _.each(data.protocol.params, function (param) {
		if (param.multi) {
			self.params[param.name] = ko.observableArray(_.map(data.experiment.params[param.name], function (multiParam) {
				var obj = new experimentMultiParamVM(multiParam);
				obj.paramValue(_.find(self.possibleSources(param)(), function (psource) {
					return psource.experiment._id() == multiParam.paramValue.experiment && psource.product.name() == multiParam.paramValue.product;
				}));
				return obj;
			}));
		} else {
			self.params[param.name] = ko.observable(_.find(self.possibleSources(param)(), function (psource) {
				return psource.experiment._id() == data.experiment.params[param.name].experiment && psource.product.name() == data.experiment.params[param.name].product;
			}));
		}
	});

	self.values = data.experiment ? ko.mapping.fromJS(data.experiment.values) : { };
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

experimentVM.prototype.possibleSources = function (param) {
	if (!this.possibleSourcesCache[param.name]) {
		this.possibleSourcesCache[param.name] = ko.computed(function () {
			var ps = ko.meteor.find(Protocols, { 'products.allTypes._id': param.type._id });
			var pproducts = { };
			_.each(ps(), function (sourceProtocol) {
				pproducts[sourceProtocol._id()] = { name: sourceProtocol.name, products: [] };
				_.each(sourceProtocol.products(), function (product) {
					if (_.contains(ko.toJS(_.pluck(product.allTypes(), '_id')), param.type._id)) {
						pproducts[sourceProtocol._id()].products.push(product);
					}
				});
			});

			var xs = ko.meteor.find(Experiments, { 'protocol._id': { $in: _.keys(pproducts) } });

			return _.flatten(_.map(xs(), function (sourceExperiment) {
				return _.map(pproducts[sourceExperiment.protocol._id()].products, function (product) {
					var origin = product.name() + ' from ' + pproducts[sourceExperiment.protocol._id()].name() + ' performed on ' + sourceExperiment.date/*()*/;

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
									break;
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

experimentVM.prototype.getParam = function (param, array) {
	if (!this.params[param.name]) {
		this.params[param.name] = array ? ko.observableArray() : ko.observable();
	}
	return this.params[param.name];
};

experimentVM.prototype.addMultiParam = function (param) {
	var self = this;
	return function () {
		self.params[param.name].push(new experimentMultiParamVM());
	};
};

experimentVM.prototype.removeMultiParam = function (param) {
	var self = this;
	return function (multiParam) {
		self.params[param.name].remove(multiParam);
	};
};

experimentVM.prototype.input = function (step, input) {
	if (!this.values[step]) this.values[step] = { };
	if (!this.values[step][input]) this.values[step][input] = ko.observable();
	return this.values[step][input];
};

experimentVM.prototype.flatten = function () {
	var params = { };
	_.each(this.params, function (paramValue, paramName) {
		if (paramValue.push) {
			params[paramName] = _.map(paramValue(), function (multiParamVM) {
				return multiParamVM.flatten();
			});
		} else {
			params[paramName] = {
				experiment: paramValue().experiment._id(),
				product: paramValue().product.name(),
			};
		}
	});

	var values = { };
	_.each(this.values, function (stepValues, stepKey) {
		values[stepKey] = { };
		_.each(stepValues, function (input, inputKey) {
			values[stepKey][inputKey] = input();
		});
	});

	return {
		protocol: _.pick(this.protocol, '_id', 'name'),
		values: values,
		params: params
	};
};

experimentVM.prototype.save = function () {
	if (!this.id) this.id = Experiments.insert(this.flatten());
}

function experimentMultiParamVM(multiParam) {
	this.paramValue = ko.observable();
	this.values = multiParam ? ko.mapping.fromJS(multiParam.values) : { };
}

experimentMultiParamVM.prototype.input = function (step, input) {
	if (!this.values[step]) this.values[step] = { };
	if (!this.values[step][input]) this.values[step][input] = ko.observable();
	return this.values[step][input];
};

experimentMultiParamVM.prototype.flatten = function () {
	var values = { };
	_.each(this.values, function (stepValues, stepKey) {
		values[stepKey] = { };
		_.each(stepValues, function (input, inputKey) {
			values[stepKey][inputKey] = input();
		});
	});

	return {
		paramValue: {
			experiment: this.paramValue().experiment._id(),
			product: this.paramValue().product.name(),
		},
		values: values
	};
};

Template.experiment.rendered = function () {
	var self = this;
	setTimeout(function () {
	self.vm = new experimentsVM(self.data);

		self.nodesToClean = [];
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
};
