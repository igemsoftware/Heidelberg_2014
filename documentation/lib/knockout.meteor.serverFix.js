ko_meteor_find = function (collection, selector, options) {
	if (Meteor.isClient) {
		return ko.meteor.find(collection, selector, options);
	} else {
		return ko.mapping.fromJS(collection.find(selector, options).fetch());
	}
};