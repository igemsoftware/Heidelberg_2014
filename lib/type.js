Type = function (data, version) {
	var self = this;
	self._id = ko.observable(data && data._id);
	if (data) {
		if (!typesUpdate) typesUpdater();
		self.typeMap[data._id](this); // TODO
	}
	self.version = version === undefined ? data && data.v.length - 1 : version;
	self.oldVersion = data && self.version != data.v.length - 1;
	self.DBData = data;
	self.data = data && data.v[self.version];

	self.name = ko.observable(self.data && self.data.name);
	self.baseTypes = ko.observableArray(self.data ? _.map(self.data.baseTypes, function (baseType) {
		return self.typeMap[baseType._id].peek();
	}) : []);

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

	self.properties = ko.observableArray(self.data ? _.map(self.data.properties, function (property) {
		return new TypeProperty(self, property);
	}) : []);
	self.inheritedProperties = ko.computed(function () {
		var arr = [];
		var map = { };
		_.each(self.baseTypes(), function (type) {
			var usedTypes = { };
			usedTypes[type._id()] = 1;

			_.each(type.allProperties(), function (property) {
				var typeid = (property.from || type)._id();
				if (map[typeid] != 1) {
					arr.push(property);
					usedTypes[typeid] = 1;
				}
			});

			_.extend(map, usedTypes);
		});

		return arr;
	});
	self.allProperties = ko.computed(function () {
		var arr = _.clone(self.properties());
		Array.prototype.push.apply(arr, self.inheritedProperties());
		return arr;
	});

	self.text = ko.observable(self.data && self.data.text);
};

Type.prototype.href = function () {
	return Router.path('viewType', { id: this._id() });
};

Type.prototype.getText = function (values) {
	var self = this;
	var text = '';
	_.each(self.text(), function (part) {
		switch (part.type) {
			case 'text':
				text = text + part.text;
				break;
			case 'propertyReference':
				text = text + ko.unwrap(values[ko.unwrap((part.property.from || self)._id)][part.property.name]);
				break;
		}
	});
	return text;
};

Type.prototype.addProperty = function () {
	this.properties.push(new TypeProperty(this));
};

Type.prototype.removeProperty = function (property) {
	this.properties.remove(property);
};

Type.prototype.toReference = function () {
	var id = this._id();
	return id && {
		_id: id,
		name: this.name(),
		v: this.version
	};
};

Type.prototype.flatten = function () {
	return {
		name: this.name(),
		baseTypes: _.map(this.baseTypes(), function (baseType) {
			return baseType.toReference();
		}),
		allBaseTypes: _.map(this.allBaseTypes(), function (baseType) {
			return baseType.toReference();
		}),
		properties: _.map(this.properties(), function (property) {
			return property.flatten();
		}),
		allProperties: _.map(this.allProperties(), function (property) {
			return property.flatten();
		}),
		text: this.text(),
	};
};

Type.prototype.tryUpdate = function (baseMappings) {
	if (this.oldVersion) throw "tryUpdate cannot be called on old versions.";
	if (!baseMappings) return true;

	_.each(this.text(), function (part, idx) {
		if (part.type == 'propertyReference' && part.property.from) {
			var matching = _.filter(baseMappings, function (mapping) {
				return (mapping.source.from || mapping.property.from)._id == part.property.from._id && mapping.source.name == part.property.name;
			});
			// TODO: implement failure of cascading type updates in a safe way
			//if (matching.length == 1) {
				part = _.clone(part);
				part.property = matching[0].property;
				flattened.text[idx] = part;
			/*} else if (matching.length != 0) {
				fail_save();
			}*/
		}
	});
	this.versionMappings = baseMappings;
	return true;
};

TypeProperty = function (from, data) {
	this.from = from;

	this.name = ko.observable(data ? data.name : '');
	this.type = ko.observable(data ? PODType.typeMap[data.type] : PODType.types[0]);
	this.required = ko.observable(data ? data.required : true);
};

TypeProperty.prototype.types = PODType.types;

TypeProperty.prototype.toReference = function () {
	return {
		name: this.name(),
		from: this.from.toReference(),
	};
};

TypeProperty.prototype.flatten = function () {
	return {
		name: this.name(),
		type: this.type().id,
		required: this.required(),
		from: this.from.toReference(),
		versionMappings: this.versionMappings,
	};
};

