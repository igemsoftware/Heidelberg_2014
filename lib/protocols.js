protocolVersionVM = function(id, version, index) {
	var self = this;
	self.id = id;
	self.versionNr = index;
	self.version = version;
	self.href = Router.path('viewProtocol', { id: self.id }, { query: { v: self.versionNr } });
}

protocolVersionVM.prototype.isCurrent = function(currentVersionNr) {
	return this.versionNr == currentVersionNr;

}

protocolVersionVM.prototype.hideModal = function() {
	$("#versionsModal").modal('hide');
	return true; // Allow standard event handler for href
}

protocolVM = function (data) {
	var self = this;
	self.editMode = data.editMode;
	var protocol = data.protocol ? data.protocol() : data.protocol;
	self.id = protocol && protocol._id;
	self.data = protocol && protocol;
	self.version = self.data && (typeof data.version() == 'undefined' ? self.data.v.length - 1 : data.version());
	self.versions = self.data && _.map(self.data.v, function (version, index) {
		return new protocolVersionVM(self.id, version, index);
	}).reverse();
	self.oldVersion = self.data && self.data.v && typeof data.version() != 'undefined' && data.version() != self.data.v.length - 1;
	self.name = ko.observable(self.oldVersion ? protocol && protocol.v[self.version].name : protocol && protocol.name);
	if(self.oldVersion) {
		self.params = ko.observableArray(protocol ? _.map(protocol.v[self.version].params, function (param) {
			return new protocolParamVM(param);
		}) : []);
		self.steps = ko.observableArray(protocol ? _.map(protocol.v[self.version].steps, function (step) {
			return new protocolStepVM(self, step);
		}) : []);
		self.products = ko.observableArray(protocol ? _.map(protocol.v[self.version].products, function (product) {
			return new protocolProductVM(self, product);
		}) : []);
	}
	else {
		self.params = ko.observableArray(protocol ? _.map(protocol.params, function (param) {
			return new protocolParamVM(param);
		}) : []);
		self.steps = ko.observableArray(protocol ? _.map(protocol.steps, function (step) {
			return new protocolStepVM(self, step);
		}) : []);
		self.products = ko.observableArray(protocol ? _.map(protocol.products, function (product) {
			return new protocolProductVM(self, product);
		}) : []);

	}
	self.multiParams = ko.computed(function () {
		return _.filter(self.params(), function (param) {
			return param.multi();
		});
	});

	self.performHref = Router.path('performProtocol', { id: self.id });
};

protocolVM.prototype.addParam = function () {
	this.params.push(new protocolParamVM());
};

protocolVM.prototype.removeParam = function (param) {
	this.params.remove(param);
};

protocolVM.prototype.addStep = function () {
	this.steps.push(new protocolStepVM(this));
};

protocolVM.prototype.removeStep = function (step) {
	this.steps.remove(step);
};

protocolVM.prototype.addProduct = function () {
	this.products.push(new protocolProductVM(this));
};

protocolVM.prototype.removeProduct = function (product) {
	this.products.remove(product);
};

protocolVM.prototype.flatten = function () {
	return {
		name: this.name(),
		params: _.map(this.params(), function (param) {
			return param.flatten();
		}),
		steps: _.map(this.steps(), function (step) {
			return step.flatten();
		}),
		products: _.map(this.products(), function (product) {
			return product.flatten();
		})
	};
};


protocolVM.prototype.displayVersions = function() {
	$("#versionsModal").modal();
}

