Protocol = function (data, version, tryUpdate) {
	var self = this;
	self._id = ko.observable(data && data._id);
	self.version = version === undefined ? data && data.v.length - 1 : version;
	self.oldVersion = data && self.version != data.v.length - 1;
	self.DBData = data;
	self.data = data && data.v[self.version];

	self.needsReview = ko.observable(data && data.needsReview);

	self.autoUpdateFailed = false; // only meaningful if tryUpdate == true

	self.name = ko.observable(self.data && self.data.name);
	self.params = ko.observableArray(self.data ? _.map(self.data.params, function (param) {
		return new ProtocolParam(param);
	}) : []);
	self.steps = ko.observableArray(self.data ? _.map(self.data.steps, function (step) {
		return new ProtocolStep(self, step);
	}) : []);
	self.products = ko.observableArray(self.data ? _.map(self.data.products, function (product) {
		return new ProtocolProduct(self, product, tryUpdate);
	}) : []);
};

Protocol.prototype.addParam = function () {
	this.params.push(new ProtocolParam());
};

Protocol.prototype.removeParam = function (param) {
	this.params.remove(param);
};

Protocol.prototype.addStep = function () {
	this.steps.push(new ProtocolStep(this));
};

Protocol.prototype.removeStep = function (step) {
	this.steps.remove(step);
};

Protocol.prototype.addProduct = function () {
	this.products.push(new ProtocolProduct(this));
};

Protocol.prototype.removeProduct = function (product) {
	this.products.remove(product);
};

Protocol.prototype.flatten = function () {
	var flat = {
		name: this.name(),
		params: _.map(this.params(), function (param) {
			return param.flatten();
		}),
		steps: _.map(this.steps(), function (step) {
			return step.flatten();
		}),
		products: _.map(this.products(), function (product) {
			return product.flatten();
		}),
	};

	if (this.autoUpdateFailed) throw flat; // TODO: Not very elegant ...
	return flat;
};

ProtocolParam = function (data) {
	var pTypeMap = { };
	this.types = _.map(Types.find().fetch(), function (type) {
		return pTypeMap[type._id] = new Type(type);
	});

	var self = this;
	self.type = ko.observable(data && new Type(Types.findOne(data.type._id)));
	self.name = ko.observable(data && data.name);
	self.multi = ko.observable(data ? data.multi : false);

	var handle;
	if (!data || data.name == data.type.name) {
		handle = self.type.subscribe(function (newValue) {
			self.name(newValue.name());
		});
	}
};

ProtocolParam.prototype.nameChanged = function () {
	if (this.handle) {
		this.handle.dispose();
		delete this.handle;
	}
};

ProtocolParam.prototype.flatten = function () {
	return {
		type: this.type().toReference(),
		name: this.name(),
		multi: this.multi(),
	};
};

ProtocolStep = function (protocol, data) {
	var self = this;
	self.protocol = protocol;
	self.desc = ko.observable(data && data.desc);
	self.inputs = ko.observableArray(data ? _.map(data.inputs, function (input) {
		return new ProtocolStepInput(protocol, input);
	}) : []);
}

ProtocolStep.prototype.addInput = function () {
	this.inputs.push(new ProtocolStepInput(this.protocol));
};

ProtocolStep.prototype.removeInput = function (input) {
	this.inputs.remove(input);
};

ProtocolStep.prototype.flatten = function () {
	return {
		desc: this.desc(),
		inputs: _.map(this.inputs(), function (input) {
			return input.flatten();
		}),
	};
};

ProtocolStepInput = function (protocol, data) {
	this.desc = ko.observable(data && data.desc);
	this.type = ko.observable(data && PODType.typeMap[data.type]);
	this.required = ko.observable(data ? data.required : true);
	this.multi = ko.observable(data ? !!data.multiParam : false);
	this.multiParam = ko.observable(data && _.find(protocol.params(), function (param) {
		return param.name() == data.multiParam;
	}));
}

ProtocolStepInput.prototype.types = PODType.types;

