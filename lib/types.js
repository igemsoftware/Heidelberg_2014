typeVersionVM = function(id, version, index) {
	var self = this;
	self.id = id;
	self.versionNr = index;
	self.version = version;
	self.href = Router.path('viewType', { id: self.id }, { query: { v: self.versionNr } });
}

typeVersionVM.prototype.isCurrent = function(currentVersionNr) {
	return this.versionNr == currentVersionNr;
}

typeVersionVM.prototype.hideModal = function() {
	$("#versionsModal").modal('hide');
	return true; // Allow standard event handler for href
}

typeVM = function(data, textCallback) {
	typeVM.prototype.types = ko_meteor_find(Types, { });

	var self = this;
	self.editMode = data.editMode;
	self.data = ko.unwrap(data.type);
	self.id = self.data && self.data._id;

	self.version = self.data && (typeof ko.unwrap(data.version) == 'undefined' ? self.data.v.length - 1 : data.version());
	self.oldVersion = self.data && self.data.v && typeof ko.unwrap(data.version) != 'undefined' && ko.unwrap(data.version) != self.data.v.length - 1;
	self.versions = self.data && _.map(self.data.v, function (version, index) {
		return new typeVersionVM(self.id, version, index);
	}).reverse();

	self.name = ko.observable(self.data ? self.data.v[self.version].name : '');

	self.baseTypes = ko.observableArray(self.data ? _.filter(this.types(), function (ptype) {
		return _.contains(_.pluck(self.data.v[self.version].baseTypes, '_id'), ptype._id());
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

	self.properties = ko.observableArray(self.data ? _.map(self.data.v[self.version].properties, function (property) {
		return new typePropertyVM(property);
	}) : []);
	self.inheritedProperties = ko.computed(function () {
		var arr = [];
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

	self.textCallback = textCallback;
	self.propertyToRef = ko.observable();
}

typeVM.prototype.addProperty = function () {
	this.properties.push(new typePropertyVM());
};

typeVM.prototype.removeProperty = function (property) {
	this.properties.remove(property);
};

typeVM.prototype.flatten = function (changeType, baseMappings) {
	var self = this;

	var flattened = {
		name: self.name(),
		baseTypes: ko.toJS(_.map(self.baseTypes(), function (baseType) {
			return _.pick(baseType, '_id', 'name');
		})),
		allBaseTypes: ko.toJS(_.map(self.allBaseTypes(), function (baseType) {
			return _.pick(baseType, '_id', 'name');
		})),
		properties: _.map(self.properties(), function (property) {
			return property.flatten();
		}),
		mtime: new Date(),
		changeType: changeType
	};

	flattened.allProperties = _.clone(flattened.properties);
	Array.prototype.push.apply(flattened.allProperties, ko.toJS(self.inheritedProperties));

	flattened.text = self.textCallback();
	if (baseMappings) _.each(flattened.text, function (part, idx) {
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

	return flattened;
};

typeVM.prototype.save = function (changeType, baseMappings) {
	var self = this;
	var flat = self.flatten(changeType, baseMappings);

	if (!self.id) {
		Meteor.call('insertType', flat, function (error, result) {
			if (!error) {
				self.id = result;
				if (!changeType) Router.go('viewType', { id: self.id });
			}
		});
		return;
	} else if (!isUnchanged(flat, self.data)) {
		var ss = Supplies.find({ 'allTypes._id': self.id, needsReview: { $exists: false } });
		var sCount = ss.count();
		var ps = Protocols.find({ relevantTypes: self.id, needsReview: { $exists: false } });
		var pCount = ps.count();
		//if (sCount > 0 || pCount > 0) {
			var cannotUpdate = false;
			var needsMapping = false;

			var mappings = [];
			if (!isUnchanged(flat.properties, self.data.properties)) {
				var oldProperties = { };

				_.each(self.data.allProperties, function (oldProperty) {
					if (!oldProperty.from) oldProperties[oldProperty.name] = oldProperty;
				});

				_.each(self.properties(), function (property) {
					oldProperty = oldProperties[property.name()];
					if (property.required() && self.data.allProperties.length == 0) {
						cannotUpdate = true;
					} else {
						var obj = {
							property: property,
							possibleMappings: self.data.allProperties,
							source: ko.observable(oldProperty),
						};
						obj.blank = ko.observable(!property.required() && !obj.source.peek());
						mappings.push(obj);
						if (!oldProperty) needsMapping = true;
					}
				});
			}

			if (cannotUpdate && !changeType) {
				self.cannotCascadeModalVM({
					sCount: sCount,
					pCount: pCount,
					confirm: ko.observable(false),
					save: function () {
						if (this.confirm()) {
							Meteor.call('updateTypeWithoutCascade', self.id, flat, changeType);
						}
						$('#cannotCascadeModal').modal().on('hidden.bs.modal', function () {
							Router.go('viewType', { id: self.id });
						}).modal('hide');
						return true;
					}
				});
				$('#cannotCascadeModal').modal();
			} else if (needsMapping && !changeType) {
				self.mappingsModalVM({
					sCount: sCount,
					pCount: pCount,
					mappings: mappings,
					save: function () {
						var flatMappings = baseMappings || [];
						_.each(mappings, function (mapping) {
							if (!mapping.blank()) {
								flatMappings.push({
									property: {
										from: {
											_id: self.id,
											name: self.name()
										},
										name: mapping.property.name()
									},
									source: {
										from: mapping.source().from,
										name: mapping.source().name
									}
								});
							}
						});

						Meteor.call('updateType', self.id, flat, changeType, flatMappings);
						$('#mappingsModal').on('hidden.bs.modal', function () {
							Router.go('viewType', { id: self.id });
						}).modal('hide');
						return true;
					}
				});
				$('#mappingsModal').modal();
				return;
			} else {
				Meteor.call('updateType', self.id, flat, changeType, baseMappings);
			}
		/*} else {
			Meteor.call('updateTypeWithoutCascade', self.id, flat, changeType, baseMappings);
		}*/
	}

	if (!changeType) Router.go('viewType', { id: self.id });
};

typeVM.prototype.edit = function () {
	Router.go('viewType', { id: this.id }, { query: { edit: 1 } });
};

typeVM.prototype.cancel = function () {
	if (this.id) {
		Router.go('viewType', { id: this.id });
	} else {
		Router.go('typeList');
	}
};

typeVM.prototype.displayVersions = function() {
	$("#versionsModal").modal();
}

function typePropertyVM(property) {
	this.name = ko.observable(property ? property.name : '');
	this.type = ko.observable(property && _.find(this.types, function (ptype) {
		return ptype.id == property.type;
	}));
	this.required = ko.observable(property ? property.required : true);
}

typePropertyVM.prototype.types = [ { id: 'text', desc: 'Text' }, { id: 'uint', desc: 'Positive integer' }, { id: 'int', desc: 'Integer' }, { id: 'ufloat', desc: 'Positive real number' }, { id: 'float', desc: 'Real number' }, { id: '%', desc: 'Percentage' } ];

typePropertyVM.prototype.flatten = function () {
	return {
		name: this.name(),
		type: this.type().id,
		required: this.required()
	};
};

Meteor.methods({
	insertType: function (flat) {
		return Types.insert(_.extend({
			v: [flat]
		}, flat));
	},
	updateType: function (id, newVersion, originalChangeType, mappings) {
		Types.update(id, { $push: { v: newVersion }, $set: _.extend({ versionMappings: mappings }, newVersion) }, function (error) {
			Types.find({ 'allBaseTypes._id': id }).forEach(function (dependentType) {
				var vm = new typeVM({ type: dependentType }, function () { return dependentType.text; });
				vm.save({
					type: 'cascade',
					dependency: {
						type: 'type',
						id: id,
						changeType: originalChangeType
					}
				}, mappings);
			});

			Supplies.find({ 'types._id': id, needsReview: { $exists: false } }).forEach(function (supply) {
				var vm = new supplyVM({ supply: supply }, true);
				vm.save({
					type: 'cascade',
					dependency: {
						type: 'type',
						id: id,
						changeType: originalChangeType
					}
				});
			});

			Protocols.find({ $or: [ { 'params.type._id': id }, { 'products.types._id': id } ], needsReview: { $exists: false } }).forEach(function (protocol) {
				var vm = new protocolVM({ protocol: protocol }, true);
				vm.save({
					type: 'cascade',
					dependency: {
						type: 'type',
						id: id,
						changeType: originalChangeType
					}
				});
			});
		});
	},
	updateTypeWithoutCascade: function (id, newVersion, originalChangeType, mappings) {
		Types.update(id, { $push: { v: newVersion }, $set: _.extend({ versionMappings: mappings }, newVersion) }, function (error) {
			Types.find({ 'allBaseTypes._id': id }).forEach(function (dependentType) {
				var vm = new typeVM({ type: dependentType }, function () { return dependentType.text; });
				vm.save({
					type: 'cascade',
					dependency: {
						type: 'type',
						id: id,
						changeType: originalChangeType
					}
				}, mappings);
			});
		});

		Supplies.update({ 'allTypes._id': id }, { $set: { needsReview: true } }, { multi: true });
		Protocols.update({ relevantTypes: id }, { $set: { needsReview: true } }, { multi: true });
	}
});
