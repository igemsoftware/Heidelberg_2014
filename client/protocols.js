'use strict';

UI.registerHelper('protocols', function () {
	return Protocols.find();
});

Session.setDefault('newProtocolDeps', []);
Session.setDefault('newProtocolResults', []);

Template.newProtocol.deps = function () {
	return Session.get('newProtocolDeps');
};

Template.newProtocol.results = function () {
	return Session.get('newProtocolResults');
};

Template.newProtocol.events({
	'click #addDependency': function () {
		var deps = Session.get('newProtocolDeps');
		deps.push({});
		Session.set('newProtocolDeps', deps);
	},
	'click #addResult': function () {
		var results = Session.get('newProtocolResults');
		results.push({});
		Session.set('newProtocolResults', results);
	},
	'click button#addTextInput': function (ev) {
		var sel = window.getSelection();
		if (!sel) return false;

		var steps = document.getElementById('protocolSteps');
		if (!steps.contains(sel.anchorNode)) return false;

		var focus = sel.focusNode;
		var focusOffset = sel.focusOffset;

		sel.deleteFromDocument();

		var input = document.createElement('input');
		switch (focus.nodeType) {
			case Node.ELEMENT_NODE:
				if (focus.childNodes.length > focusOffset) {
					focus.insertBefore(input, focus.childNodes[focusOffset]);
				} else {
					focus.appendChild(input);
				}
				break;
			case Node.TEXT_NODE:
				var txt = document.createTextNode(focus.nodeValue.substr(focusOffset));
				focus.nodeValue = focus.nodeValue.substr(0, focusOffset);
				focus.parentNode.insertBefore(txt, focus.nextSibling);
				focus.parentNode.insertBefore(input, txt);
				break;
			default:
				// Should not happen
		}

		sel.removeAllRanges();
		var range = document.createRange();
		range.setStartAfter(input);
		range.setEndAfter(input);
		sel.addRange(range);
		steps.focus();
	},
	'input ol#protocolSteps': function (ev) {
		ev.preventDefault();
		var steps = document.getElementById('protocolSteps');
		if (!steps.hasChildNodes()) {
			var emptyLi = document.createElement('li');
			document.getElementById('protocolSteps').appendChild(emptyLi);

			// Set the focus inside the <li />
			var sel = window.getSelection();
			sel.removeAllRanges();
			var range = document.createRange();
			range.selectNodeContents(emptyLi);
			sel.addRange(range);
		} else if (steps.childNodes.length == 1
		           && steps.childNodes[0].childNodes.length == 1
		           && steps.childNodes[0].childNodes[0].nodeName.toLowerCase() == 'br'
		           && steps.childNodes[0].childNodes[0].getAttribute('type') == '_moz') {
			// Firefox bug inserts <br />s before ol; delete them
			$('#protocolStepsWrapper > br').remove();
		}
	},
	'click button#submitProtocol': function () {
		var steps = document.getElementById('protocolSteps');
		Protocols.insert({
			name: $('#protocolName').text(),
			steps: _.map(steps.childNodes, function (li) {
				return _.reduce(li.childNodes, function (memo, node) {
					switch (node.nodeName.toLowerCase()) {
						case '#text':
							if (node.nodeValue != '') memo.push({ type: 'text', text: node.nodeValue });
							break;
						case 'br':
							// Firefox inserts a <br type="moz" /> at the end; ignore it
							if (node.getAttribute('type') != '_moz') memo.push({ type: 'br' });
							break;
						case 'input':
							memo.push({ type: 'input' });
							break;
						default:
							// Should not happen
							console.log('ERROR: cannot handle node', node);
					}
					return memo;
				}, []);
			})
		});
	}
});
