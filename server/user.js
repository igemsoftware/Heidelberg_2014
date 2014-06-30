defaultOptions = {
	'dateFormat': 'dd, MMM Do YYYY, HH:mm'
}
Accounts.onCreateUser(function(options, user){
	user.profile = _.extend(options.profile, {
		options: defaultOptions
	});
	return user;
});
