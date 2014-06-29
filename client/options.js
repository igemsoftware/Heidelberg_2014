'use strict';

UI.registerHelper('getOption', function (option) {
	var result = Options.findOne({ key: option}, {fields: { value: 1}});
	return result && result.value;;
});

UI.registerHelper('formatDate', function (date, relative) {
	return formatDate(date, relative);
});

Template.options.events({
	'click #savebtn': function() {
		Meteor.call('updateOptions', 'timeFormat', $('#timeFormat').val())
		alert("Saved!");
	}
});

