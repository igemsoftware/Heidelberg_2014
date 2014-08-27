Supply = function (manager, data, version, tryUpdate) {
	var self = this;
	self.manager = manager;

	self._id = ko.observable(data && data._id);
	self.version = version === undefined ? data && data.v.length - 1 : version;
	self.oldVersion = data && self.version != data.v.length - 1;
	self.DBData = data;
	self.data = data && data.v[self.version];

	self.needsReview = ko.observable(data && data.needsReview);

	this.possibleTypes = _.map(Types.find().fetch(), function (type) {
		return self.manager.getType(type._id, undefined, type);
	});

	var typeMappings = { };
	self.types = ko.observableArray(self.DBData ? _.map(self.DBData.types, function (type) {
		var obj = self.manager.getType(type._id);
		if (type.v != obj.version) {
			if (!tryUpdate) {
				obj = self.manager.getType(type._id, type.v);
			} else if (obj.DBData.versionMappings) {
				_.each(obj.DBData.versionMappings, function (mapping) {
					if (!typeMappings[mapping.property.from._id]) typeMappings[mapping.property.from._id] = { };
					typeMappings[mapping.property.from._id][mapping.property.name] = mapping.source;
				});
			}
		}
		return obj;
	}) : []);

	var propertyMap = { };
	self.autoUpdateFailed = false; // only meaningful when tryUpdate == true
	self.propertyMap = ko.computed({
		read: function () {
			var map = { };
			_.each(self.types(), function (type) {
				_.each(type.allProperties(), function (property) {
					var fromId = property.from._id();
					var name = property.name();
					var md5Name = CryptoJS.MD5(name).toString();

					if (!propertyMap[fromId]) propertyMap[fromId] = { };

					var source;
					if (typeMappings[fromId] && typeMappings[fromId][name]) {
						var sourceTypeId = typeMappings[fromId][name].from._id;
						source = self.DBData.properties[sourceTypeId]
							&& self.DBData.properties[sourceTypeId][CryptoJS.MD5(typeMappings[fromId][name].name).toString()];
						if (!source && property.required()) {
							self.autoUpdateFailed = false;
						}
					} else if (self.DBData && self.DBData.properties[fromId]) {
						source = self.DBData.properties[fromId][md5Name];
					}

					if (!propertyMap[fromId][name]) propertyMap[fromId][name] = new SupplyProperty(this, property, source);

					if (!map[fromId]) map[fromId] = { };
					map[fromId][name] = propertyMap[fromId][name];
				});
			});

			return map;
		},
		deferEvaluation: true,
	});

	self.properties = ko.computed({
		read: function () {
			return _.flatten(_.map(self.propertyMap(), _.values));
		},
		deferEvaluation: true,
	});

	self.source = ko.observable(self.DBData && self.DBData.source);
	self.date = ko.observable(self.DBData ? self.DBData.date : new Date());
	self.notes = ko.observable(self.DBData && self.DBData.notes);

	self.href = ko.computed({
		read: function () {
			return Router.path('viewSupply', { id: self._id() });
		},
		deferEvaluation: true,
	});
	self.text = ko.computed({
		read: function () {
			return _.map(self.types(), function (type) {
				return type.getText(self.propertyMap());
			}).join('/');
		},
		deferEvaluation: true,
	});
	self.typeNames = ko.computed({
		read: function () {
			return _.invoke(self.types(), 'name').join(', ');
		},
		deferEvaluation: true,
	});
};

Supply.prototype.toReference = function () {
	return self._id() && {
		_id: self._id(),
		v: self.version,
	};
};

Supply.prototype.flatten = function () {
	var self = this;

	var allTypes = { };
	_.each(this.types(), function (type) {
		allTypes[type._id()] = type.toReference();
		_.each(type.allBaseTypes(), function (baseType) {
			allTypes[baseType._id()] = baseType.toReference();
		});
	});

	var properties = { };
	_.each(self.properties(), function (property) {
		if (!properties[property.property.from._id()]) {
			properties[property.property.from._id()] = { };
		}
		properties[property.property.from._id()][CryptoJS.MD5(property.property.name()).toString()] = property.flatten();
	});

	var flat = {
		types: _.map(self.types(), function (type) {
			return _.extend({
				text: type.getText(self.propertyMap()),
			}, type.toReference());
		}),
		allTypes: _.values(allTypes),
		properties: properties,
		source: self.source(),
		date: self.date(),
		notes: self.notes(),
	};

	if (self.autoUpdateFailed) throw flat; // TODO: Not very elegant ...
	return flat;
};

SupplyProperty = function (supply, property, data) {
	this.parent = supply;

	this.property = property;
	this.value = ko.observable(data && data.value);
};

SupplyProperty.prototype.flatten = function () {
	return {
		from: this.property.from.toReference(),
		name: this.property.name(),
		value: this.value(),
	};
};

updateSupply = function (id, newVersion) {
	Supplies.update(id, { $push: { v: newVersion }, $set: newVersion, $unset: { needsReview: true } });
	return {
		experiments: function () { return Experiments.find({ sourceSupplies: id }).fetch(); },
	};
};

Meteor.methods({
	insertSupply: function (flat) {
		if (!this.userId) throw 403;

		flat.editor = this.userId;
		flat.mtime = new Date();
		return Supplies.insert(_.extend({
			v: [flat],
		}, flat));
	},
	updateSupply: function (id, newVersion) {
		if (!this.userId) throw 403;

		var manager = new OMManager();

		newVersion.editor = this.userId;
		newVersion.mtime = new Date();

		cascadingUpdate(manager, updateSupply(id, newVersion), {
			type: 'cascade',
			dependency: {
				type: 'supply',
				id: id,
			}
		});
	}
});
