'use strict';

UI.registerHelper('types', function () {
	return Types.find();
});

function typeVM(textEditor, type) {
	var self = this;
	self.editMode = ko.observable(!type);
	self.id = type && type._id;
	self.name = ko.observable(type ? type.name : 'Enter the name of the new type here');

	self.baseTypes = ko.observableArray(type ? _.filter(this.types(), function (ptype) {
		return _.contains(_.pluck(type.baseTypes, '_id'), ptype._id());
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

	self.properties = ko.observableArray(type ? _.map(type.properties, function (property) {
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

	self.textEditor = textEditor;
	self.propertyToRef = ko.observable();
}

typeVM.prototype.types = ko.meteor.find(Types, { });

typeVM.prototype.addProperty = function () {
	this.properties.push(new typePropertyVM());
};

typeVM.prototype.removeProperty = function (property) {
	this.properties.remove(property);
};

typeVM.prototype.addRef = function () {
	var sel = window.getSelection();
	var ranges = [];
	for (var ii = 0; ii < sel.rangeCount; ii++) {
		var range = sel.getRangeAt(ii);
		if (this.textEditor.contains(range.commonAncestorContainer)) {
			range.deleteContents();

			var block = typeVM.createRefBlock(this.propertyToRef());
			range.insertNode(block);
			// TODO: <template instance>.nodesToClean.push(block);

			range = document.createRange();
			range.setStartAfter(block);
			range.collapse(true);
			ranges.push(range);

			this.textEditor.focus();
		} else {
			ranges.push(range);
		}
	}

	sel.removeAllRanges();
	_.each(ranges, function (range) {
		sel.addRange(range);
	})
};

typeVM.createRefBlock = function (vm) {
	var block = document.createElement('span');
	block.setAttribute('contenteditable', 'false');
	block.className = 'editorSpecial editorReference';
	block.setAttribute('data-bind', 'text: name');
	ko.applyBindings(vm, block);
	return block;
};

typeVM.prototype.flatten = function () {
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
		}),
		text: []
	};

	flattened.allProperties = _.map(flattened.properties, _.clone);
	Array.prototype.push.apply(flattened.allProperties, ko.toJS(this.inheritedProperties));

	_.each(this.textEditor.childNodes, function (child) {
		switch (child.nodeType) {
			case Node.ELEMENT_NODE:
				if (child.classList.contains('editorReference')) {
					flattened.text.push({ type: 'propertyReference', property: ko.dataFor(child).name() });
				}
				break;
			case Node.TEXT_NODE:
				if (child.nodeValue) flattened.text.push({ type: 'text', text: child.nodeValue })
				break;
		}
	})

	return flattened;
};

typeVM.prototype.save = function () {
	if (!this.id) this.id = Types.insert(this.flatten());
	this.editMode(false);
};

function typePropertyVM(property) {
	this.name = ko.observable(property ? property.name : 'Enter the name of the property here');
	this.type = ko.observable(property && _.find(this.types, function (ptype) {
		return ptype.id == property.type;
	}));
}

typePropertyVM.prototype.types = [ { id: 'text', desc: 'Text' }, { id: 'uint', desc: 'Positive integer' }, { id: 'int', desc: 'Integer' }, { id: 'ufloat', desc: 'Positive real number' }, { id: 'float', desc: 'Real number' }, { id: '%', desc: 'Percentage' } ];

typePropertyVM.prototype.flatten = function () {
	return {
		name: this.name(),
		type: this.type().id
	};
};

Template.type.rendered = function () {
	var self = this;
	var editor = self.find('#textEditor');
	self.vm = ko.computed(function () {
		return new typeVM(editor, self.data());
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

		if (self.data()) {
			_.each(self.data().text, function (part) {
				switch (part.type) {
					case 'text':
						editor.appendChild(document.createTextNode(part.text));
						break;
					case 'propertyReference':
						var block = typeVM.createRefBlock(_.find(self.vm().allProperties(), function (property) {
							return property.name() == part.property;
						}));
						editor.appendChild(block);
						self.nodesToClean.push(block);
						break;
				}
			});
		}
		editor.appendChild(document.createElement('br'));
	}, 0);
};

Template.type.destroyed = function () {
	_.each(this.nodesToClean, function (node) {
		ko.cleanNode(node);
	});
	this.vm.dispose();
};

Template.type.events({
	'input [contenteditable=true]': function (ev, tmpl) {
		for (var ii = 0; ii < ev.target.childNodes.length;) {
			var node = ev.target.childNodes[ii];
			if (node.nodeType == Node.ELEMENT_NODE && !node.classList.contains('editorSpecial')) {
				while (node.firstChild) {
					ev.target.insertBefore(node.firstChild, node);
				}
				ev.target.removeChild(node);
				continue;
			}
			ii++;
		}
		ev.target.appendChild(document.createElement('br'));
	}
});
