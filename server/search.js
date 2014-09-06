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
	var result = HTTP.post('http://localhost:9200/md_devel/' + type + '/_search', {
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
		/*
		if (!query) return;
		var future = new Future();
		MongoInternals.defaultRemoteCollectionDriver().mongo.db.command({
			text: Supplies._name,
			search: query,
			project: {
				_id: 1 // Only take the ids
			}
		}, function(error, resultsDoc) {
			if (error) throw error;
			if (resultsDoc.ok === 1) {
				future.return(_.map(resultsDoc.results, function (result) {
					return result.obj._id;
				}));
			} else {
				future.return([]);
			}
		});
		return future.wait();
		*/

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
								'allTypes._id': typeId
							},
						},
					},
				},
			},
		}), '_id');
	},
	searchExperiments: function (query, protocolIds) {
		return _.map(search('experiment-products', query, {
			terms: {
				'protocol_id': protocolIds
			},
		}), function (experimentProduct) {
			return {
				experiment_id: experimentProduct._source.experiment_id,
				productMD5: experimentProduct._source.productMD5,
				texts: experimentProduct._source.texts,
			};
		});
	},
});