protocolVM.prototype.save = function (rootVM) {
	var self = this;
	var flat = self.flatten();

	if (!this.id) {
		this.id = Protocols.insert(_.extend({
			v: [flat]
		}, flat));
	} else if (!isUnchanged(flat, self.data)) {
		var xs = Experiments.find({ 'protocol._id': self.id, 'protocol.v': self.data.v.length - 1 });
		var xCount = xs.count();
		if (xCount > 0) {
			var cannotUpdate = false;
			var needsMapping = false;

			var paramMappings = [];
			if (!isUnchanged(flat.params, self.data.params)) {
				var oldParams = { };
				var oldParamsByType = { };
				_.each(self.data.params, function (oldParam) {
					oldParam = _.clone(oldParam);
					oldParam.allTypes = _.pluck(Types.findOne(oldParam.type).allBaseTypes, '_id');
					oldParam.allTypes.push(oldParam.type._id);
					oldParam.allTypesMap = { };

					_.each(oldParam.allTypes, function (typeId) {
						oldParam.allTypesMap[typeId] = 1;
						if (!oldParamsByType[typeId]) oldParamsByType[typeId] = { 0: [], 1: [] };
						oldParamsByType[typeId][oldParam.multi ? 1 : 0].push(oldParam);
					});
					oldParams[oldParam.name] = oldParam;
				});

				_.each(self.params(), function (param) {
					var oldParam = oldParams[param.name()];
					var typeMatchingOldParams = _.clone(oldParamsByType[param.type()._id()]) || { 0: [], 1: [] };
					_.each(param.type().allBaseTypes(), function (type) {
						if (oldParamsByType[type._id()]) {
							Array.prototype.push.apply(typeMatchingOldParams[0], oldParamsByType[type._id()][0]);
							Array.prototype.push.apply(typeMatchingOldParams[1], oldParamsByType[type._id()][1]);
						}
					});

					if (!typeMatchingOldParams[0] && !param.multi()) {
						cannotUpdate = true;
					} else {
						var obj = {
							param: param,
							possibleMappings: typeMatchingOldParams[param.multi() ? 1 : 0] || []
						};
						obj.source = ko.observable(_.contains(obj.possibleMappings, oldParam) && oldParam);
						obj.blank = ko.observable(param.multi() && !obj.source.peek());
						paramMappings.push(obj);
						if (!param.multi() && (!oldParam || !oldParam.allTypesMap[param.type()._id()] || !oldParam.allTypesMap[param.type()._id()][0])) needsMapping = true;
					}
				});
			}

			var inputMappings = [];
			if (!isUnchanged(flat.steps, self.data.steps)) {
				var oldInputs = { };
				var oldInputsByDesc = { };
				var oldInputsByType = { };

				_.each(self.data.steps, function (oldStep, oldStepIdx) {
					oldInputs[oldStep.desc] = { };
					_.each(oldStep.inputs, function (oldInput, oldInputIdx) {
						oldInput = _.clone(oldInput);
						oldInput.stepIdx = oldStepIdx;
						oldInput.inputIdx = oldInputIdx;
						oldInput.longDesc = oldInput.desc + ' of step "' + oldStep.desc + '"';
						oldInputs[oldStep.desc][oldInput.desc] = oldInput;
						if (!oldInputsByDesc[oldInput.desc]) oldInputsByDesc[oldInput.desc] = { };
						oldInputsByDesc[oldInput.desc][oldStepIdx] = oldInput;
						if (!oldInputsByType[oldInput.type]) oldInputsByType[oldInput.type] = [];
						oldInputsByType[oldInput.type].push(oldInput);
					});
				});

				_.each(self.steps(), function (step, stepIdx) {
					_.each(step.inputs(), function (input, inputIdx) {
						oldInput = oldInputs[step.desc()] && oldInputs[step.desc()][input.desc()];
						if (input.required() && !oldInputsByType[input.type().id]) {
							cannotUpdate = true;
						} else {
							var obj = {
								stepIdx: stepIdx,
								step: step,
								inputIdx: inputIdx,
								input: input,
								possibleMappings: oldInputsByType[input.type().id],
								source: ko.observable(oldInput || (oldInputsByDesc[input.desc()] && oldInputsByDesc[input.desc()][stepIdx])),
							};
							obj.blank = ko.observable(!input.required() && !obj.source.peek());
							inputMappings.push(obj);
							if (!oldInput || oldInput.type != input.type().id) needsMapping = true;
						}
					});
				});
			}

			if (cannotUpdate && Meteor.isClient) {
				rootVM.cannotCascadeModalVM({
					protocol: self,
					xCount: xCount,
					save: function () {
						Protocols.update(self.id, { $push: { v: flat }, $set: flat });
						Router.go('viewProtocol', { id: self.id });
					}
				});
				$('#cannotCascadeModal').modal();
			} else if (needsMapping && Meteor.isClient) {
				rootVM.mappingsModalVM({
					protocol: self,
					xCount: xCount,
					cascade: ko.observable(true),
					paramMappings: paramMappings,
					inputMappings: inputMappings,
					save: function () {
						if (this.cascade()) {
							var flatParamMappings = [];
							_.each(paramMappings, function (paramMapping) {
								if (!paramMapping.blank()) flatParamMappings.push({ param: paramMapping.param.name(), source: paramMapping.source().name });
							});

							var inputMappingsMap = { };
							_.each(inputMappings, function (inputMapping) {
								if (!inputMapping.blank()) {
									if (!inputMappingsMap[inputMapping.stepIdx]) inputMappingsMap[inputMapping.stepIdx] = { };
									inputMappingsMap[inputMapping.stepIdx][inputMapping.inputIdx] = { step: inputMapping.source().stepIdx, input: inputMapping.source().inputIdx };
								}
							});

							Meteor.call('updateProtocol', self.id, flat, self.data.v.length - 1, flatParamMappings, inputMappingsMap);
						} else {
							Protocols.update(self.id, { $push: { v: flat }, $set: flat });
						}
						$('#mappingsModal').on('hidden.bs.modal', function () {
							Router.go('viewProtocol', { id: self.id });
						});
					}
				});
				$('#mappingsModal').modal();
			}
			return;
		} else {
			Protocols.update(self.id, { $push: { v: flat }, $set: flat });
		}
	}
	if (Meteor.isClient) Router.go('viewProtocol', { id: self.id });
};

