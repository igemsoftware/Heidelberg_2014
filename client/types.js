'use strict';

UI.registerHelper('types', function () {
	return Types.find();
});

function TypeVM(data, textCallback) {
	var self = this;
	Type.call(this, data.type(), ko.unwrap(data.version));

	self.editMode = data.editMode;
	self.versions = self.DBData ? _.map(self.DBData.v, function (version, index) {
		return new VersionVM(version, index, Router.path('viewType', { id: self._id() }, { query: { v: index } }));
	}).reverse() : [];

	self.textCallback = textCallback;
	self.propertyToRef = ko.observable();
}
TypeVM.prototype = new Type();
TypeVM.prototype.constructor = TypeVM;

TypeVM.prototype.edit = function () {
	Router.go('viewType', { id: this._id() }, { query: { edit: 1 } });
};

TypeVM.prototype.save = function () {
	var self = this;
	self.text(self.textCallback());
	var flat = self.flatten();

	if (!self._id()) {
		Meteor.call('insertType', flat, function (error, result) {
			if (!error) {
				self._id(result);
				Router.go('viewType', { id: self._id() });
			}
		});
	} else if (!isUnchanged(flat, self.DBData)) {
		var ss = Supplies.find({ 'allTypes._id': self._id(), needsReview: { $exists: false } });
		var sCount = ss.count();
		var ps = Protocols.find({ $or: [{ 'params.type._id': self._id() }, { 'products.types._id': self._id() }], needsReview: { $exists: false } });
		var pCount = ps.count();
		if (sCount > 0 || pCount > 0) {
			var cannotUpdate = false;
			var needsMapping = false;

			var mappings = [];
			if (!isUnchanged(flat.properties, self.DBData.properties)) {
				var oldProperties = { };

				_.each(self.DBData.allProperties, function (oldProperty) {
					if (!oldProperty.from) oldProperty.from = self.toReference();
					if (!oldProperties[oldProperty.from._id]) oldProperties[oldProperty.from._id] = { };
					oldProperties[oldProperty.from._id][oldProperty.name] = oldProperty;
				});

				_.each(self.allProperties(), function (property) {
					if (property.required() && self.DBData.allProperties.length == 0) {
						cannotUpdate = true;
					} else {
						var oldProperty = oldProperties[property.from._id()] && oldProperties[property.from._id()][property.name()];
						var obj = {
							property: property,
							possibleMappings: self.DBData.allProperties,
							source: ko.observable(oldProperty),
						};
						obj.blank = ko.observable(!property.required() && !obj.source.peek());
						mappings.push(obj);
						if (!oldProperty) needsMapping = true;
					}
				});
			}

			if (cannotUpdate) {
				self.cannotCascadeModalVM({
					sCount: sCount,
					pCount: pCount,
					confirm: ko.observable(false),
					save: function () {
						if (this.confirm()) {
							Meteor.call('updateTypeWithoutCascade', self._id(), flat);
						}
						$('#cannotCascadeModal').modal().on('hidden.bs.modal', function () {
							Router.go('viewType', { id: self._id() });
						}).modal('hide');
						return true;
					}
				});
				$('#cannotCascadeModal').modal();
			} else if (needsMapping) {
				self.mappingsModalVM({
					sCount: sCount,
					pCount: pCount,
					mappings: mappings,
					save: function () {
						flat.versionMappings = [];
						_.each(mappings, function (mapping) {
							if (!mapping.blank()) {
								flat.versionMappings.push({
									property: mapping.property.toReference(),
									source: {
										from: mapping.source().from,
										name: mapping.source().name
									}
								});
							}
						});

						Meteor.call('updateType', self._id(), flat, function (error, result) {
							console.log(error, result);
						});
						$('#mappingsModal').on('hidden.bs.modal', function () {
							Router.go('viewType', { id: self._id() });
						}).modal('hide');
						return true;
					}
				});
				$('#mappingsModal').modal();
			} else {
				Meteor.call('updateType', self._id(), flat, function (error, result) {
					console.log(error, result);
				});
				Router.go('viewType', { id: self._id() });
			}
		} else {
			Meteor.call('updateTypeWithoutCascade', self._id(), flat);
			Router.go('viewType', { id: self._id() });
		}
	} else {
		Router.go('viewType', { id: self._id() });
	}
};

TypeVM.prototype.cancel = function () {
	if (this._id()) {
		Router.go('viewType', { id: this._id() });
	} else {
		Router.go('typeList');
	}
};

TypeVM.prototype.displayVersions = function () {
	$("#versionModal").modal();
};

function createRefBlock(vm) {
	var block = document.createElement('span');
	block.setAttribute('contenteditable', 'false');
	block.className = 'editorSpecial editorReference';
	block.setAttribute('data-bind', 'text: name');
	ko.applyBindings(vm, block);
	return block;
}

Template.type.rendered = function () {
	var self = this;

	var editor = self.find('#textEditor');
	function textCallback() {
		var text = [];
		_.each(editor.childNodes, function (child) {
			switch (child.nodeType) {
				case Node.ELEMENT_NODE:
					if (child.classList.contains('editorReference')) {
						var data = ko.dataFor(child);
						text.push({
							type: 'propertyReference',
							property: ko.dataFor(child).toReference(),
						});
					}
					break;
				case Node.TEXT_NODE:
					if (child.nodeValue) text.push({ type: 'text', text: child.nodeValue })
					break;
			}
		});
		return text;
	};

	var cannotCascadeModalVM = ko.observable();
	var mappingsModalVM = ko.observable();
	self.vm = ko.computed(function () {
		var vm = new TypeVM(self.data, textCallback);
		vm.cannotCascadeModalVM = cannotCascadeModalVM;
		vm.mappingsModalVM = mappingsModalVM;
		return vm;
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

		self.updateEditor = ko.computed(function () {
			while (editor.firstChild) {
				editor.removeChild(editor.firstChild);
			}

			if (self.data.type()) {
				_.each(self.data.type().text, function (part) {
					switch (part.type) {
						case 'text':
							editor.appendChild(document.createTextNode(part.text));
							break;
						case 'propertyReference':
							var block = createRefBlock(_.find(self.vm().allProperties.peek(), function (property) {
								return property.name.peek() == part.property.name;
							}));
							editor.appendChild(block);
							self.nodesToClean.push(block);
							break;
					}
				});
			}
			editor.appendChild(document.createElement('br'));
		});
	}, 0);
};

Template.type.destroyed = function () {
	_.each(this.nodesToClean, function (node) {
		ko.cleanNode(node);
	});
	this.updateEditor.dispose();
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
	},
	'click #addRef': function (ev, tmpl) {
		var sel = window.getSelection();
		var ranges = [];
		var textEditor = tmpl.find('#textEditor');
		for (var ii = 0; ii < sel.rangeCount; ii++) {
			var range = sel.getRangeAt(ii);
			if (textEditor.contains(range.commonAncestorContainer)) {
				range.deleteContents();

				var block = createRefBlock(tmpl.vm().propertyToRef());
				range.insertNode(block);
				tmpl.nodesToClean.push(block);

				range = document.createRange();
				range.setStartAfter(block);
				range.collapse(true);
				ranges.push(range);

				textEditor.focus();
			} else {
				ranges.push(range);
			}
		}

		sel.removeAllRanges();
		_.each(ranges, function (range) {
			sel.addRange(range);
		})
	}
});
