'use strict';

var newProtocolVM = function () {
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
};

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
	this.products.push(new newProtocolProductVM());
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

var newProtocolParamVM = function () {
	var self = this;
	self.type = ko.observable();
	self.type.subscribe(function (newValue) {
		if (!self.nameWasChanged) self.name(newValue.name);
	});
	self.name = ko.observable();
	self.multi = ko.observable(false);
	self.nameWasChanged = false;
};

newProtocolParamVM.prototype.classes = function () {
	return Classes.find().fetch();
};

newProtocolParamVM.prototype.nameChanged = function (data) {
	data.nameWasChanged = true;
};

newProtocolParamVM.prototype.flatten = function () {
	return {
		type: this.type()._id,
		name: this.name(),
		multi: this.multi()
	};
};

var newProtocolStepVM = function () {
	var self = this;
	self.desc = ko.observable('Enter description of the step');
	self.inputs = ko.observableArray();
	self.substep = ko.observable(false);
	self.substepParam = ko.observable();
	self.substepDesc = ko.observable('Enter description of the repeating sub-step');
	self.substepInputs = ko.observableArray();
};

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

var newProtocolStepInputVM = function () {
	var self = this;
	self.desc = ko.observable('Enter description of the input field here');
	self.type = ko.observable();
};

newProtocolStepInputVM.prototype.types = [ { id: 'text', desc: 'Text' }, { id: 'uint', desc: 'Positive integer' }, { id: 'int', desc: 'Integer' }, { id: 'ufloat', desc: 'Positive real number' }, { id: 'float', desc: 'Real number' } ];

newProtocolStepInputVM.prototype.flatten = function () {
	return {
		desc: this.desc(),
		type: this.type().id
	};
};

var newProtocolProductVM = function () {
	var self = this;
	self.name = ko.observable('Enter name of the product here');
	self.classes = ko.observableArray();
};

newProtocolProductVM.prototype.allClasses = function () {
	return Classes.find().fetch();
};
newProtocolProductVM.prototype.flatten = function () {
	return {
		name: this.name(),
		classes: _.map(this.classes(), function (xlass) {
			return xlass._id;
		})
	};
};

UI.registerHelper('protocols', function () {
	return Protocols.find();
});

Template.newProtocol.rendered = function () {
	var node = this.firstNode;
	this.vm = new newProtocolVM();
	do {
		if (node.nodeType == Node.ELEMENT_NODE) ko.applyBindings(this.vm, node);
	} while (node = node.nextSibling);
};

Template.newProtocol.isSelected = function (type) {
	return type === this._id;
};

Template.newProtocol.isChecked = function () {
	return this.multi;
};

Template.newProtocol.steps = function () {
	return Session.get('newProtocolSteps');
};

Template.newProtocol.results = function () {
	return Session.get('newProtocolResults');
};
