'use strict';

var HTTP = Package.http.HTTP;

function search(type, query, filter) {
	if (!query) return;

	query = {
		match: {
			_all: {
				query: query,
				operator: 'and',
			},
		},
	};

	if (filter) {
		query = {
			filtered: {
				query: query,
				filter: filter
			},
		};
	}

	var result = HTTP.post(Meteor.settings.elasticIndexURL + '/' + type + '/_search', {
		data: {
			query: query,
		},
	});

	if (result.statusCode === 200) {
		return JSON.parse(result.content).hits.hits;
	} else {
		throw new Meteor.Error(result.statusCode, JSON.parse(result.content));
	}
}

Meteor.methods({
	searchSupplies: function (query, typeId) {
		return _.pluck(search('supplies', query, {
			nested: {
				path: 'allTypes',
				query: {
					filtered: {
						query: {
							match_all: { },
						},
						filter: {
							term: {
								'allTypes._id': typeId,
							},
						},
					},
				},
			},
		}), '_id');
	},
	searchExperiments: function (query, typeId) {
		return _.map(search('experiment-products', query, {
			nested: {
				path: 'allTypes',
				query: {
					filtered: {
						query: {
							match_all: { },
						},
						filter: {
							term: {
								'allTypes._id': typeId,
							},
						},
					},
				},
			},
		}), function (experimentProduct) {
			return {
				experiment_id: experimentProduct._source.experiment_id,
				productMD5: experimentProduct._source.productMD5,
			};
		});
	},
});
