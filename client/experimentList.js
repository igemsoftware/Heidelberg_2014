'use strict';

UI.registerHelper('experiments', function () {
	return Experiments.find({ }, { sort: { finishDate: -1 } });
});

Template.experimentList.products = function () {
	return _.values(this.products);
}

Template.experimentList.protocol = function () {
	return Protocols.findOne(this.protocol._id);
}

Template.experimentList.productText = function (experiment) {
	var texts = [];
	var version = experiment.v[experiment.v.length - 1];
	_.each(version.products[CryptoJS.MD5(this.name).toString()], function (productType) {
		if (productType.text) texts.push(productType.text);
	});
	return texts.join('/');
}
