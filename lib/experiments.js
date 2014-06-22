experimentsVM = function (dataContainer) {
	var self = this;
	self.editMode = dataContainer.editMode;
	self.newMode = dataContainer.newMode;
	var data = dataContainer.data();
	self.performer = ko.observable(data.experiment && data.experiment.v[data.experiment.v.length - 1].performer);
	self.protocol = data.protocol;
	self.experiments = ko.observableArray([ new experimentVM(data) ]);
	self.colspan = ko.computed(function () {
		return self.experiments().length + 1;
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
		experiment.save(self.performer());
	});

	self.editMode(false);
	self.newMode(false);

	if (Meteor.isClient) {
		if (this.experiments().length == 1) {
			Router.go('viewExperiment', { id: this.experiments()[0].id });
		} else {
			Router.go('experimentList');
		}
	}
};

experimentsVM.prototype.cancel = function () {
	if (this.newMode()) {
		Router.go('viewProtocol', { id: this.protocol._id });
	} else {
		Router.go('viewExperiment', { id: this.experiments()[0].id });
	}
};

experimentVM = function (data) {
	var self = this;
	self.id = data.experiment && data.experiment._id;
	self.data = data.experiment;
	self.protocol = data.protocol;
	self.params = { };
	self.possibleSourcesCache = { };

	var version = data.experiment && data.experiment.v[data.experiment.v.length - 1];

	if (data.experiment) _.each(data.protocol.params, function (param) {
		var sourceParam = version.params[CryptoJS.MD5(param.name).toString()]
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

	self.values = data.experiment ? ko.mapping.fromJS(version.values) : { };

	self.finishDate = ko.observable(data.experiment ? version.finishDate : new Date());
	self.finishDateUpdate = !data.experiment && setInterval(function () {
		self.finishDate(new Date());
	}, 1000);

	self.notes = ko.observable(data.experiment && version.notes);
};

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
			var supplies = _.map(ss(), function (supply) {
				var origin = 'obtained on ' + supply.date();

				var texts = [];
				_.each(supply.types(), function (supplyType) {
					if (supplyType.text()) texts.push(supplyType.text());
				});

				return {
					type: 'supply',
					supply: supply,
					href: Meteor.isClient && Router.path('viewSupply', { id: supply._id() }),
					text: texts.length ? texts.join('/') + ' (' + origin + ')' : origin,
					sortKey: supply.date() 
				};
			});

			var xs = ko_meteor_find(Experiments, { _id: { $ne: self.id }, 'protocol._id': { $in: _.keys(pproducts) } }, { sort: { finishDate: -1 } });
			var experiments = _.flatten(_.map(xs(), function (sourceExperiment) {
				var sourceVersion = sourceExperiment.v()[sourceExperiment.v().length - 1];
				return _.map(pproducts[sourceExperiment.protocol._id()].products, function (product, pid) {
					var productNameHash = CryptoJS.MD5(product.name()).toString();
					var origin = product.name() + ' from ' + sourceExperiment.protocol.name() + ' performed on ' + sourceVersion.finishDate();

					var texts = [];
					_.each(product.types(), function (productType) {
						var text = sourceVersion.products[productNameHash][productType._id()] && ko.utils.unwrapObservable(sourceVersion.products[productNameHash][productType._id()].text);
						if (text) texts.push(text);
					});

					return {
						type: 'experiment',
						experiment: sourceExperiment,
						product: product,
						href: Meteor.isClient && Router.path('viewExperiment', { id: sourceExperiment._id() }),
						text: texts.length ? texts.join('/') + ' (' + origin + ')' : origin,
						sortKey: sourceVersion.finishDate()
					};
				});
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

experimentVM.prototype.flatten = function (performer, changeType) {
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
						supply: paramValue().supply._id(),
						v: paramValue().supply.v().length - 1
					};
					break;
				case 'experiment':
					params[paramNameHash] = {
						type: 'experiment',
						experiment: paramValue().experiment._id(),
						product: paramValue().product.name(),
						v: paramValue().experiment.v().length - 1
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
								products[productNameHash][propertyTypeId].properties[propertyNameHash] = ko.utils.unwrapObservable(param().supply.properties[(binding.source.paramProperty.from || paramDef.type)._id][CryptoJS.MD5(binding.source.paramProperty.name).toString()].value);
								break;
							case 'experiment':
								var sourceExperiment = param().experiment;
								var sourceVersion = sourceExperiment.v()[sourceExperiment.v().length - 1];
								products[productNameHash][propertyTypeId].properties[propertyNameHash] = ko.utils.unwrapObservable(sourceVersion.products[CryptoJS.MD5(param().product.name()).toString()][(binding.source.paramProperty.from || paramDef.type)._id].properties[CryptoJS.MD5(binding.source.paramProperty.name).toString()]);
								break;
						};
						break;
				}
			});

			var text = '';
			_.each(type.text, function (part) {
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
		values: ko.mapping.toJS(self.values),
		params: params,
		finishDate: self.finishDate(),
		notes: self.notes(),
		performer: performer,
		products: products,
		mtime: new Date(),
		changeType: changeType
	};
};

experimentVM.prototype.save = function (performer, changeType) {
	clearInterval(this.finishDateUpdate);
	var flat = this.flatten(performer, changeType);
	if (!this.id) {
		this.id = Experiments.insert(_.extend({
			protocol: _.pick(this.protocol, '_id', 'name'),
			v: [flat],
			finishDate: flat.finishDate
		}, flat));
		return 0;
	} else {
		Meteor.call('updateExperiment', this.id, flat, changeType);
		return this.data.v.length;
	}
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
					supply: this.paramValue().supply._id(),
					v: this.paramValue().supply.v.length - 1
				},
				values: ko.mapping.toJS(this.values)
			};
		case 'experiment':
			return {
				paramValue: {
					type: 'experiment',
					experiment: this.paramValue().experiment._id(),
					product: this.paramValue().product.name(),
					v: this.paramValue().experiment.v.length - 1
				},
				values: ko.mapping.toJS(this.values)
			};
	}
};

Meteor.methods({
	updateExperiment: function (id, newVersion, originalChangeType) {
		sourceExperiments = [];
		sourceSupplies = [];
		_.each(newVersion.params, function (param) {
			if (param.push) {
				_.each(param, function (param) {
					switch (param.paramValue.type) {
						case 'supply':
							sourceSupplies.push(param.paramValue.supply);
							break;
						case 'experiment':
							sourceExperiments.push(param.paramValue.experiment);
							break;
					}
				})
			} else {
				if (param.type == 'experiment') sourceExperiments.push(param.experiment);
			}
		});

		Experiments.update(id, { $push: { v: newVersion }, $set: _.extend({ sourceExperiments: sourceExperiments }, newVersion) }, function (error) {
			Experiments.find({ sourceExperiments: id }).forEach(function (dependentExperiment) {
				var protocol = Protocols.findOne(dependentExperiment.protocol._id);
				var vm = new experimentVM({ experiment: dependentExperiment, protocol: protocol });
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
