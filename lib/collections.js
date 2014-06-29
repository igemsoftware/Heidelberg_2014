Types = new Meteor.Collection('types');
Supplies = new Meteor.Collection('supplies');
Protocols = new Meteor.Collection('protocols');
Experiments = new Meteor.Collection('experiments');
Options = new Meteor.Collection('options');

Meteor.publish('Everything', function() {
	if(this.userId){
		return [Types.find(), Supplies.find(), Protocols.find(), Experiments.find(), Options.find()];
	}
})