ProtocolStepInput.prototype.flatten = function () {
	return {
		desc: this.desc(),
		type: this.type().id,
		required: this.required(),
		multiParam: this.multi() ? this.multiParam().name() : null
	};
};

ProtocolProduct = function (protocol, data, tryUpdate) {
	var pTypeMap = { };
	this.possibleTypes = _.map(Types.find().fetch(), function (type) {
		return pTypeMap[type._id] = new Type(type);
	}); // TODO

	var self = this;
	self.name = ko.observable(data && data.name);

	var typeMappings = { };
	self.types = ko.observableArray(data ? _.map(data.types, function (type) {
		var obj = pTypeMap[type._id];
		if (!tryUpdate && type.v != obj.version) obj = new Type(Types.findOne(type._id), type.v);
		if (tryUpdate && type.v != obj.version && obj.DBData.versionMappings) {
			_.each(obj.DBData.versionMappings, function (mapping) {
				if (!typeMappings[mapping.property.from._id]) typeMappings[mapping.property.from._id] = { };
				typeMappings[mapping.property.from._id][mapping.property.name] = mapping.source;
			});
		}
		return obj;
	}) : []);

	self.allTypes = ko.computed(function () {
		var allTypes = { };

		_.each(self.types(), function (type) {
			allTypes[type._id()] = type;
			_.each(type.baseTypes(), function (baseType) {
				allTypes[baseType._id()] = baseType;
			});
		});

		return _.values(allTypes);
	});

	var propertyBindingsMap = { };
	self.propertyBindings = ko.computed(function () {
		var propertyBindings = [];
		var map = { };

		_.each(self.types(), function (type) {
			var usedTypes = { };

			_.each(type.allProperties(), function (property) {
				var fromId = property.from._id();
				if (!map[fromId]) {
					if (!propertyBindingsMap[fromId]) propertyBindingsMap[fromId] = { };
					if (!propertyBindingsMap[fromId][property.name()]) {
						var ppp = new ProtocolProductProperty(protocol, property, undefined);
						propertyBindingsMap[fromId][property.name()] = ppp;

						if (data) {
							var md5Name = CryptoJS.MD5(property.name()).toString();
							var mapping = tryUpdate && typeMappings[fromId] && typeMappings[fromId][md5Name];
							if (mapping) {
								fromId = (ko.unwrap(mapping.source.from) || mapping.property.from)._id();
								md5Name = CryptoJS.MD5(mapping.source.name()).toString();
							}

							var source;
							if (data.propertyBindings[fromId] && data.propertyBindings[fromId][md5Name]) {
								var binding = data.propertyBindings[fromId][md5Name];
								switch (binding.source.type) {
									case 'paramProperty':
										var sourceTypeId = ko.unwrap((binding.source.paramProperty.from || type)._id);
										var sourceMapping = typeMappings[sourceTypeId]
											&& typeMappings[sourceTypeId][CryptoJS.MD5(binding.source.paramProperty.name).toString()];
										var sourceFromId = sourceMapping ? sourceMapping.from._id : sourceTypeId;
										var sourceName = (sourceMapping || binding.source.paramProperty).name;
										source =_.find(ppp.possibleSourceParamProperties(), function (psource) {
											return psource.param.name() == binding.source.param && psource.paramProperty.from._id() == sourceFromId && psource.paramProperty.name() == sourceName;
										});
										break;
									case 'input':
										source =_.find(ppp.possibleSourceInputs(), function (psource) {
											return psource.stepIndex == binding.source.input.step && psource.inputIndex == binding.source.input.input;
										});
										break;
								};

								if (source) {
									ppp.source(source);
								}
							}

							if (tryUpdate && !source && property.required()) {
								protocol.autoUpdateFailed = true;
							}
						}
					}

					if (!usedTypes[fromId]) usedTypes[fromId] = [];
					usedTypes[fromId].push(propertyBindingsMap[fromId][property.name()]);
				}
			});

			_.extend(map, usedTypes);
		});

		return _.flatten(_.values(map));
	});
};

