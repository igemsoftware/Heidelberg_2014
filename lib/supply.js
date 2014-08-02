Supply = function (data, version, tryUpdate) {
	var pTypeMap = { };
	this.possibleTypes = _.map(Types.find().fetch(), function (type) {
		return pTypeMap[type._id] = new Type(type);
	}); // TODO

	var self = this;
	self._id = ko.observable(data && data._id);
	self.version = version === undefined ? data && data.v.length - 1 : version;
	self.oldVersion = data && self.version != data.v.length - 1;
	self.DBData = data;
	self.data = data && data.v[self.version];

	self.needsReview = ko.observable(data && data.needsReview);

	var typeMappings = { };
	self.types = ko.observableArray(self.DBData ? _.map(self.DBData.types, function (type) {
		var obj = pTypeMap[type._id];
		if (type.v != obj.version) {
			if (!tryUpdate) {
				obj = new Type(Types.findOne(type._id), type.v);
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
	self.properties = ko.computed(function () {
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

		return _.flatten(_.map(map, _.values));
	});

	self.source = ko.observable(self.DBData && self.DBData.source);
	self.date = ko.observable(self.DBData ? self.DBData.date : new Date());
	self.notes = ko.observable(self.DBData && self.DBData.notes);
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
	var propertyValues = { };
	_.each(self.properties(), function (property) {
		if (!properties[property.property.from._id()]) {
			properties[property.property.from._id()] = { };
			propertyValues[property.property.from._id()] = { };
		}
		properties[property.property.from._id()][CryptoJS.MD5(property.property.name()).toString()] = property.flatten();
		propertyValues[property.property.from._id()][property.property.name()] = property.value;
	});

	var flat = {
		types: _.map(self.types(), function (type) {
			return _.extend({
				text: type.getText(propertyValues),
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

		newVersion.editor = this.userId;
		newVersion.mtime = new Date();

		cascadingUpdate(updateSupply(id, newVersion), {
			type: 'cascade',
			dependency: {
				type: 'supply',
				id: id,
			}
		});
	}
});
