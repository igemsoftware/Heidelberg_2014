Experiment = function (manager, data, version, tryUpdate) {
	var self = this;
	self.manager = manager;
	self.DBData = data && data.experiment;
	self._id = ko.observable(self.DBData && self.DBData._id);
	self.version = version === undefined ? self.DBData && self.DBData.v.length - 1 : version;
	self.oldVersion = self.DBData && self.version != self.DBData.v.length - 1;
	self.data = self.DBData && self.DBData.v[self.version];

	self.needsReview = self.DBData && self.DBData.needsReview;

	self.params = ko.observable({ });
	self.possibleSourceSuppliesCache = { };
	self.possibleSourceExperimentsCache = { };

	self.protocol = self.manager && self.manager.getProtocol(data && (self.data || data).protocol._id, self.data && self.data.protocol.v);

	self.values = { };

	if (self.data) {
		var protocolUpdateSuccessful = false; // only meaningful when tryUpdate == true
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

		if (tryUpdate && self.protocol.DBData.v.length - 2 == self.protocol.version) {
			// Assume success for now
			protocolUpdateSuccessful = true;
			if (self.protocol.versionMappings) {
				var newParams = { };
				_.each(self.protocol.versionMappings.params, function (paramMapping) {
					newParams[paramMapping.param] = params()[paramMapping.source];
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
					if (_.every(self.protocol.versionMappings.inputs, function (stepInputMappings, stepIdx) {
						_newValues[stepIdx] = { };
						return _.every(stepInputMappings, function (inputMapping, inputIdx) {
							if (values[inputMapping.step] && values[inputMapping.input] !== undefined) {
								newValues[stepIdx][inputIdx] = values[inputMapping.step][inputMapping.input];
							}
							if (self.protocol.steps[stepIdx].inputs[inputIdx].required && (newValues[stepIdx][inputIdx] === undefined || newValues[stepIdx][inputIdx] == '')) {
								// The update is unsuccessful when the mapping for a now-required input field is empty
								return protocolUpdateSuccessful = false;
							} else {
								return true;
							}
						});
					})) {
						self.values = newValues;
					}
				}
			} else {
				// When no versionMappings are specified, only the protocol name has changed; always succeed
				self.params = params;
				self.values = values;
			}
		} else {
			self.params = params;
			self.values = values;
		}

		if (protocolUpdateSuccessful) {
			self.protocol = manager.getProtocol(self.protocol.DBData._id, undefined, self.protocol.DBData);
		} else {
			self.params = params;
			self.values = values;
			self.possibleSourceSuppliesCache = possibleSourceSuppliesCacheBackup;
			self.possibleSourceExperimentsCache = possibleSourceExperimentsCacheBackup;
		}
	}

	var productsCache = { };
	self.products = ko.computed({
		read: function () {
			var products = { };
			_.each(self.protocol.products(), function (product) {
				var productNameHash = CryptoJS.MD5(product.name()).toString();
				if (!productsCache[product.name()]) productsCache[product.name()] = new ExperimentProduct(self, product, self.data && self.data.products[productNameHash], tryUpdate);
				products[product.name()] = productsCache[product.name()];
			});
			return products;
		},
		deferEvaluation: true,
	});

	self.performer = ko.observable(self.data && self.data.performer);
	self.finishDate = ko.observable(self.data ? self.data.finishDate : new Date());
	self.notes = ko.observable(self.data && self.data.notes);

	self.href = ko.computed(function () {
		return Router.path('viewExperiment', { id: self._id() });
	});
};

Experiment.prototype.addMultiParam = function (param) {
	this.params()[param.name()].push(new ExperimentParamMultiSource(this));
};

Experiment.prototype.removeMultiParam = function (param) {
	this.params()[param.name()].remove(multiSource);
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
			paramSource = _.find(self.possibleSourceExperiments(param), function (psource) {
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
		case 'text':
			paramSource = new ExperimentParamSourceText(data.text);
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
	var productTypes = [];
	_.each(self.products(), function (product) {
		var productNameHash = CryptoJS.MD5(product.product.name()).toString()
		products[productNameHash] = product.flatten();
		productTypes.push(product.type()._id());
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
		productTypes: productTypes,
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
	_.each(ko.unwrap(version.data.types), function (supplyType) { // TODO
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

ExperimentParamSourceSupply.prototype.hasProperties = true;

ExperimentParamSourceSupply.prototype.getProperty = function (paramProperty) {
	return _.find(this.supply.properties(), function (pproperty) {
		return pproperty.property.from._id() == paramProperty.from._id() && pproperty.property.name() == paramProperty.name();
	}).value();
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
	var self = this;
	var texts = [];
	return version.products()[self.product.name()].text();
};

ExperimentParamSourceExperiment.prototype.getHref = function (query) {
	return Router.path('viewExperiment', { id: ko.unwrap(this.experiment._id) }, { query: query });
};

ExperimentParamSourceExperiment.prototype.getTypes = function() {
	return this.product.types();
};

ExperimentParamSourceExperiment.prototype.hasProperties = true;

ExperimentParamSourceExperiment.prototype.getProperty = function (paramProperty) {
	return this.experiment.products()[this.product.name()].getProperty(paramProperty).value();
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

ExperimentParamSourceText = function (text) {
	this.text = ko.observable(text || '');
	this.href = '';
	this.currentVersionHref = '';
};

ExperimentParamSourceText.prototype.editMode = function () {
	return true;
};

ExperimentParamSourceText.prototype.pushId = function (supplyIds, experimentIds) { };

ExperimentParamSourceText.prototype.hasProperties = false;

ExperimentParamSourceText.prototype.flatten = function () {
	return {
		type: 'text',
		text: this.text(),
	};
};

ExperimentParamMultiSource = function (experiment, param, paramSource, tryUpdate) {
	this.paramValue = param ? experiment.getExperimentParamSource(param, paramSource.paramValue, tryUpdate) : ko.observable(new ExperimentParamSourceText());
	this.values = param ? ko.mapping.fromJS(paramSource.values) : { };
};

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

ExperimentProduct = function (experiment, product, data, tryUpdate) {
	var self = this;
	self.experiment = experiment;
	self.product = product;
	self.data = data;

	var type;
	var typeMappings;
	if (data) {
		type = experiment.manager.getType(data.type._id, data.type.v);

		if (tryUpdate && type.oldVersion && type.DBData.versionMappings) {
			typeMappings = { };

			_.each(type.DBData.versionMappings, function (mapping) {
				if (!typeMappings[mapping.property.from._id]) typeMappings[mapping.property.from._id] = { };
				typeMappings[mapping.property.from._id][mapping.property.name] = mapping.source;
			});

			type = experiment.manager.getType(data.type._id, undefined, type.DBData);
		}
	}
	self.type = ko.observable(type || product.types()[0]);

	var propertiesCache = { };
	self.properties = ko.computed({
		read: function () {
			var properties = [];
			self.propertiesMap = { };
			_.each(self.type().allProperties(), function (property) {
				var fromId = property.from._id();
				var propertyName = property.name();
				var propertyMD5Name = CryptoJS.MD5(propertyName).toString();

				if (!propertiesCache[fromId]) propertiesCache[fromId] = { };
				if (!propertiesCache[fromId][propertyName]) {
					var propertyData;
					if (data) {
						if (typeMappings) {
							var mapping = typeMappings[fromId] && typeMappings[fromId][propertyName];
							if (mapping) {
								propertyData = data.properties[mapping.from._id] && data.properties[mapping.from._id][CryptoJS.MD5(mapping.name).toString()];
							} else if (property.required()) {
								// TODO: fail
							}
						} else if (data.properties[fromId]) {
							propertyData = data.properties[fromId][propertyMD5Name]
						}
					}
					propertiesCache[fromId][propertyName] = new ExperimentProductProperty(experiment, property, product.findPropertyBinding(property, self.type()), propertyData);
				}

				if (!self.propertiesMap[fromId]) self.propertiesMap[fromId] = { };
				if (!self.propertiesMap[fromId][propertyName]) {
					properties.push(self.propertiesMap[fromId][propertyName] = propertiesCache[fromId][propertyName]);
				}
			});
			return properties;
		},
		deferEvaluation: true,
	});

	self.text = ko.computed({
		read: function () {
			self.properties(); // ensure self.propertiesMap is populated
			return self.type().getText(self.propertiesMap);
		},
		deferEvaluation: true,
	});
};

ExperimentProduct.prototype.possibleTypes = function () {
	var self = this;
	var types = [self.product.types()[0]];
	Types.find({ 'allBaseTypes._id': self.product.types()[0]._id() }, { sort: { name: 1 } }).forEach(function (type) {
		types.push(self.experiment.manager.getType(type._id, undefined, type));
	});
	return types;
};

ExperimentProduct.prototype.getProperty = function (property) {
	this.properties(); // ensure this.propertiesMap is populated
	return this.propertiesMap[property.from._id()][property.name()];
};

ExperimentProduct.prototype.flatten = function () {
	var self = this;
	var properties = { };

	_.each(self.properties(), function (property) {
		if (!properties[property.property.from._id()]) properties[property.property.from._id()] = { };
		properties[property.property.from._id()][CryptoJS.MD5(property.property.name()).toString()] = property.flatten();
	});

	var allTypes = _.invoke(self.type().allBaseTypes(), 'toReference');
	allTypes.push(self.type().toReference());

	return {
		text: self.text(),
		properties: properties,
		type: self.type().toReference(),
		allTypes: allTypes,
	};
};

ExperimentProductProperty = function (experiment, property, binding, value) {
	var self = this;
	self.experiment = experiment;
	self.property = property;
	self.binding = binding;

	self.manualValue = ko.observable(value);
	self.value = ko.computed({
		read: function () {
			return self.isComputed() ? self.binding.source().getValue(self.experiment) : self.manualValue();
		},
		deferEvaluation: true,
	});
};

ExperimentProductProperty.prototype.isComputed = function () {
	return this.binding && ko.unwrap(this.binding.source().providesValue(this.experiment));
};

ExperimentProductProperty.prototype.flatten = function () {
	return this.value();
};

updateExperiment = function (id, newVersion) {
	Experiments.update(id, { $push: { v: newVersion }, $set: newVersion, $unset: { needsReview: true }  });
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
			v: [flat],
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
			},
		});
	}
})
