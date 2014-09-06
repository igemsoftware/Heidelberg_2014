Experiment = function (manager, data, version, tryUpdate) {
	var self = this;
	self.manager = manager;
	self.DBData = data && data.experiment;
	self._id = ko.observable(self.DBData && self.DBData._id);
	self.version = version === undefined ? self.DBData && self.DBData.v.length - 1 : version;
	self.oldVersion = self.DBData && self.version != self.DBData.v.length - 1;
	self.data = self.DBData && self.DBData.v[self.version];

	self.params = ko.observable({ });
	self.possibleSourceSuppliesCache = { };
	self.possibleSourceExperimentsCache = { };

	self.protocol = self.manager && self.manager.getProtocol(data && (self.data || data).protocol._id, self.data && self.data.protocol.v);

	self.values = { };

	self.products = { };

	if (data && data.experiment) {
		var protocolUpdateSuccessful = false;
		var possibleSourceSuppliesCacheBackup = self.possibleSourceSuppliesCache;
		var possibleSourceExperimentsCacheBackup = self.possibleSourceExperimentsCache;

		var params = ko.computed({
			read: function () {
				var _params = { };
				_.each(self.protocol.params(), function (param) {
					var paramSource = self.data.params[CryptoJS.MD5(param.name()).toString()];
					if (param.multi()) {
						_params[param.name()] = ko.observableArray(_.map(paramSource, function (paramSource) {
							return new ExperimentParamMultiSource(self, param, paramSource, tryUpdate);
						}));
					} else {
						_params[param.name()] = self.getExperimentParamSource(param, paramSource, tryUpdate);
					}
				});
				return _params;
			},
			deferEvaluation: true,
		});

		var values = ko.mapping.fromJS(self.data.values);
		var products = ko.mapping.fromJS(self.data.products);

		if (tryUpdate && self.protocol.DBData.v.length - 2 == self.protocol.version) {
			if (self.protocol.versionMappings) {
				// Assume success for now
				protocolUpdateSuccessful = true;

				var newParams = { };
				_.each(self.protocol.versionMappings.params, function (paramMapping) {
					newParams[paramMapping.param] = params[paramMapping.source];
					var param = _.find(self.protocol.params, function (pparam) {
						return pparam.name == paramMapping.param;
					});
					switch (newParams[paramMapping.param]().type) {
						case 'supply':
							if (!_.find(self.possibleSourceSupplies(param)(), function (psource) {
								return psource.supply._id() == newParams[paramMapping.param]().supply._id();
							})) protocolUpdateSuccessful = false;
							break;
						case 'experiment':
							if (!_.find(self.possibleSourceExperiments(param)(), function (psource) {
								return psource.experiment._id() == newParams[paramMapping.param]().experiment._id();
							})) protocolUpdateSuccessful = false;
							break;
					}
				});
				self.params(newParams);

				if (protocolUpdateSuccessful) {
					var newValues = { };
					_.each(self.protocol.versionMappings.inputs, function (stepInputMappings, stepIdx) {
						_newValues[stepIdx] = { };
						_.each(stepInputMappings, function (inputMapping, inputIdx) {
							if (values[inputMapping.step] && values[inputMapping.input] !== undefined) {
								newValues[stepIdx][inputIdx] = values[inputMapping.step][inputMapping.input];
							}
							if (self.protocol.steps[stepIdx].inputs[inputIdx].required && (newValues[stepIdx][inputIdx] === undefined || newValues[stepIdx][inputIdx] == '')) {
								// The update is unsuccessful when the mapping for a now-required input field is empty
								protocolUpdateSuccessful = false;
							}
						});
					});
					self.values = newValues;
				}
			} else {
				// When no versionMappings are specified, only the protocol name and/or products have changed; always succeed
				protocolUpdateSuccessful = true;
				self.params = params;
				self.values = values;
			}
		}

		if (protocolUpdateSuccessful) {
			self.protocol = manager.getProtocol(self.protocol.DBData._id, undefined, self.protocol.DBData);
		} else {
			self.params = params;
			self.values = values;
			self.products = products;
			self.possibleSourceSuppliesCache = possibleSourceSuppliesCacheBackup;
			self.possibleSourceExperimentsCache = possibleSourceExperimentsCacheBackup;
		}
	}

	self.performer = ko.observable(self.data && self.data.performer);
	self.finishDate = ko.observable(self.data ? self.data.finishDate : new Date());
	self.notes = ko.observable(self.data && self.data.notes);

	self.href = ko.computed(function () {
		return Router.path('viewExperiment', { id: self._id() });
	});
};

