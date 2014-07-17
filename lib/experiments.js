experimentVersionVM = function(id, version, index) {
	var self = this;
	self.id = id;
	self.versionNr = index;
	self.version = version;
	self.href = Router.path('viewExperiment', { id: self.id }, { query: { v: self.versionNr } });
}

experimentVersionVM.prototype.isCurrent = function(currentVersionNr) {
	return this.versionNr == currentVersionNr;
}

experimentVersionVM.prototype.hideModal = function() {
	$("#versionModal").modal('hide');
	return true; // Allow standard event handler for href
}

experimentsVM = function (dataContainer) {
	var self = this;
	self.editMode = dataContainer.editMode;
	self.newMode = dataContainer.newMode;
	var data = dataContainer.data();
	self.DBData = data.experiment;
	self.version = data.experiment && (typeof dataContainer.version() == 'undefined' ? data.experiment.v.length - 1 : dataContainer.version());
	self.oldVersion = data.experiment && typeof dataContainer.version() != 'undefined' && dataContainer.version() != data.experiment.v.length - 1;
	self.performer = ko.observable(data.experiment && data.experiment.v[self.version].performer);
	self.protocol = data.experiment ? data.protocol.v[data.experiment.v[self.version].protocol.v] : data.protocol;
	self.experiments = ko.observableArray([ new experimentVM(data, self.version) ]);
	self.versions = data.experiment && _.map(data.experiment.v, function(version, index){
		return new experimentVersionVM(data.experiment._id, version, index);
	}).reverse();
	self.colspan = ko.computed(function () {
		return self.experiments().length + 1;
	});

	if (Meteor.isClient) self.experiments.subscribe(function (newValue) {
		var $container = $('#container');
		if (newValue.length > 3) {
			$container.stop().animate({ width: '100%' });
		} else {
			var oldWidth = $container.stop().width();
			var naturalWidth = $container.css('width', '').outerWidth();
			$container.width(oldWidth).animate({ width: naturalWidth }, { complete: function () { $container.width(''); } });
		}
	});
};

experimentsVM.prototype.addExperiment = function () {
	this.experiments.push(new experimentVM({ protocol: this.protocol }));
};

experimentsVM.prototype.removeExperiment = function (experiment) {
	this.experiments.remove(experiment);
};

experimentsVM.prototype.edit = function () {
	Router.go('viewExperiment', { id: this.experiments()[0].id }, { query: { edit: 1 } });
};


experimentsVM.prototype.save = function () {
	var self = this;
	_.each(this.experiments(), function (experiment) {
		experiment.save(self.performer(), undefined, self.experiments().length == 1);
	});

	self.editMode(false);
	self.newMode(false);

	if (Meteor.isClient && self.experiments().length != 1) {
		Router.go('experimentList');
	}
};

experimentsVM.prototype.cancel = function () {
	if (this.newMode()) {
		Router.go('viewProtocol', { id: this.protocol._id });
	} else {
		Router.go('viewExperiment', { id: this.experiments()[0].id });
	}
};

experimentsVM.prototype.displayVersions = function() {
	$("#versionModal").modal();
}

