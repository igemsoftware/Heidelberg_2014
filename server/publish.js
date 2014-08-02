Meteor.publish('Everything', function() {
	if (this.userId) {
		return [Types.find(), Supplies.find(), Protocols.find(), Experiments.find(), Meteor.users.find({ }, { username: true })];
	}
});
