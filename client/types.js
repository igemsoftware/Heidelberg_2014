'use strict';

UI.registerHelper('types', function () {
	return Types.find();
});

function newTypeVM() {
	var self = this;
	self.name = ko.observable('Enter the name of the new type here');
	self.baseTypes = ko.observableArray();

	self.allBaseTypes = ko.computed(function () {
		var allBaseTypes = { };

		_.each(self.baseTypes(), function (baseType) {
			allBaseTypes[baseType._id()] = baseType;
			_.each(baseType.allBaseTypes(), function (baseBaseType) {
				allBaseTypes[baseBaseType._id()] = baseBaseType;
			});
		});

		return _.values(allBaseTypes);
	});

	self.properties = ko.observableArray();
	self.inheritedProperties = ko.computed(function () {
		var arr = [ ];
		var map = { };
		_.each(self.baseTypes(), function (type) {
			var usedTypes = { };
			usedTypes[type._id()] = 1;

			_.each(type.allProperties(), function (property) {
				var typeid = property.from && property.from._id() || type._id();
				if (map[typeid] != 1) {
					property = _.clone(property);
					property.from = property.from || _.pick(type, '_id', 'name');
					arr.push(property);
				}
			});

			_.extend(map, usedTypes);
		});

		return arr;
	});
}

newTypeVM.prototype.types = ko.meteor.find(Types, { });

newTypeVM.prototype.addProperty = function () {
	this.properties.push(new newTypePropertyVM());
};

newTypeVM.prototype.removeProperty = function (property) {
	this.properties.remove(property);
};

newTypeVM.prototype.flatten = function () {
	var flattened = {
		name: this.name(),
		baseTypes: ko.toJS(_.map(this.baseTypes(), function (baseType) {
			return _.pick(baseType, '_id', 'name');
		})),
		allBaseTypes: ko.toJS(_.map(this.allBaseTypes(), function (baseType) {
			return _.pick(baseType, '_id', 'name');
		})),
		properties: _.map(this.properties(), function (property) {
			return property.flatten();
		})
	};

	flattened.allProperties = _.map(flattened.properties, _.clone);
	Array.prototype.push.apply(flattened.allProperties, ko.toJS(this.inheritedProperties));

	return flattened;
};

newTypeVM.prototype.save = function () {
	var x = this.flatten();
	console.log(x);
	Types.insert(x);
};

function newTypePropertyVM() {
	this.name = ko.observable('Enter the name of the property here');
	this.type = ko.observable();
}

newTypePropertyVM.prototype.types = [ { id: 'text', desc: 'Text' }, { id: 'uint', desc: 'Positive integer' }, { id: 'int', desc: 'Integer' }, { id: 'ufloat', desc: 'Positive real number' }, { id: 'float', desc: 'Real number' } ];

newTypePropertyVM.prototype.flatten = function () {
	return {
		name: this.name(),
		type: this.type().id
	};
};

Template.newType.rendered = function () {
	console.log('newType.rendered', this);
	var node = this.firstNode;
	this.vm = new newTypeVM();
	do {
		// apply bindings to each direct child element of the template
		// this does not apply to comments, i. e. containerless binding syntax!
		// to enable both, we'd need to parse the comments ourselves
		if (node.nodeType == Node.ELEMENT_NODE) ko.applyBindings(this.vm, node);
	} while (node = node.nextSibling);
};

Template.newType.destroyed = function () {
	console.log('newType.destroyed', this);
	var node = this.firstNode;
	do {
		if (node.nodeType == Node.ELEMENT_NODE) ko.cleanNode(node);
	} while (node = node.nextSibling);
};
