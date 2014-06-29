Meteor.methods({
	'updateType': function(id, type) {
		if(!this.userId)
			return;
		Types.update(id, type);
	},
	'insertType': function(type) {
		if(!this.userId)
			return;
		return Types.insert(type);
	}
})