'use strict';

function protocolVM(protocol) {
	var self = this;
	self.editMode = ko.observable(!protocol);
	self.id = protocol && protocol._id;
	self.name = ko.observable(protocol ? protocol.name : 'Enter the name of the new protocol here');

	self.params = ko.observableArray(protocol ? _.map(protocol.params, function (param) {
		return new protocolParamVM(param);
	}) : []);
	self.multiParams = ko.computed(function () {
		return _.filter(self.params(), function (param) {
			return param.multi();
		});
	});

	self.steps = ko.observableArray(protocol ? _.map(protocol.steps, function (step) {
		return new protocolStepVM(self, step);
	}) : []);

	self.products = ko.observableArray(protocol ? _.map(protocol.products, function (product) {
		return new protocolProductVM(self, product);
	}) : []);
}

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

protocolVM.prototype.save = function () {
	if (!this.id) this.id = Protocols.insert(this.flatten());
	this.editMode(false);
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
	self.nameWasChanged = param ? param.name == param.type.name : false;
}

protocolParamVM.prototype.types = ko.meteor.find(Types, { });

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
	self.desc = ko.observable(step ? step.desc : 'Enter description of the step');
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
	this.desc = ko.observable(input ? input.desc : 'Enter description of the input field here');
	this.type = ko.observable(input && _.find(this.types, function (ptype) {
		return ptype.id == input.type;
	}));
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
		multiParam: this.multi() ? this.multiParam().name() : null
	};
};

function protocolProductVM(protocolVM, product) {
	var self = this;
	self.name = ko.observable(product ? product.name : 'Enter name of the product here');
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
									if (input.type().id == property.type() && !input.multi()) {
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

					if (product && product.propertyBindings[property.name()]) obj.source(_.find(obj.possibleSources(), function (psource) {
						// Meteor 0.8 ships with underscore 1.5.2, which does not yet implement _.matches, so we'll have to do it ourselves
						return _.every(product.propertyBindings[property.name()].source, function (value, key) {
							return _.isEqual(ko.toJS(psource[key]), value);
						});
					}));

					arr.push(obj);
					usedTypes[property.from._id()] = 1;
				}
			});

			_.extend(map, usedTypes);
		});

		return arr;
	});
}

protocolProductVM.prototype.possibleTypes = ko.meteor.find(Types, { });

protocolProductVM.prototype.flatten = function () {
	return {
		name: this.name(),
		types: ko.toJS(_.map(this.types(), function (type) {
			return _.pick(type, '_id', 'name');
		})),
		allTypes: ko.toJS(_.map(this.allTypes(), function (type) {
			return _.pick(type, '_id', 'name');
		})),
		propertyBindings: ko.toJS(_.reduce(this.propertyBindings(), function (memo, binding) {
			memo[binding.property.name()] = {
				from: _.pick(binding.property.from, '_id', 'name'),
				source: _.omit(binding.source(), 'text')
			};
			return memo;
		}, { }))
	};
};

Template.protocol.rendered = function () {
	var self = this;
	self.vm = ko.computed(function () {
		return new protocolVM(self.data());
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

Template.protocol.destroyed = function () {
	_.each(this.nodesToClean, function (node) {
		ko.cleanNode(node);
	});
	this.vm.dispose();
};