Experiment.prototype.addMultiParam = function (param) {
	var self = this;
	return function () {
		self.params()[param.name()].push(new ExperimentParamMultiSource(self));
	};
};

Experiment.prototype.removeMultiParam = function (param) {
	var self = this;
	return function (multiSource) {
		self.params()[param.name()].remove(multiSource);
	};
};

Experiment.prototype.getExperimentParamSource = function (param, data, tryUpdate) {
	var self = this;

	var paramSource;
	switch (data.type) {
		case 'supply':
			paramSource = _.find(self.possibleSourceSupplies(param), function (psource) {
				return psource.supply._id() == data.supply && (tryUpdate || psource.supply.version == data.v);
			});

			if (paramSource === undefined || (!tryUpdate && paramSource.supply.version != data.v)) {
				var currentVersionText = paramSource && paramSource.text();
				var currentVersionHref = paramSource && paramSource.getHref();

				paramSource = new ExperimentParamSourceSupply(self.manager.getSupply(data.supply, data.v));

				paramSource.currentVersionText = currentVersionText && (currentVersionText != paramSource.text ? 'now identified as ' + currentVersionText : 'updated');
				paramSource.currentVersionHref = currentVersionHref;
			}

			break;
		case 'experiment':
			paramSource =_.find(self.possibleSourceExperiments(param), function (psource) {
				return psource.experiment._id() == data.experiment && psource.product.name() == data.product && (tryUpdate || psource.experiment.version == data.v);
			});

			if (paramSource === undefined || (!tryUpdate && paramSource.experiment.version != data.v)) {
				var currentVersionText = paramSource && paramSource.text();
				var currentVersionHref = paramSource && paramSource.getHref();

				var obj = self.manager.getExperiment(data.experiment, data.v);
				var sourceProduct = _.find(obj.protocol.products(), function (pproduct) {
					return pproduct.name() == data.product;
				});
				paramSource = new ExperimentParamSourceExperiment(obj, sourceProduct);

				paramSource.currentVersionText = currentVersionText && (currentVersionText != paramSource.text ? 'now identified as ' + currentVersionText : 'updated');
				paramSource.currentVersionHref = currentVersionHref;
			}
			break;
	}

	return ko.observable(paramSource);
};

Experiment.prototype.possibleSourceSupplies = function (param) {
	var self = this;
	if (!self.possibleSourceSuppliesCache[param.name()]) {
		self.possibleSourceSuppliesCache[param.name()] = _.map(Supplies.find({ 'allTypes._id': param.type()._id() }, { sort: { date: -1 } }).fetch(), function (supply) {
			return new ExperimentParamSourceSupply(self.manager.getSupply(supply._id, undefined, supply));
		});
	}
	return self.possibleSourceSuppliesCache[param.name()];
};

Experiment.prototype.possibleSourceExperiments = function (param) {
	var self = this;
	if (!self.possibleSourceExperimentsCache[param.name()]) {
		var protocols = _.map(Protocols.find({ 'products.allTypes._id': param.type()._id() }).fetch(), function (protocol) {
			return self.manager.getProtocol(protocol._id, undefined, protocol);
		});
		var pproducts = { };
		_.each(protocols, function (sourceProtocol) {
			pproducts[sourceProtocol._id()] = { name: sourceProtocol.name, products: [] };
			_.each(sourceProtocol.products(), function (product) {
				if (_.contains(ko.toJS(_.pluck(product.allTypes(), '_id')), param.type()._id())) {
					pproducts[sourceProtocol._id()].products.push(product);
				}
			});
		});

		var experiments = Experiments.find({ _id: { $ne: self._id() }, 'protocol._id': { $in: _.keys(pproducts) } }, { sort: { finishDate: -1 } }).fetch();
		self.possibleSourceExperimentsCache[param.name()] = _.flatten(_.map(experiments, function (sourceExperiment) {
			return _.map(pproducts[sourceExperiment.protocol._id].products, function (product) {
				return new ExperimentParamSourceExperiment(self.manager.getExperiment(sourceExperiment._id, undefined, sourceExperiment), product);
			});
		}));
	}
	return self.possibleSourceExperimentsCache[param.name()];
};

