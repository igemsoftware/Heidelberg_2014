ko.bindingHandlers.datepicker = {
	init: function (element, valueAccessor, allBindings) {
		var modelValue = valueAccessor();
		var options = { };
		if (typeof modelValue == 'object') {
			_.extend(options, modelValue.options);
			modelValue = modelValue.date;
		}

		$(element).datepicker(options).on('change', function (ev) {
			var newDate = new Date(ev.target.value);
			var currentDate = new Date(modelValue());
			newDate.setHours(currentDate.getHours());
			newDate.setMinutes(currentDate.getMinutes());
			newDate.setSeconds(currentDate.getSeconds());
			if (!isNaN(newDate.getHours())) {
				modelValue(newDate);
			} else {
				modelValue(currentDate);
			}
		});
	},
	update: function (element, valueAccessor, allBindingsAccessor) {
		var modelValue = valueAccessor();
		if (typeof modelValue == 'object') modelValue = modelValue.date;
		$(element).datepicker('setDate', modelValue());
	}
};

ko.bindingHandlers.clockpicker = {
	init: function (element, valueAccessor, allBindings) {
		var modelValue = valueAccessor();
		var options = { placement: 'top' };
		if (typeof modelValue == 'object') {
			_.extend(options, modelValue.options);
			modelValue = modelValue.date;
		}

		$(element).clockpicker(options).find('.form-control').on('change', function (ev) {
			var currentDate = new Date(modelValue()) || new Date();
			var parts = ev.target.value.split(':');
			var newDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate(), parseInt(parts[0]), parseInt(parts[1]));
			if (!isNaN(newDate.getHours())) {
				modelValue(newDate);
			} else {
				modelValue(currentDate);
			}
		});
	},
	update: function (element, valueAccessor, allBindingsAccessor) {
		var modelValue = valueAccessor();
		if (typeof modelValue == 'object') modelValue = modelValue.date;
		var date = modelValue();

		$(element).find('.form-control').val(('0' + date.getHours()).slice(-2) + ':' + ('0' + date.getMinutes()).slice(-2));
	}
};