protocolVM.prototype.edit = function () {
	Router.go('viewProtocol', { id: this.id }, { query: { edit: 1 } });
}

protocolVM.prototype.cancel = function () {
	if (this.id) {
		Router.go('viewProtocol', { id: this.id });
	} else {
		Router.go('protocolList');
	}
};

function protocolParamVM(param) {
	var self = this;
	self.type = ko.observable(param && _.find(self.types(), function (type) {
		return type._id() == param.type._id;
	}));
	self.type.subscribe(function (newValue) {
		if (!self.nameWasChanged) self.name(newValue.name());
	});
	self.name = ko.observable(param && param.name);
	self.multi = ko.observable(param ? param.multi : false);
	self.nameWasChanged = param ? param.name != param.type.name : false;
}

protocolParamVM.prototype.types = ko_meteor_find(Types, { });

protocolParamVM.prototype.nameChanged = function () {
	this.nameWasChanged = true;
};

protocolParamVM.prototype.flatten = function () {
	return ko.toJS({
		type: _.pick(this.type(), '_id', 'name'),
		name: this.name,
		multi: this.multi
	});
};

function protocolStepVM(protocolVM, step) {
	var self = this;
	self.protocolVM = protocolVM;
	self.desc = ko.observable(step && step.desc);
	self.inputs = ko.observableArray(step ? _.map(step.inputs, function (input) {
		return new protocolStepInputVM(protocolVM, input);
	}) : []);
}

protocolStepVM.prototype.addInput = function () {
	this.inputs.push(new protocolStepInputVM(this.protocolVM));
};

protocolStepVM.prototype.removeInput = function (input) {
	this.inputs.remove(input);
};

protocolStepVM.prototype.flatten = function () {
	var obj = {
		desc: this.desc(),
		inputs: _.map(this.inputs(), function (input) {
			return input.flatten();
		})
	};

	return obj;
};

function protocolStepInputVM(protocolVM, input) {
	this.desc = ko.observable(input && input.desc);
	this.type = ko.observable(input && _.find(this.types, function (ptype) {
		return ptype.id == input.type;
	}));
	this.required = ko.observable(input ? input.required : true);
	this.multi = ko.observable(input ? !!input.multiParam : false);
	this.multiParam = ko.observable(input && _.find(protocolVM.params(), function (param) {
		return param.name() == input.multiParam;
	}));
}

protocolStepInputVM.prototype.types = [ { id: 'text', desc: 'Text' }, { id: 'uint', desc: 'Positive integer' }, { id: 'int', desc: 'Integer' }, { id: 'ufloat', desc: 'Positive real number' }, { id: 'float', desc: 'Real number' }, { id: '%', desc: 'Percentage' } ];

