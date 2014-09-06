ko.bindingHandlers.typeahead = {
	init: function (element, valueAccessor, allBindings) {
		var modelValue = ko.unwrap(valueAccessor()) || { };

		var args = [modelValue.options || { }];
		_.each(modelValue.datasets, function (dataset) {
			var arg = { };
			_.each(dataset, function (optionValue, optionKey) {
				switch (optionKey) {
					case 'templates':
						arg.templates = { };
						_.each(optionValue, function (template, templateName) {
							template = ko.unwrap(template);
							arg.templates[templateName] = function (data) {
								setTimeout(function () {
									ko.memoization.unmemoizeDomNodeAndDescendants(element.parentNode.lastChild);
								}, 0);
								return ko.renderTemplate(template, data);
							};
						});
						break;
					case 'displayKey':
						arg.displayKey = function (obj) {
							return ko.unwrap(obj[optionValue]);
						};
						break;
					default:
						arg[optionKey] = ko.toJS(optionValue);
				}
			});
			args.push(arg);
		});

		var $element = $(element);
		if (modelValue.value) {
			$element.val(args[1].displayKey ? args[1].displayKey(ko.unwrap(modelValue.value)) : ko.unwrap(ko.unwrap(modelValue.value).value)); // TODO: find which dataset the value belongs to
		}
		$element.typeahead.apply($element, args).on('typeahead:selected typeahead:autocompleted', function (event, newValue) {
			$element.change();
			if (modelValue.value) ko.expressionRewriting.writeValueToProperty(modelValue.value, modelValue, 'value', newValue);
		});
		
		ko.utils.domNodeDisposal.addDisposeCallback(element, function () {
			setTimeout(function () {
				$element.typeahead('destroy');
			}, 0);
		});
	},
	update: function (element, valueAccessor, allBindingsAccessor) {
		// TODO!
	},
};
