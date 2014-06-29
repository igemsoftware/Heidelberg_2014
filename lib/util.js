isUnchanged = function (newVersion, oldVersion) {
	return _.all(_.map(newVersion, function (value, key) {
		if (key == 'mtime' || key == 'changeType') return true;
		if (value === undefined || value === null) {
			return oldVersion[key] === undefined || oldVersion[key] === null;
		} else if (oldVersion[key] === undefined || oldVersion[key] === null) {
			return false;
		}

		if (value instanceof Array) {
			return oldVersion[key] instanceof Array && value.length == oldVersion[key].length && _.all(_.map(value, function (aValue, idx) {
				return isUnchanged(aValue, oldVersion[key][idx]);
			}));
		}

		if (value instanceof Date) {
			return oldVersion[key] instanceof Date && value.getTime() == oldVersion[key].getTime();
		}

		if (value instanceof Object) {
			return oldVersion[key] instanceof Object && isUnchanged(value, oldVersion[key]);
		}

		return value === oldVersion[key];
	}));
};

formatDate = function (date, relative) {
	var format = getUserOption('dateFormat');
	relative = (typeof relative === "undefined") ? false : relative;
	if(moment(date).isAfter(moment().subtract(1, 'day')) && relative){
		return moment(date).fromNow();
	}
	return moment(date).format(format);
};

getUserOption = function(option){
	var user = Meteor.user();
	if(user) {
		return user.profile.options && user.profile.options[option]
	}
	return;
}

idToUser = function(userid){
	return Meteor.users.findOne({_id: userid}, {username: 1});
}

Meteor.methods({
	'updateOption': function(key, value) {
		if(!this.userId)
			return;
		var set = { };
		set['profile.options.'+key] = value;
		Meteor.users.update(this.userId, { $set: set })
	}
});