experimentVM = function (data, version, tryUpdate) {
	var self = this;
	self.id = data.experiment && data.experiment._id;
	self.data = data.experiment;
	self.protocol = data.protocol;
	self.version = typeof version == 'undefined' ? data.experiment && data.experiment.v.length - 1 : version;
	self.params = { };
	self.possibleSourcesCache = { };

	var version = data.experiment && data.experiment.v[self.version];
	self.protocolVersion = version ? version.protocol.v : data.protocol.v.length - 1;

	self.values = { };

	if (data.experiment) {
		var protocolUpdateSuccessful = false;
		var possibleSourcesCacheBackup = self.possibleSourcesCache;

		var params = { };
		_.each(data.protocol.v[self.protocolVersion].params, function (param) {
			var sourceParam = version.params[CryptoJS.MD5(param.name).toString()]
			if (param.multi) {
				params[param.name] = ko.observableArray(_.map(sourceParam, function (multiParam) {
					var obj = new experimentMultiParamVM(multiParam);
					obj.paramValue = self.getParamObs(param, multiParam.paramValue, tryUpdate);
					return obj;
				}));
			} else {
				params[param.name] = self.getParamObs(param, sourceParam, tryUpdate);
			}
		});
		self.params = params;

		var values = data.experiment ? ko.mapping.fromJS(version.values) : { };
		self.values = values;

		if (tryUpdate && self.protocol.v.length - 2 == self.protocolVersion) {
			if (self.protocol.versionMappings) {
				// Assume success for now
				protocolUpdateSuccessful = true;

				var newParams = { };
				_.each(self.protocol.versionMappings.params, function (paramMapping) {
					newParams[paramMapping.param] = params[paramMapping.source];
					var param = _.find(self.protocol.params, function (pparam) {
						return pparam.name == paramMapping.param;
					});
					if (param.multi) {
						if (!_.every(newParams[paramMapping.param](), function (paramValue) {
							return _.find(self.possibleSources(param)(), function (psource) {
								return psource.type == paramValue.paramValue().type && psource.reference._id() == paramValue.paramValue().reference._id();
							});
						})) protocolUpdateSuccessful = false;
					} else {
						if (!_.find(self.possibleSources(param)(), function (psource) {
							return psource.type == newParams[paramMapping.param]().type && psource.reference._id() == newParams[paramMapping.param]().reference._id();
						})) protocolUpdateSuccessful = false;
					}
				});
				self.params = newParams;

				// If the parameter mappings have already been unsuccessful, don't bother with the values
				if (protocolUpdateSuccessful) {
					var newValues = { };
					_.each(self.protocol.versionMappings.inputs, function (stepInputMappings, stepIdx) {
						newValues[stepIdx] = { };
						_.each(stepInputMappings, function (inputMapping, inputIdx) {
							if (values[inputMapping.step] && values[inputMapping.step][inputMapping.input] !== undefined) {
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
			}
		}

		if (protocolUpdateSuccessful) {
			self.protocolVersion = self.protocol.v.length - 1;
		} else {
			self.params = params;
			self.values = values;
			self.possibleSourcesCache = possibleSourcesCacheBackup;
		}
	}

	self.finishDate = ko.observable(data.experiment ? version.finishDate : new Date());
	self.finishDateUpdate = !data.experiment && setInterval(function () {
		self.finishDate(new Date());
	}, 1000);

	self.notes = ko.observable(data.experiment && version.notes);
};

experimentVM.prototype.getParamObs = function (param, sourceParam, tryUpdate) {
	var paramObs = ko.observable(_.find(this.possibleSources(param)(), function (psource) {
		if (psource.type != sourceParam.type) return false;
		switch (psource.type) {
			case 'supply':
				return psource.reference._id() == sourceParam.supply;
			case 'experiment':
				return psource.reference._id() == sourceParam.experiment && psource.product() == sourceParam.product;
		}
	}));

	if (paramObs.peek() === undefined) {
		switch (sourceParam.type) {
			case 'supply':
				var supply = Supplies.findOne(sourceParam.supply);
				paramObs(makeSupplyPsource(supply));
				break;
			case 'experiment':
				var sourceExperiment = Experiments.findOne(sourceParam.experiment);
				var sourceVersion = sourceExperiment.v[sourceParam.v];
				var sourceProtocol = Protocols.findOne(sourceVersion.protocol._id);
				var sourceProduct = _.find(sourceProtocol.v[sourceVersion.protocol.v].products, function (pproduct) {
					return pproduct.name == sourceParam.product;
				});
				paramObs(makeMakeExperimentPsource([sourceProduct])(sourceExperiment)[0]);
				break;
		}

		paramObs.peek().edit = function () {
			paramObs.peek().editable(true);
		};
		paramObs.peek().editable(false);
	}

	if (!tryUpdate && ko.unwrap(paramObs.peek().reference.v).length - 1 != sourceParam.v) {
		paramObs(_.clone(paramObs.peek()));
		paramObs.peek().v = sourceParam.v;

		var currentVersionText = paramObs.peek().text;
		paramObs.peek().text = paramObs.peek().getText(ko.unwrap(paramObs.peek().reference.v)[sourceParam.v]);
		paramObs.peek().currentVersionText = currentVersionText != paramObs.peek().text ? 'now identified as ' + currentVersionText : 'updated';
		paramObs.peek().currentVersionHref = paramObs.peek().getHref();
	}

	if (Meteor.isClient) paramObs.peek().href = paramObs.peek().getHref({ v: sourceParam.v });

	return paramObs;
}

function getSupplyTexts(version) {
	var texts = [];
	_.each(ko.unwrap(version.types), function (supplyType) {
		if (ko.unwrap(supplyType.text)) texts.push(ko.unwrap(supplyType.text));
	});
	return texts;
};

function makeSupplyPsource(supply) {
	var obj = {
		type: 'supply',
		reference: supply,
		getText: function (version) {
			var origin = 'obtained from ' + ko.unwrap(version.source) + ' on ' + formatDate(ko.unwrap(version.date));
			var texts = getSupplyTexts(version);
			return texts.length ? texts.join('/') + ' (' + origin + ')' : origin;
		},
		getHref: function (query) {
			return Router.path('viewSupply', { id: ko.unwrap(supply._id) }, { query: query });
		},
		editable: ko.observable(true),
		v: supply.v && ko.unwrap(supply.v).length - 1,
		currentVersionHref: null,
		sortKey: ko.unwrap(supply.date)
	};
	obj.text = obj.getText(supply);
	if (Meteor.isClient) obj.href = obj.getHref();
	return obj;
}

function makeGetExperimentTexts(product) {
	var productNameHash = CryptoJS.MD5(ko.unwrap(product.name)).toString();
	return function (version) {
		var texts = [];
		_.each(ko.unwrap(product.types), function (productType) {
			var text = version.products[productNameHash][ko.unwrap(productType._id)] && ko.utils.unwrapObservable(version.products[productNameHash][ko.unwrap(productType._id)].text);
			if (text) texts.push(text);
		});
		return texts;
	};
}

function makeMakeExperimentPsource(products) {
	return function (sourceExperiment) {
		return _.map(products, function (product, pid) {
			var productNameHash = CryptoJS.MD5(ko.unwrap(product.name)).toString();

			var obj = {
				type: 'experiment',
				reference: sourceExperiment,
				product: product.name,
				getText: function (version) {
					var origin = ko.unwrap(product.name) + ' from ' + ko.unwrap(version.protocol.name) + ' performed on ' + ko.unwrap(version.finishDate);
					var texts = makeGetExperimentTexts(product)(version);
					return texts.length ? texts.join('/') + ' (' + origin + ')' : origin;
				},
				getHref: function (query) {
					return Router.path('viewExperiment', { id: ko.unwrap(sourceExperiment._id) }, { query: query });
				},
				editable: ko.observable(true),
				v: sourceExperiment.v && ko.unwrap(sourceExperiment.v).length - 1,
				currentVersionHref: null,
				sortKey: ko.unwrap(sourceExperiment.finishDate)
			};
			obj.text = obj.getText(sourceExperiment);
			if (Meteor.isClient) obj.href = obj.getHref();
			return obj;
		});
	};
}

experimentVM.prototype.possibleSources = function (param) {
	var self = this;
	if (!self.possibleSourcesCache[param.name]) {
		self.possibleSourcesCache[param.name] = ko.computed(function () {
			var ps = ko_meteor_find(Protocols, { 'products.allTypes._id': param.type._id });
			var pproducts = { };
			_.each(ps(), function (sourceProtocol) {
				pproducts[sourceProtocol._id()] = { name: sourceProtocol.name, products: [] };
				_.each(sourceProtocol.products(), function (product) {
					if (_.contains(ko.toJS(_.pluck(product.allTypes(), '_id')), param.type._id)) {
						pproducts[sourceProtocol._id()].products.push(product);
					}
				});
			});

			var ss = ko_meteor_find(Supplies, { 'allTypes._id': param.type._id }, { sort: { date: -1 } });
			var supplies = _.map(ss(), makeSupplyPsource);

			var xs = ko_meteor_find(Experiments, { _id: { $ne: self.id }, 'protocol._id': { $in: _.keys(pproducts) } }, { sort: { finishDate: -1 } });
			var experiments = _.flatten(_.map(xs(), function (sourceExperiment) {
				return makeMakeExperimentPsource(pproducts[sourceExperiment.protocol._id()].products)(sourceExperiment);
			}));

			var merged = [];
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
		});
	}
	return self.possibleSourcesCache[param.name];
};

experimentVM.prototype.getParam = function (param, array) {
	if (!this.params[param.name]) {
		this.params[param.name] = array ? ko.observableArray() : ko.observable({ editable: ko.observable(true) });
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

experimentVM.prototype.flatten = function (performer, changeType) {
	var self = this;

	var params = { };
	var sourceSupplies = [];
	var sourceExperiments = [];
	_.each(self.params, function (paramValue, paramName) {
		var paramNameHash = CryptoJS.MD5(paramName).toString();
		if (paramValue.push) {
			params[paramNameHash] = _.map(paramValue(), function (multiParamVM) {
				switch (multiParamVM.paramValue().type) {
					case 'supply':
						sourceSupplies.push(ko.unwrap(multiParamVM.paramValue().reference._id));
						break;
					case 'experiment':
						sourceExperiments.push(ko.unwrap(multiParamVM.paramValue().reference._id));
						break;
				}
				return multiParamVM.flatten();
			});
		} else {
			switch (paramValue().type) {
				case 'supply':
					params[paramNameHash] = {
						type: 'supply',
						supply: ko.unwrap(paramValue().reference._id),
						v: paramValue().editable() ? ko.unwrap(paramValue().reference.v).length - 1 : paramValue().v
					};
					sourceSupplies.push(ko.unwrap(paramValue().reference._id));
					break;
				case 'experiment':
					params[paramNameHash] = {
						type: 'experiment',
						experiment: ko.unwrap(paramValue().reference._id),
						product: ko.unwrap(paramValue().product),
						v: paramValue().editable() ? ko.unwrap(paramValue().reference.v).length - 1 : paramValue().v
					};
					sourceExperiments.push(ko.unwrap(paramValue().reference._id));
					break;
			}
			
		}
	});

	var products = { };
	_.each(self.protocol.v[self.protocolVersion].products, function (product) {
		var productNameHash = CryptoJS.MD5(product.name).toString()
		products[productNameHash] = { };
		_.each(product.types, function (typeRef) {
			type = Types.findOne(typeRef._id);
			_.each(type.v[typeRef.v].allProperties, function (property) {
				var propertyNameHash = CryptoJS.MD5(property.name).toString();
				var propertyTypeId = (property.from || type)._id;
				if (!products[productNameHash][propertyTypeId]) products[productNameHash][propertyTypeId] = { properties: { } };

				var binding = product.propertyBindings[propertyTypeId][propertyNameHash];
				switch (binding.source.type) {
					case 'input':
						products[productNameHash][propertyTypeId].properties[propertyNameHash] = ko.unwrap(self.values[binding.source.input.step][binding.source.input.input]);
						break;
					case 'paramProperty':
						var param = self.params[binding.source.param];
						var paramDef = _.find(self.protocol.v[self.protocolVersion].params, function (pparam) {
							return pparam.name == binding.source.param;
						});
						var sourceVersion = param().editable() ? param().reference : ko.unwrap(param().reference.v)[param().v];
						switch (param().type) {
							case 'supply': 
								products[productNameHash][propertyTypeId].properties[propertyNameHash] = ko.utils.unwrapObservable(sourceVersion.properties[(binding.source.paramProperty.from || paramDef.type)._id][CryptoJS.MD5(binding.source.paramProperty.name).toString()].value);
								break;
							case 'experiment':
								products[productNameHash][propertyTypeId].properties[propertyNameHash] = ko.utils.unwrapObservable(sourceVersion.products[CryptoJS.MD5(param().product()).toString()][(binding.source.paramProperty.from || paramDef.type)._id].properties[CryptoJS.MD5(binding.source.paramProperty.name).toString()]);
								break;
						};
						break;
				}
			});

			var text = '';
			_.each(type.v[typeRef.v].text, function (part) {
				switch (part.type) {
					case 'text':
						text = text + part.text;
						break;
					case 'propertyReference':
						var value = products[productNameHash][(part.property.from || type)._id].properties[CryptoJS.MD5(part.property.name).toString()];
						if (value) text = text + value;
						break;
				}
			});

			if (text) {
				if (!products[productNameHash][type._id]) products[productNameHash][type._id] = { };
				products[productNameHash][type._id].text = text;
			}
		});
	});

	return {
		protocol: {
			_id: self.protocol._id,
			name: self.protocol.v[self.protocolVersion].name,
			v: self.protocolVersion
		},
		values: ko.mapping.toJS(self.values),
		params: params,
		finishDate: self.finishDate(),
		notes: self.notes(),
		performer: performer,
		products: products,
		sourceSupplies: sourceSupplies,
		sourceExperiments: sourceExperiments,
		mtime: new Date(),
		changeType: changeType
	};
};

experimentVM.prototype.save = function (performer, changeType, redirect) {
	var self = this;
	clearInterval(this.finishDateUpdate);
	var flat = this.flatten(performer, changeType);
	if (!this.id) {
		Meteor.call('insertExperiment', flat, function (error, result) {
			if (!error) {
				self.id = result;
				if (redirect) Router.go('viewExperiment', { id: self.id });
			}
		});
	} else if (!isUnchanged(flat, this.data)) {
		Meteor.call('updateExperiment', this.id, flat, changeType);
		if (redirect) Router.go('viewExperiment', { id: self.id });
	}
}

function experimentMultiParamVM(multiParam) {
	var self = this;
	self.paramValue = ko.observable({ editable: ko.observable(true) });
	self.values = multiParam ? ko.mapping.fromJS(multiParam.values) : { };
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
					supply: this.paramValue().reference._id(),
					v: this.paramValue().editable() ? ko.unwrap(this.paramValue().reference.v).length - 1 : this.paramValue().v
				},
				values: ko.mapping.toJS(this.values)
			};
		case 'experiment':
			return {
				paramValue: {
					type: 'experiment',
					experiment: this.paramValue().reference._id(),
					product: this.paramValue().product(),
					v: this.paramValue().editable() ? ko.unwrap(this.paramValue().reference.v).length - 1 : this.paramValue().v
				},
				values: ko.mapping.toJS(this.values)
			};
	}
};

Meteor.methods({
	insertExperiment: function (flat) {
		if (!this.userId) return;
		flat.editor = this.userId;
		return Experiments.insert(_.extend({
			v: [flat]
		}, flat));
	},
	updateExperiment: function (id, newVersion, originalChangeType) {
		if (!this.userId) return;
		newVersion.editor = this.userId;
		Experiments.update(id, { $push: { v: newVersion }, $set: newVersion }, function (error) {
			Experiments.find({ sourceExperiments: id }).forEach(function (dependentExperiment) {
				var protocol = Protocols.findOne(dependentExperiment.protocol._id);
				var vm = new experimentVM({ experiment: dependentExperiment, protocol: protocol }, undefined, true);
				vm.save(dependentExperiment.v[dependentExperiment.v.length - 1].performer, {
					type: 'cascade',
					dependency: {
						type: 'experiment',
						id: id,
						changeType: originalChangeType
					}
				});
			});
		});
	}
})
