'use strict';

UI.registerHelper('types', function () {
	return Types.find();
});

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
						text.push({
							type: 'propertyReference',
							property: ko.toJS(_.pick(ko.dataFor(child), 'name', 'from'))
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
		var vm = new typeVM(self.data, textCallback);
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
