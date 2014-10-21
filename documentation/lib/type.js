Type = function (manager, data, version) {
	var self = this;
	self.manager = manager;
	self._id = ko.observable(data && data._id);
	self.version = version === undefined ? data && data.v.length - 1 : version;
	self.oldVersion = data && self.version != data.v.length - 1;
	self.DBData = data;
	self.data = data && data.v[self.version];

	self.types = ko.computed({
		read: function () {
			return _.map(Types.find().fetch(), function (type) {
				return self.manager.getType(type._id, undefined, type);
			});
		},
		deferEvaluation: true,
	});

	self.name = ko.observable(self.data && self.data.name);
	self.baseTypes = ko.computed({
		read: function () {
			self.types();
			return ko.observableArray(self.data ? _.map(self.data.baseTypes, function (baseType) {
				return self.manager.getType(baseType._id);
			}) : []);
		},
		deferEvaluation: true,
	});

	self.allBaseTypes = ko.computed({
		read: function () {
			var allBaseTypes = { };

			_.each(self.baseTypes()(), function (baseType) {
				allBaseTypes[baseType._id()] = baseType;
				_.each(baseType.allBaseTypes(), function (baseBaseType) {
					allBaseTypes[baseBaseType._id()] = baseBaseType;
				});
			});

			return _.values(allBaseTypes);
		},
		deferEvaluation: true,
	});

	self.properties = ko.observableArray(self.data ? _.map(self.data.properties, function (property) {
		return new TypeProperty(self, property);
	}) : []);
	self.inheritedProperties = ko.computed({
		read: function () {
			var arr = [];
			var map = { };
			_.each(self.baseTypes()(), function (type) {
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
		},
		deferEvaluation: true,
	});
	self.allProperties = ko.computed({
		read: function () {
			var arr = _.clone(self.properties());
			Array.prototype.push.apply(arr, self.inheritedProperties());
			return arr;
		},
		deferEvaluation: true,
	});

	self.text = ko.observable(self.data && self.data.text);

	self.versionMappings = null;
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
				text = text + ko.unwrap(values[ko.unwrap((part.property.from || self)._id)][part.property.name].value());
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
		baseTypes: _.map(this.baseTypes()(), function (baseType) {
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
		versionMappings: this.versionMappings,
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
				part.property = matching[0].property;
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
	};
};

updateType = function (id, newVersion) {
	Types.update(id, { $push: { v: newVersion }, $set: newVersion });
	return {
		types: function () { return Types.find({ 'allBaseTypes._id': id }).fetch(); },
		supplies: function () { return Supplies.find({ 'types._id': id, needsReview: { $exists: false } }).fetch(); },
		protocols: function () { return Protocols.find({ $or: [{ 'params.type._id': id }, { 'products.types._id': id }], needsReview: { $exists: false } }).fetch(); },
		experiments: function () { return Experiments.find({ productTypes: id, needsReview: { $exists: false } }).fetch(); },
	};
};

Meteor.methods({
	insertType: function (flat) {
		if (!this.userId) throw 403;

		flat.editor = this.userId;
		flat.mtime = new Date();
		return Types.insert(_.extend({
			v: [flat],
		}, flat));
	},
	updateType: function (id, newVersion) {
		if (!this.userId) throw 403;

		var manager = new OMManager();

		newVersion.editor = this.userId;
		newVersion.mtime = new Date();

		return cascadingUpdate(manager, updateType(id, newVersion), {
			type: 'cascade',
			dependency: {
				type: 'type',
				id: id,
			}
		}, newVersion.versionMappings);
	},
	updateTypeWithoutCascade: function (id, newVersion) {
		if (!this.userId) throw 403;

		var manager = new OMManager();

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
				var obj = manager.getType(dependentType._id, undefined, dependentType);
				obj.tryUpdate(newVersion.versionMappings);
				var flat = obj.flatten();
				if (!isUnchanged(flat, dependentType)) {
					Meteor.call('updateTypeWithoutCascade', dependentType._id, _.extend({ changeType: changeType }, flat));
				}
			});
		});

		Supplies.update({ 'types._id': id }, { $set: { needsReview: true } }, { multi: true });
		Protocols.update({ $or: [{ 'params.type._id': id }, { 'products.types._id': id }] }, { $set: { needsReview: true } }, { multi: true });
		Experiments.update({ productTypes: id }, { $set: { needsReview: true } }, { multi: true });
	}
});
