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
	self.performer = ko.observable(data.experiment && data.experiment.performer);
	self.protocol = data.protocol;
	self.experiments = ko.observableArray([ new experimentVM(data) ]);
	self.colspan = ko.computed(function () {
		return self.experiments().length + 1;
	});
}

experimentsVM.prototype.addExperiment = function () {
	this.experiments.push(new experimentVM({ protocol: this.protocol }));
};

experimentsVM.prototype.removeExperiment = function (experiment) {
	this.experiments.remove(experiment);
};

experimentsVM.prototype.save = function () {
	var self = this;
	_.each(this.experiments(), function (experiment) {
		experiment.save(self.performer);
	});
	self.editMode(false);
};

function experimentVM(data) {
	var self = this;
	self.id = data.experiment && data.experiment._id;
	self.protocol = data.protocol;
	self.params = { };
	self.possibleSourcesCache = { };
	if (data.experiment) _.each(data.protocol.params, function (param) {
		var sourceParam = data.experiment.params[CryptoJS.MD5(param.name).toString()]
		if (param.multi) {
			self.params[param.name] = ko.observableArray(_.map(sourceParam, function (multiParam) {
				var obj = new experimentMultiParamVM(multiParam);
				obj.paramValue(_.find(self.possibleSources(param)(), function (psource) {
					if (psource.type != multiParam.paramValue.type) return false;
					switch (psource.type) {
						case 'supply':
							return psource.supply._id() == multiParam.paramValue.supply;
						case 'experiment':
							return psource.experiment._id() == multiParam.paramValue.experiment && psource.product.name() == multiParam.paramValue.product;
					}
					return psource.experiment._id() == multiParam.paramValue.experiment && psource.product.name() == multiParam.paramValue.product;
				}));
				return obj;
			}));
		} else {
			self.params[param.name] = ko.observable(_.find(self.possibleSources(param)(), function (psource) {
				if (psource.type != sourceParam.type) return false;
				switch (psource.type) {
					case 'supply':
						return psource.supply._id() == sourceParam.supply;
					case 'experiment':
						return psource.experiment._id() == sourceParam.experiment && psource.product.name() == sourceParam.product;
				}
			}));
		}
	});

	self.values = data.experiment ? ko.mapping.fromJS(data.experiment.values) : { };

	self.finishDate = ko.observable(data.experiment ? data.experiment.finishDate : new Date());
	self.finishDateUpdate = !data.experiment && setInterval(function () {
		self.finishDate(new Date());
	}, 1000);

	self.notes = ko.observable(data.experiment && data.experiment.notes);
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

			var xs = ko.meteor.find(Experiments, { 'protocol._id': { $in: _.keys(pproducts) } }, { sort: { finishDate: -1 } });

			var ss = ko.meteor.find(Supplies, { 'allTypes._id': param.type._id });
			var supplies = _.map(ss(), function (supply) {
				var origin = 'obtained on ' + supply.date();

				var texts = [];
				_.each(supply.types(), function (supplyType) {
					if (supplyType.text()) texts.push(supplyType.text());
				});

				return {
					type: 'supply',
					supply: supply,
					text: texts.length ? texts.join('/') + ' (' + origin + ')' : origin
				};
			});

			var experiments = _.flatten(_.map(xs(), function (sourceExperiment) {
				return _.map(pproducts[sourceExperiment.protocol._id()].products, function (product, pid) {
					var productNameHash = CryptoJS.MD5(product.name()).toString();
					var origin = product.name() + ' from ' + pproducts[sourceExperiment.protocol._id()].name() + ' performed on ' + sourceExperiment.finishDate();

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
									var value = sourceExperiment.products[productNameHash][(part.property.from || productType)._id].properties[CryptoJS.MD5(part.property.name).toString()];
									if (value) text = text + value();
									break;
							}
						});

						if (text) texts.push(text);
					});

					return {
						type: 'experiment',
						experiment: sourceExperiment,
						product: product,
						text: texts.length ? texts.join('/') + ' (' + origin + ')' : origin
					};
				});
			}));

			var merged = [];
			while (supplies.length && experiments.length) {
				if (supplies[0].supply.date() > experiments[0].experiment.finishDate()) {
					merged.push(supplies[0]);
					supplies.shift();
				} else {
					merged.push(experiments[0]);
					experiments.shift();
				}
			}
			Array.prototype.push.apply(merged, supplies);
			Array.prototype.push.apply(merged, experiments);
			return merged;
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

