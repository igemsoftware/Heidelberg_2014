'use strict';

UI.registerHelper('getOption', function (option) {
	return getUserOption(option);
});

UI.registerHelper('formatDate', function (date, relative) {
	return formatDate(date, relative);
});

Template.options.events({
	'click #savebtn': function() {
		Meteor.call('updateOption', 'dateFormat', $('#dateFormat').val())
		alert("Saved!");
	}
});