protocolStepInputVM.prototype.flatten = function () {
	return {
		desc: this.desc(),
		type: this.type().id,
		required: this.required(),
		multiParam: this.multi() ? this.multiParam().name() : null
	};
};

function protocolProductVM(protocolVM, product) {
	var self = this;
	self.name = ko.observable(product && product.name);
	self.types = ko.observableArray(product ? _.filter(self.possibleTypes(), function (ptype) {
		return _.contains(_.pluck(product.types, '_id'), ptype._id());
	}) : []);

	self.allTypes = ko.computed(function () {
		var map = { };

		_.each(self.types(), function (type) {
			map[type._id()] = type;
			_.each(type.baseTypes(), function (baseType) {
				map[baseType._id()] = baseType;
			});
		});

		return _.values(map);
	});

	self.propertyBindings = ko.computed(function () {
		var arr = [ ];
		var map = { };

		_.each(self.types(), function (type) {
			var usedTypes = { };

			_.each(type.allProperties(), function (property) {
				property = _.clone(property);
				if (!property.from) property.from = type;

				if (map[property.from._id()] != 1) {
					var obj = {
						property: property,
						source: ko.observable(),
						possibleSources: ko.computed(function () {
							var arr = [ ];

							_.each(protocolVM.params(), function (param) {
								if (!param.multi()) {
									_.each(param.type().allProperties(), function (paramProperty) {
										if (paramProperty.type() == property.type()) {
											arr.push({
												type: 'paramProperty',
												text: ko.computed(function () {
													return 'Property ' + paramProperty.name() + ' of parameter ' + param.name();
												}),
												param: param.name,
												paramProperty: paramProperty
											});
										}
									});
								}
							});

							_.each(protocolVM.steps(), function (step, stepIndex) {
								_.each(step.inputs(), function (input, inputIndex) {
									if ((input.type() && input.type().id) == property.type() && !input.multi()) {
										arr.push({
											type: 'input',
											text: ko.computed(function () {
												return 'Input field ' + input.desc() + ' of step "' + step.desc() + '"';
											}),
											input: {
												step: stepIndex,
												input: inputIndex
											}
										});
									}
								});
							});

							return arr;
						})
					};

					if (product && product.propertyBindings[property.from._id()] && product.propertyBindings[property.from._id()][CryptoJS.MD5(property.name()).toString()]) {
						obj.source(_.find(obj.possibleSources(), function (psource) {
							// Meteor 0.8 ships with underscore 1.5.2, which does not yet implement _.matches, so we'll have to do it ourselves
							return _.every(product.propertyBindings[property.from._id()][CryptoJS.MD5(property.name()).toString()].source, function (value, key) {
								return _.isEqual(ko.toJS(psource[key]), value);
							});
						}));
					}

					arr.push(obj);
					usedTypes[property.from._id()] = 1;
				}
			});

			_.extend(map, usedTypes);
		});

		return arr;
	});
}

protocolProductVM.prototype.possibleTypes = ko_meteor_find(Types, { });

protocolProductVM.prototype.flatten = function () {
	var propertyBindings = { };
	_.each(this.propertyBindings(), function (binding) {
		if (!propertyBindings[binding.property.from._id()]) propertyBindings[binding.property.from._id()] = { };
		propertyBindings[binding.property.from._id()][CryptoJS.MD5(binding.property.name()).toString()] = {
			property: {
				name: binding.property.name,
				from: _.pick(binding.property.from, '_id', 'name')
			},
			source: _.omit(binding.source(), 'text')
		}
	});

	return {
		name: this.name(),
		types: ko.toJS(_.map(this.types(), function (type) {
			return _.pick(type, '_id', 'name');
		})),
		allTypes: ko.toJS(_.map(this.allTypes(), function (type) {
			return _.pick(type, '_id', 'name');
		})),
		propertyBindings: ko.toJS(propertyBindings)
	};
};

Meteor.methods({
	'updateProtocol': function (id, newVersion, oldVersionNo, paramMappings, inputMappings) {
		newVersion = _.extend(_.clone(newVersion), { versionMappings: { params: paramMappings, inputs: inputMappings } });
		Protocols.update(id, { $push: { v: newVersion }, $set: newVersion }, function (error) {
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
