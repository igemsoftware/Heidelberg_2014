'use strict';

UI.registerHelper('supplies', function () {
	return Supplies.find();
});

Template.suppliesList.text = function () {
	return _.pluck(this.types, 'text').join('/');
};

function supplyVM(data) {
	var self = this;
	self.editMode = data.editMode;
	var supply = data.supply ? data.supply() : data.supply;
	self.id = supply && supply._id;

	self.types = ko.observableArray(supply ? _.filter(this.possibleTypes(), function (ptype) {
		return _.some(supply.types, function (type) {
			return ptype._id() == type._id;
		});
	}) : []);

	var propertyMap = { };
	self.properties = ko.computed(function () {
		var map = { };
		_.each(self.types(), function (type) {
			_.each(type.allProperties(), function (property) {
				if (!property.from) property.from = type;

				if (!propertyMap[property.from._id()]) propertyMap[property.from._id()] = { };
				if (!propertyMap[property.from._id()][property.name()]) propertyMap[property.from._id()][property.name()] = {
					from: _.pick(property.from, '_id', 'name'),
					name: property.name,
					value: ko.observable(supply && supply.properties[property.from._id()][CryptoJS.MD5(property.name()).toString()].value)
				};

				if (!map[property.from._id()]) map[property.from._id()] = { };
				map[property.from._id()][property.name()] = propertyMap[property.from._id()][property.name()];
			});
		});

		return _.flatten(_.map(map, _.values));
	});

	self.source = ko.observable(supply && supply.source);

	self.date = ko.observable(supply ? supply.date : new Date());
	self.dateUpdate = !supply && setInterval(function () {
		self.date(new Date());
	}, 1000);

	self.notes = ko.observable(supply && supply.notes);
}

supplyVM.prototype.possibleTypes = ko.meteor.find(Types, { });

supplyVM.prototype.flatten = function () {
	var allTypes = { };
	_.each(this.types(), function (type) {
		allTypes[type._id()] = _.pick(type, '_id', 'name');
		_.each(type.baseTypes(), function (baseType) {
			allTypes[baseType._id()] = _.pick(baseType, '_id', 'name');
		});
	});

	var properties = { };
	_.each(this.properties(), function (property) {
		if (!properties[property.from._id()]) properties[property.from._id()] = { };
		properties[property.from._id()][CryptoJS.MD5(property.name()).toString()] = property;
	});

	return ko.toJS({
		types: _.map(this.types(), function (type) {
			var obj = _.pick(type, '_id', 'name');
			obj.text = '';''
			_.each(type.text(), function (part) {
				switch (part.type()) {
					case 'text':
						obj.text = obj.text + part.text();
						break;
					case 'propertyReference':
						obj.text = obj.text + properties[(part.property.from || type)._id()][CryptoJS.MD5(part.property.name()).toString()].value();
						break;
				}
			});
			return obj;
		}),
		allTypes: ko.toJS(_.values(allTypes)),
		properties: properties,
		source: this.source,
		date: this.date,
		notes: this.notes
	});
};

supplyVM.prototype.save = function () {
	clearInterval(this.dateUpdate);
	if (!this.id)
		this.id = Supplies.insert(this.flatten());
	else
		Supplies.update(this.id, this.flatten());
	Router.go('viewSupply', {id: this.id, edit: false});
};

Template.supply.rendered = function () {
	var self = this;
	self.vm = ko.computed(function () {
		return new supplyVM(self.data);
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

Template.supply.destroyed = function () {
	_.each(this.nodesToClean, function (node) {
		ko.cleanNode(node);
	});
	this.vm.dispose();
};