ProtocolProduct.prototype.flatten = function () {
	var propertyBindings = this.propertyBindings();

	var propertyBindingsMap = { };
	_.each(propertyBindings, function (binding) {
		if (!propertyBindingsMap[binding.property.from._id()]) propertyBindingsMap[binding.property.from._id()] = { };
		propertyBindingsMap[binding.property.from._id()][CryptoJS.MD5(binding.property.name()).toString()] = binding.flatten();
	});

	return {
		name: this.name(),
		types: _.map(this.types(), function (type) {
			return type.toReference();
		}),
		allTypes: _.map(this.allTypes(), function (type) {
			return type.toReference();
		}),
		propertyBindings: propertyBindingsMap,
	};
};

ProtocolProductProperty = function (protocol, property, data) {
	var self = this;
	self.property = property,
	self.source = ko.observable(data),

	self.possibleSourceParamProperties = ko.computed(function () {
		var arr = [ ];

		_.each(protocol.params(), function (param) {
			if (!param.multi()) {
				_.each(param.type().allProperties(), function (paramProperty) {
					if (paramProperty.type() == property.type()) {
						arr.push(new ProtocolProductPropertyParamPropertySource(param, paramProperty));
					}
				});
			}
		});

		return arr;
	});

	self.possibleSourceInputs = ko.computed(function () {
		var arr = [ ];

		_.each(protocol.steps(), function (step, stepIndex) {
			_.each(step.inputs(), function (input, inputIndex) {
				if (input.type() == property.type() && !input.multi()) {
					arr.push(new ProtocolProductPropertyInputSource(step, stepIndex, input, inputIndex));
				}
			});
		});

		return arr;
	});

	self.possibleSources = ko.computed(function () {
		var arr = _.clone(self.possibleSourceParamProperties());
		arr.push.apply(arr, self.possibleSourceInputs());
		return arr;
	});
};

ProtocolProductProperty.prototype.flatten = function () {
	return {
		property: this.property.toReference(),
		source: this.source().flatten(),
	};
};

ProtocolProductPropertyParamPropertySource = function (param, paramProperty) {
	var self = this;
	self.param = param,
	self.paramProperty = paramProperty,

	self.text = ko.computed(function () {
		return 'Property ' + paramProperty.name() + ' of parameter ' + param.name();
	});
};

ProtocolProductPropertyParamPropertySource.prototype.flatten = function () {
	return {
		type: 'paramProperty',
		param: this.param.name(),
		paramProperty: this.paramProperty.toReference(),
	};
};

ProtocolProductPropertyInputSource = function (step, stepIndex, input, inputIndex) {
	var self = this;
	self.step = step;
	self.stepIndex = stepIndex;
	self.input = input;
	self.inputIndex = inputIndex;
	
	self.text = ko.computed(function () {
		return 'Input field ' + input.desc() + ' of step ' + (stepIndex + 1) + ' (' + step.desc() + ')';
	});
};

ProtocolProductPropertyInputSource.prototype.flatten = function () {
	return {
		type: 'input',
		input: {
			step: this.stepIndex,
			input: this.inputIndex,
		},
	}
};

Meteor.methods({
	insertProtocol: function (flat) {
		if (!this.userId) throw 403;

		flat.editor = this.userId;
		flat.mtime = new Date();

		return Protocols.insert(_.extend({
			v: [flat]
		}, flat));
	},
	updateProtocol: function (id, newVersion, oldVersionNo) {
		if (!this.userId) throw 403;

		newVersion.editor = this.userId;
		newVersion.mtime = new Date();

		Protocols.update(id, { $push: { v: newVersion }, $set: newVersion, $unset: { needsReview: true } }, function (error) {
			var protocol = Protocols.findOne(id);
			Experiments.find({ 'protocol._id': id, 'protocol.v': oldVersionNo }).forEach(function (dependentExperiment) {
				var vm = new experimentVM({ experiment: dependentExperiment, protocol: protocol }, undefined, true);
				vm.save(dependentExperiment.v[dependentExperiment.v.length - 1].performer, {
					type: 'cascade',
					dependency: {
						type: 'protocol'
					}
				});
			});
		});
	}
});