experimentVM.prototype.flatten = function (performer) {
	var self = this;

	var params = { };
	_.each(self.params, function (paramValue, paramName) {
		var paramNameHash = CryptoJS.MD5(paramName).toString();
		if (paramValue.push) {
			params[paramNameHash] = _.map(paramValue(), function (multiParamVM) {
				return multiParamVM.flatten();
			});
		} else {
			switch (paramValue().type) {
				case 'supply':
					params[paramNameHash] = {
						type: 'supply',
						supply: paramValue().supply._id()
					};
					break;
				case 'experiment':
					params[paramNameHash] = {
						type: 'experiment',
						experiment: paramValue().experiment._id(),
						product: paramValue().product.name(),
					};
					break;
			}
			
		}
	});

	var products = { };
	_.each(self.protocol.products, function (product) {
		var productNameHash = CryptoJS.MD5(product.name).toString()
		products[productNameHash] = { };

		_.each(product.types, function (type) {
			type = Types.findOne(type._id);
			_.each(type.allProperties, function (property) {
				var propertyNameHash = CryptoJS.MD5(property.name).toString();
				var propertyTypeId = (property.from || type)._id;
				if (!products[productNameHash][propertyTypeId]) products[productNameHash][propertyTypeId] = { properties: { } };

				var binding = product.propertyBindings[propertyTypeId][propertyNameHash];
				switch (binding.source.type) {
					case 'input':
						products[productNameHash][propertyTypeId].properties[propertyNameHash] = self.values[binding.source.input.step][binding.source.input.input]();
						break;
					case 'paramProperty':
						var param = self.params[binding.source.param];
						var paramDef = _.find(self.protocol.params, function (pparam) {
							return pparam.name == binding.source.param;
						});
						switch (param().type) {
							case 'supply':
								products[productNameHash][propertyTypeId].properties[propertyNameHash] = ko.utils.unwrapObservable(param().supply.properties[propertyTypeId][propertyNameHash].value);
								break;
							case 'experiment':
								products[productNameHash][propertyTypeId].properties[propertyNameHash] = ko.utils.unwrapObservable(param().experiment.products[CryptoJS.MD5(param().product.name()).toString()][(binding.source.paramProperty.from || paramDef.type)._id].properties[CryptoJS.MD5(binding.property.name).toString()]);
								break;
						};
						break;
				}
			});
		});
	});

	return {
		protocol: _.pick(self.protocol, '_id', 'name'),
		values: ko.toJS(self.values),
		params: params,
		finishDate: self.finishDate(),
		notes: self.notes(),
		performer: performer(),
		products: products
	};
};

experimentVM.prototype.save = function (performer) {
	clearInterval(this.finishDateUpdate);
	if (!this.id) this.id = Experiments.insert(this.flatten(performer));
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
	switch (this.paramValue().type) {
		case 'supply':
			return {
				paramValue: {
					type: 'supply',
					supply: this.paramValue().supply._id()
				},
				values: ko.toJS(this.values)
			};
		case 'experiment':
			return {
				paramValue: {
					type: 'experiment',
					experiment: this.paramValue().experiment._id(),
					product: this.paramValue().product.name(),
				},
				values: ko.toJS(this.values)
			};
	}
};

Template.experiment.rendered = function () {
	var self = this;
	self.vm = ko.computed(function () {
		return new experimentsVM(self.data());
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