function reloadTypes() {
	// TODO
	//if (subscription && subscription.ready()) {
		Type.prototype.typeMap = { };
		var types = Types.find().fetch();
		_.each(types, function (type) {
			Type.prototype.typeMap[type._id] = ko.observable(ko.mapping.fromJS(type));
		});
		Type.prototype.types = _.map(types, function (type) {
			return new Type(type);
		});
	//}
}

var typesUpdate;

function typesUpdater() {
	if (Meteor.isClient) {
		if (!typesUpdate && subscription && subscription.ready()) {
			typesUpdate = true;
			Deps.autorun(reloadTypes);
		}
	} else {
		typesUpdate = true;
		reloadTypes();
	}
}

Meteor.startup(typesUpdater);

Meteor.methods({
	insertType: function (flat) {
		if (!this.userId) throw 403;

		flat.editor = this.userId;
		flat.mtime = new Date();
		return Types.insert(_.extend({
			v: [flat],
		}, flat));
		reloadTypes(); // TODO
	},
	updateType: function (id, newVersion) {
		if (!this.userId) throw 403;

		newVersion.editor = this.userId;
		newVersion.mtime = new Date();

		var changeType = {
			type: 'cascade',
			dependency: {
				type: 'type',
				id: id,
				changeType: newVersion.changeType,
			}
		};

		Types.update(id, { $push: { v: newVersion }, $set: newVersion }, function (error) {
			reloadTypes(); // TODO

			Types.find({ 'allBaseTypes._id': id }).forEach(function (dependentType) {
				var obj = new Type(dependentType);
				obj.tryUpdate(newVersion.versionMappings);
				var flat = obj.flatten();
				if (!isUnchanged(flat, dependentType)) {
					Meteor.call('updateType', dependentType._id, _.extend({ changeType: changeType }, flat));
				}
			});

			Supplies.find({ 'types._id': id, needsReview: { $exists: false } }).forEach(function (supply) {
				var obj = new Supply(supply, undefined, true);
				var flat;
				try {
					flat = obj.flatten();
				} catch (e) {
					// The result being thrown as an exception signals a failed cascading update; just set needsReview
					// Check if the exception really is the result first
					if (e instanceof Error) throw e;
					Supplies.update(supply._id, { $set: { needsReview: true } }, { multi: true });
				}
				if (flat && !isUnchanged(flat, supply)) {
					Meteor.call('updateSupply', supply._id, _.extend({ changeType: changeType }, flat));
				}
			});

			Protocols.find({ $or: [{ 'params.type._id': id }, { 'products.types._id': id }], needsReview: { $exists: false } }).forEach(function (protocol) {
				var obj = new Protocol(protocol, undefined, true);
				var flat;
				try {
					flat = obj.flatten();
				} catch (e) {
					// The result being thrown as an exception signals a failed cascading update; just set needsReview
					// Check if the exception really is the result first
					if (e instanceof Error) throw e;
					Protocols.update(protocol._id, { $set: { needsReview: true } }, { multi: true });
				}
				if (flat && !isUnchanged(flat, protocol)) {
					Meteor.call('updateProtocol', protocol._id, _.extend({ changeType: changeType }, flat), protocol.v.length - 1);
				}
			});
		});
	},
	updateTypeWithoutCascade: function (id, newVersion) {
		if (!this.userId) throw 403;

		newVersion.editor = this.userId;
		newVersion.mtime = new Date();

		var changeType = {
			type: 'cascade',
			dependency: {
				type: 'type',
				id: id,
				changeType: newVersion.changeType,
			}
		};

		Types.update(id, { $push: { v: newVersion }, $set: newVersion }, function (error) {
			Types.find({ 'allBaseTypes._id': id }).forEach(function (dependentType) {
				var obj = new Type(dependentType);
				obj.tryUpdate(newVersion.versionMappings);
				var flat = obj.flatten();
				if (!isUnchanged(flat, dependentType)) {
					Meteor.call('updateTypeWithoutCascade', dependentType._id, _.extend({ changeType: changeType }, flat));
				}
			});
		});

		Supplies.update({ 'types._id': id }, { $set: { needsReview: true } }, { multi: true });
		Protocols.update({ $or: [{ 'params.type._id': id }, { 'products.types._id': id }] }, { $set: { needsReview: true } }, { multi: true });
	}
});
