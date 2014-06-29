'use strict';

UI.registerHelper('getOption', function (option) {
	var result = Options.findOne({ key: option}, {fields: { value: 1}});
	return result && result.value;;
});

UI.registerHelper('formatDate', function (date, relative) {
	var format = Options.findOne({ key: 'timeFormat'}, {fields: { value: 1}});
	relative = (typeof relative === "undefined") ? false : relative;
	format = format && format.value;
	if(moment(date).isAfter(moment().subtract(1, 'day')) && relative){
		return moment(date).fromNow();
	}
	return moment(date).format(format);
});

Template.options.events({
	'click #savebtn': function() {
		Meteor.call('updateOptions', 'timeFormat', $('#timeFormat').val())
		alert("Saved!");
	}
});