Experiment.prototype.possibleSources = function (param) {
	var merged = [];
	var supplies = this.possibleSourceSupplies(param);
	var experiments = this.possibleSourceExperiments(param);
	while (supplies.length && experiments.length) {
		if (supplies[0].sortKey > experiments[0].sortKey) {
			merged.push(supplies.shift());
		} else {
			merged.push(experiments.shift());
		}
	}
	Array.prototype.push.apply(merged, supplies);
	Array.prototype.push.apply(merged, experiments);
	return merged;
};

Experiment.prototype.productText = function (product) {
	var texts = [];
	_.each(this.products[CryptoJS.MD5(product.name()).toString()], function (productType) {
		if (productType.text && productType.text()) texts.push(productType.text());
	});
	return texts.join('/');
};

Experiment.prototype.flatten = function () {
	var self = this;

	var params = { };
	var sourceSupplies = [];
	var sourceExperiments = [];
	_.each(self.params(), function (paramValue, paramName) {
		var paramNameHash = CryptoJS.MD5(paramName).toString();
		if (paramValue().length != undefined) {
			params[paramNameHash] = _.map(paramValue(), function (multiSource) {
				multiSource.paramValue().pushId(sourceSupplies, sourceExperiments);
				return multiSource.flatten();
			});
		} else {
			params[paramNameHash] = paramValue().flatten();
			paramValue().pushId(sourceSupplies, sourceExperiments);
		}
	});

	var products = { };
	_.each(self.protocol.products(), function (product) {
		var productNameHash = CryptoJS.MD5(product.name()).toString()
		products[productNameHash] = { };

		_.each(product.types(), function (type) {
			_.each(type.allProperties(), function (property) {
				var propertyNameHash = CryptoJS.MD5(property.name()).toString();
				if (!products[productNameHash][property.from._id()]) products[productNameHash][property.from._id()] = { properties: { } };

				var binding = _.find(product.propertyBindings(), function (pbinding) {
					return pbinding.property.from._id() == property.from._id() && pbinding.property.name() == property.name();
				});
				products[productNameHash][property.from._id()].properties[propertyNameHash] = ko.unwrap(binding.source().getValue(self.values, self.params));
			});

			var text = '';
			_.each(type.text(), function (part) {
				switch (part.type) {
					case 'text':
						text = text + part.text;
						break;
					case 'propertyReference':
						var value = products[productNameHash][ko.unwrap((part.property.from || type)._id)].properties[CryptoJS.MD5(part.property.name).toString()];
						if (value) text = text + value;
						break;
				}
			});

			if (text) {
				if (!products[productNameHash][type._id()]) products[productNameHash][type._id()] = { };
				products[productNameHash][type._id()].text = text;
			}
		});
	});

	return {
		protocol: self.protocol.toReference(),
		values: ko.mapping.toJS(self.values),
		params: params,
		finishDate: self.finishDate(),
		notes: self.notes(),
		performer: self.performer(),
		products: products,
		sourceSupplies: sourceSupplies,
		sourceExperiments: sourceExperiments,
	};
};

ExperimentParamSourceSupply = function (supply) {
	this.supply = supply;
	this.editMode = ko.observable(false);
	this.currentVersionHref = null;
	this.sortKey = supply.date();
	this.text = this.getText(supply);
	this.href = this.getHref();
};

ExperimentParamSourceSupply.prototype.getText = function (version) {
	var texts = [];
	_.each(ko.unwrap(version.DBData.v[version.version].types), function (supplyType) {
		if (ko.unwrap(supplyType.text)) texts.push(ko.unwrap(supplyType.text));
	});
	return texts.join('/');
};

ExperimentParamSourceSupply.prototype.getHref = function (query) {
	return Router.path('viewSupply', { id: ko.unwrap(this.supply._id) }, { query: query });
};

ExperimentParamSourceSupply.prototype.getTypes = function() {
	return this.supply.types();
};

