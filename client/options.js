'use strict';

UI.registerHelper('getOption', function (option) {
	var result = Options.findOne({ key: option}, {fields: { value: 1}});
	return result && result.value;;
});

UI.registerHelper('formatDate', function (date) {
	var format = Options.findOne({ key: 'timeFormat'}, {fields: { value: 1}});
	format = format && format.value;
	return moment(date).format(format);
});

Template.options.events({
	'click #savebtn': function() {
		Meteor.call('updateOptions', 'timeFormat', $('#timeFormat').val())
		alert("Saved!");
	}
});

