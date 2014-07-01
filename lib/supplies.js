supplyVersionVM = function(id, version, index) {
	var self = this;
	self.id = id;
	self.versionNr = index;
	self.version = version;
	self.href = Router.path('viewSupply', { id: self.id }, { query: { v: self.versionNr } });
}

supplyVersionVM.prototype.isCurrent = function(currentVersionNr) {
	return this.versionNr == currentVersionNr;

}

supplyVersionVM.prototype.hideModal = function() {
	$("#versionModal").modal('hide');
	return true; // Allow standard event handler for href
}

supplyVM = function (data, tryUpdate) {
	supplyVM.prototype.possibleTypes = ko_meteor_find(Types, { });

	var self = this;
	self.editMode = data.editMode;
	self.data = ko.unwrap(data.supply);
	self.id = self.data && self.data._id;
	self.version = self.data && (typeof ko.unwrap(data.version) == 'undefined' ? self.data.v.length - 1 : ko.unwrap(data.version));
	self.oldVersion = self.data && self.data.v && typeof ko.unwrap(data.version) != 'undefined' && ko.unwrap(data.version) != self.data.v.length - 1;
	self.versions = self.data && _.map(self.data.v, function(version, index) {
		return new supplyVersionVM(self.id, version, index);
	}).reverse();
	self.needsReview = ko.observable(self.data && self.data.needsReview);

	self.types = ko.observableArray(self.data ? _.filter(this.possibleTypes(), function (ptype) {
		return _.some(self.data.v[self.version].types, function (type) {
			return ptype._id() == type._id;
		});
	}) : []);

	self.autoUpdateFailed = false; // only meaningful when tryUpdate == true

	self.properties = ko.computed(function () {
		var map = { };
		_.each(self.types(), function (type) {
			var typeMap = { };
			var typeVersion;
			if (self.data && !(self.editMode && self.editMode())) {
				var refType = _.find(self.data.v[self.version].types, function (ptype) {
					return ptype._id == type._id();
				});
				if (refType) typeVersion = refType.v;
			}
			if (!typeVersion) typeVersion = type.v().length - 1;
			_.each(type.v()[typeVersion].allProperties(), function (property) {
				if (!property.from) property.from = type;

				if (!typeMap[property.from._id()]) typeMap[property.from._id()] = { };
				typeMap[property.from._id()][property.name()] = {
					from: _.pick(property.from, '_id', 'name'),
					name: property.name,
					value: ko.observable(self.data && self.data.v[self.version].properties[property.from._id()] && self.data.v[self.version].properties[property.from._id()][CryptoJS.MD5(property.name()).toString()] && self.data.v[self.version].properties[property.from._id()][CryptoJS.MD5(property.name()).toString()].value)
				};
			});

			if (tryUpdate && typeVersion == type.v().length - 2) {
				var typeMapBackup = _.clone(typeMap);
				var updateMap = { };
				typeMap[type._id()] = { };
				_.each(type.versionMappings(), function (mapping) {
					if (!updateMap[mapping.property.from._id()]) updateMap[mapping.property.from._id()] = { };
					var sourceTypeId = (ko.unwrap(mapping.source.from) || mapping.property.from)._id();
					if (typeMapBackup[sourceTypeId] && typeof typeMapBackup[sourceTypeId][mapping.source.name()] != 'undefined') {
						updateMap[mapping.property.from._id()][mapping.property.name()] = {
							name: mapping.property.name,
							from: mapping.property.from,
							value: typeMapBackup[sourceTypeId][mapping.source.name()].value
						};
					} else if (tryUpdate && _.find(type.allProperties(), function (pproperty) {
						return (pproperty.from || type)._id() == mapping.property.from._id() && pproperty.name() == mapping.property.name();
					}).required()) {
						self.autoUpdateFailed = true;
					}
				});
				if (self.autoUpdateFailed) {
					typeMap = typeMapBackup;
				} else {
					_.each(updateMap, function (mappingsForType, typeId) {
						if (!typeMap[typeId]) typeMap[typeId] = { };
						_.extend(typeMap[typeId], mappingsForType);
					});
				}
			}
			_.extend(map, typeMap);
		});

		return _.flatten(_.map(map, _.values));
	});

	self.source = ko.observable(self.data && self.data.v[self.version].source);

	self.date = ko.observable(self.data ? self.data.v[self.version].date : new Date());
	self.dateUpdate = !self.data && setInterval(function () {
		self.date(new Date());
	}, 1000);

	self.notes = ko.observable(self.data && self.data.v[self.version].notes);
};

supplyVM.prototype.flatten = function (changeType) {
	var allTypes = { };
	_.each(this.types(), function (type) {
		allTypes[type._id()] = _.pick(type, '_id', 'name');
		_.each(type.allBaseTypes(), function (baseType) {
			allTypes[baseType._id()] = _.extend({
				v: type.v().length - 1
			}, _.pick(baseType, '_id', 'name'));
		});
	});

	var properties = { };
	_.each(this.properties(), function (property) {
		if (!properties[property.from._id()]) properties[property.from._id()] = { };
		properties[property.from._id()][CryptoJS.MD5(property.name()).toString()] = property;
	});

	return ko.toJS({
		types: _.map(this.types(), function (type) {
			var obj = _.extend({
				text: '',
				v: type.v().length - 1
			}, _.pick(type, '_id', 'name'));
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
		notes: this.notes,
		mtime: new Date(),
		changeType: changeType
	});
};

supplyVM.prototype.save = function (changeType) {
	clearInterval(this.dateUpdate);
	var flat = this.flatten(changeType);

	if (!this.id) {
		Meteor.call('insertSupply', flat, function (error, result) {
			if (!error) {
				self.id = result;
				if (!changeType) Router.go('viewSupply', { id: self.id });
			}
		});
		return;
	} else if (!isUnchanged(flat, this.data)) {
		Meteor.call('updateSupply', this.id, flat);
	}

	if (this.autoUpdateFailed) {
		// Should only happen on the server, so we don't need Meteor.methods()
		Supplies.update(this.id, { $set: { needsReview: true } })
	}

	if (!changeType) Router.go('viewSupply', { id: this.id });
	return this.data ? this.data.v.length : 0;
};

supplyVM.prototype.edit = function () {
	Router.go('viewSupply', { id: this.id }, { query: { edit: 1 } });
};

supplyVM.prototype.cancel = function () {
	if (this.id) {
		Router.go('viewSupply', { id: this.id });
	} else {
		Router.go('suppliesList');
	}
};

supplyVM.prototype.displayVersions = function() {
	$("#versionModal").modal();
}

Meteor.methods({
	insertSupply: function (flat) {
		if (!this.userId) return;
		flat.editor = this.userId;
		return Supplies.insert(_.extend({
			v: [flat]
		}, flat));
	},
	updateSupply: function (id, newVersion) {
		if (!this.userId) return;
		newVersion.editor = this.userId;
		Supplies.update(id, { $push: { v: newVersion }, $set: newVersion, $unset: { needsReview: true } }, function (error) {
			Experiments.find({ sourceSupplies: id }).forEach(function (dependentExperiment) {
				var protocol = Protocols.findOne(dependentExperiment.protocol._id);
				var vm = new experimentVM({ experiment: dependentExperiment, protocol: protocol }, undefined, true);
				vm.save(dependentExperiment.v[dependentExperiment.v.length - 1].performer, {
					type: 'cascade',
					dependency: {
						type: 'supply',
						id: id
					}
				});
			});
		});
	}
});
