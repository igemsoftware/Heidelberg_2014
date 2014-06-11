'use strict';

UI.registerHelper('types', function () {
	return Types.find();
});

function newTypeVM(textEditor) {
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

newTypeVM.prototype.types = ko.meteor.find(Types, { });

newTypeVM.prototype.addProperty = function () {
	this.properties.push(new newTypePropertyVM());
};

newTypeVM.prototype.removeProperty = function (property) {
	this.properties.remove(property);
};

newTypeVM.prototype.addRef = function () {
	var sel = window.getSelection();
	var ranges = [];
	for (var ii = 0; ii < sel.rangeCount; ii++) {
		var range = sel.getRangeAt(ii);
		if (this.textEditor.contains(range.commonAncestorContainer)) {
			range.deleteContents();

			var block = document.createElement('span');
			block.setAttribute('contenteditable', 'false');
			block.className = 'editorSpecial editorReference';
			block.setAttribute('data-bind', 'text: name');
			range.insertNode(block);
			console.log(this.propertyToRef());
			ko.applyBindings(this.propertyToRef(), block);

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

newTypeVM.prototype.save = function () {
	Types.insert(this.flatten());
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
	this.vm = new newTypeVM(this.find('#textEditor'));

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

Template.newType.events({
	'input [contenteditable=true]': function (ev, tmpl) {
		//tmpl.vm.text.removeAll();
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
