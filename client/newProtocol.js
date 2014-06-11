'use strict';

function newProtocolVM() {
	var self = this;
	self.name = ko.observable('Enter the name of the new protocol here');
	self.params = ko.observableArray();
	self.multiParams = ko.computed(function () {
		return _.filter(self.params(), function (param) {
			return param.multi();
		});
	});
	self.steps = ko.observableArray();
	self.products = ko.observableArray();
}

newProtocolVM.prototype.addParam = function () {
	this.params.push(new newProtocolParamVM());
};

newProtocolVM.prototype.removeParam = function (param) {
	this.params.remove(param);
};

newProtocolVM.prototype.addStep = function () {
	this.steps.push(new newProtocolStepVM());
};

newProtocolVM.prototype.removeStep = function (step) {
	this.steps.remove(step);
};

newProtocolVM.prototype.addProduct = function () {
	this.products.push(new newProtocolProductVM(this));
};

newProtocolVM.prototype.removeProduct = function (product) {
	this.products.remove(product);
};

newProtocolVM.prototype.flatten = function () {
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

newProtocolVM.prototype.save = function () {
	Protocols.insert(this.flatten());
};

function newProtocolParamVM() {
	var self = this;
	self.type = ko.observable();
	self.type.subscribe(function (newValue) {
		if (!self.nameWasChanged) self.name(newValue.name());
	});
	self.name = ko.observable();
	self.multi = ko.observable(false);
	self.nameWasChanged = false;
}

newProtocolParamVM.prototype.types = ko.meteor.find(Types, { });

newProtocolParamVM.prototype.nameChanged = function () {
	this.nameWasChanged = true;
};

newProtocolParamVM.prototype.flatten = function () {
	return {
		type: this.type()._id(),
		name: this.name(),
		multi: this.multi()
	};
};

function newProtocolStepVM() {
	var self = this;
	self.desc = ko.observable('Enter description of the step');
	self.inputs = ko.observableArray();
	self.substep = ko.observable(false);
	self.substepParam = ko.observable();
	self.substepDesc = ko.observable('Enter description of the repeating sub-step');
	self.substepInputs = ko.observableArray();
}

newProtocolStepVM.prototype.addInput = function () {
	this.inputs.push(new newProtocolStepInputVM());
};

newProtocolStepVM.prototype.removeInput = function (input) {
	this.inputs.remove(input);
};

newProtocolStepVM.prototype.addSubInput = function () {
	this.substepInputs.push(new newProtocolStepInputVM());
};

newProtocolStepVM.prototype.removeSubInput = function (input) {
	this.substepInputs.remove(input);
};

newProtocolStepVM.prototype.flatten = function () {
	var obj = {
		desc: this.desc(),
		inputs: _.map(this.inputs(), function (input) {
			return input.flatten();
		}),
		substep: this.substep()
	};

	if (this.substep()) {
		obj = _.extend(obj, {
			substepParam: this.substepParam().name(),
			substepDesc: this.substepDesc(),
			substepInputs: _.map(this.substepInputs(), function (input) {
				return input.flatten();
			})
		});
	};

	return obj;
};

function newProtocolStepInputVM() {
	this.desc = ko.observable('Enter description of the input field here');
	this.type = ko.observable();
}

newProtocolStepInputVM.prototype.types = [ { id: 'text', desc: 'Text' }, { id: 'uint', desc: 'Positive integer' }, { id: 'int', desc: 'Integer' }, { id: 'ufloat', desc: 'Positive real number' }, { id: 'float', desc: 'Real number' } ];

newProtocolStepInputVM.prototype.flatten = function () {
	return {
		desc: this.desc(),
		type: this.type().id
	};
};

function newProtocolProductVM(parent) {
	var self = this;
	self.parent = parent;
	self.name = ko.observable('Enter name of the product here');
	self.types = ko.observableArray();

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
					arr.push({
						property: property,
						source: ko.observable(),
						possibleSources: ko.computed(function () {
							var arr = [ ];

							_.each(parent.params(), function (param) {
								if (!param.multi()) {
									_.each(param.type().allProperties(), function (paramProperty) {
										if (paramProperty.type() == property.type()) {
											arr.push({
												type: 'paramProperty',
												text: ko.computed(function () {
													return 'Property ' + paramProperty.name() + ' of parameter ' + param.name();
												}),
												param: param.name(),
												paramProperty: paramProperty
											});
										}
									});
								}
							});

							_.each(parent.steps(), function (step, stepIndex) {
								_.each(step.inputs(), function (input, inputIndex) {
									if (input.type().id == property.type()) {
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
					});
					usedTypes[property.from._id()] = 1;
				}
			});

			_.extend(map, usedTypes);
		});

		return arr;
	});
}

newProtocolProductVM.prototype.possibleTypes = ko.meteor.find(Types, { });

newProtocolProductVM.prototype.flatten = function () {
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
				from: binding.property.from,
				source: _.omit(binding.source(), 'text')
			};
			return memo;
		}, { }))
	};
};

Template.newProtocol.rendered = function () {
	console.log('newProtocol.rendered', this);
	var node = this.firstNode;
	this.vm = new newProtocolVM();
	do {
		// apply bindings to each direct child element of the template
		// this does not apply to comments, i. e. containerless binding syntax!
		// to enable both, we'd need to parse the comments ourselves
		if (node.nodeType == Node.ELEMENT_NODE) ko.applyBindings(this.vm, node);
	} while (node = node.nextSibling);
};

Template.newProtocol.destroyed = function () {
	console.log('newProtocol.destroyed', this);
	var node = this.firstNode;
	do {
		if (node.nodeType == Node.ELEMENT_NODE) ko.cleanNode(node);
	} while (node = node.nextSibling);
};