ExperimentParamSourceSupply.prototype.getProperty = function (paramProperty) {
	return _.find(this.supply.properties(), function (pproperty) {
		return pproperty.property.from._id() == paramProperty.from._id() && pproperty.property.name() == paramProperty.name();
	}).value;
};

ExperimentParamSourceSupply.prototype.pushId = function (supplyIds, experimentIds) {
	supplyIds.push(this.supply._id());
};

ExperimentParamSourceSupply.prototype.edit = function () {
	this.editMode(true);
};

ExperimentParamSourceSupply.prototype.flatten = function () {
	return {
		type: 'supply',
		supply: this.supply._id(),
		v: this.supply.version,
	};
};

ExperimentParamSourceExperiment = function (experiment, product) {
	this.experiment = experiment;
	this.product = product;
	this.editMode = ko.observable(false);
	this.currentVersionHref = null;
	this.sortKey = experiment.finishDate();
	this.text = this.getText(experiment);
	this.href = this.getHref();
};

ExperimentParamSourceExperiment.prototype.getText = function (version) {
	var productNameHash = CryptoJS.MD5(this.product.name()).toString();
	var texts = [];
	_.each(this.product.types(), function (productType) {
		var text = version.products[productNameHash][productType._id()] && version.products[productNameHash][productType._id()].text();
		if (text) texts.push(text);
	});
	return texts.join('/');
};

ExperimentParamSourceExperiment.prototype.getHref = function (query) {
	return Router.path('viewExperiment', { id: ko.unwrap(this.experiment._id) }, { query: query });
};

ExperimentParamSourceExperiment.prototype.getTypes = function() {
	return this.product.types();
};

ExperimentParamSourceExperiment.prototype.getProperty = function (paramProperty) {
	return ko.unwrap(this.experiment.products[CryptoJS.MD5(this.product.name()).toString()][paramProperty.from._id()].properties[CryptoJS.MD5(paramProperty.name()).toString()]);
};

ExperimentParamSourceExperiment.prototype.pushId = function (supplyIds, experimentIds) {
	experimentIds.push(this.experiment._id());
};

ExperimentParamSourceExperiment.prototype.edit = function () {
	this.editMode(true);
};

ExperimentParamSourceExperiment.prototype.flatten = function () {
	return {
		type: 'experiment',
		experiment: this.experiment._id(),
		v: this.experiment.version,
		product: this.product.name(),
	};
};

ExperimentParamSourceNull = function () {
	this.text = '';
	this.href = '';
	this.currentVersionHref = '';
};

ExperimentParamSourceNull.prototype.editMode = function () {
	return true;
};

ExperimentParamSourceNull.prototype.pushId = function (supplyIds, experimentIds) { };

ExperimentParamSourceNull.prototype.flatten = function () {
	return null;
};

ExperimentParamMultiSource = function (experiment, param, paramSource, tryUpdate) {
	this.paramValue = param ? experiment.getExperimentParamSource(param, paramSource.paramValue, tryUpdate) : ko.observable(new ExperimentParamSourceNull());
	this.values = param ? ko.mapping.fromJS(paramSource.values) : { };
}

ExperimentParamMultiSource.prototype.input = function (step, input) {
	if (!this.values[step]) this.values[step] = { };
	if (!this.values[step][input]) this.values[step][input] = ko.observable();
	return this.values[step][input];
};

ExperimentParamMultiSource.prototype.flatten = function () {
	return {
		paramValue: this.paramValue().flatten(),
		values: ko.mapping.toJS(this.values),
	};
};

updateExperiment = function (id, newVersion) {
	Experiments.update(id, { $push: { v: newVersion }, $set: newVersion });
	return {
		experiments: function () { return Experiments.find({ sourceExperiments: id }).fetch(); },
	};
};

Meteor.methods({
	insertExperiment: function (flat) {
		if (!this.userId) throw 403;

		flat.editor = this.userId;
		flat.mtime = new Date();
		return Experiments.insert(_.extend({
			v: [flat]
		}, flat));
	},
	updateExperiment: function (id, newVersion) {
		if (!this.userId) throw 403;

		var manager = new OMManager();

		newVersion.editor = this.userId;
		newVersion.mtime = new Date();

		cascadingUpdate(manager, updateExperiment(id, newVersion), {
			type: 'cascade',
			dependency: {
				type: 'experiment',
				id: id,
			}
		});
	}
})
