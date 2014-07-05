'use strict';

Template.masterTemplate.events({
	'click #loginNag': function (ev, tmpl) {
		setTimeout(function () {
			$('#login-dropdown-list').addClass('open');
		}, 0);
	}
});

Template.navItems.helpers({
	activeIfInPath: function (path) {
		var currentRoute = Router.current();
		return currentRoute && (currentRoute.path.indexOf(path) == 0) ? 'active' : '';
	}
});

Accounts.ui.config({passwordSignupFields: 'USERNAME_AND_EMAIL'});

Meteor.subscribe('Everything');
