cascadingUpdate = function (manager, affected, changeType, versionMappings) {
	var errors = [];

	var affectedTypes = affected.types ? affected.types() : [];
	var affectedSupplies = { };
	if (affected.supplies) _.each(affected.supplies(), function (supply) {
		affectedSupplies[supply._id] = supply;
	});
	var affectedProtocols = { };
	if (affected.protocols) _.each(affected.protocols(), function (protocol) {
		affectedProtocols[protocol._id] = protocol;
	});
	var affectedExperiments = affected.experiments ? affected.experiments() : [];

	for (var type; type = affectedTypes.shift();) {
		var obj = manager.getType(type._id, undefined, type);
		obj.tryUpdate(versionMappings);
		var flat = obj.flatten();
		if (!isUnchanged(flat, type)) {
			var moreAffected = updateType(type._id, _.extend({ changeType: changeType }, flat));
			affectedTypes.push.apply(affectedTypes, moreAffected.types());
			_.each(moreAffected.supplies(), function (supply) {
				affectedSupplies[supply._id] = supply;
			});
			if (moreAffected.protocols) _.each(affected.protocols(), function (protocol) {
				affectedProtocols[protocol._id] = protocol;
			});
		}
	}

	_.each(affectedSupplies, function (supply) {
		try {
			var obj = manager.getSupply(supply._id, undefined, supply, true);
			var flat = obj.flatten();
			if (!isUnchanged(flat, supply)) {
				affectedExperiments.push.apply(affectedExperiments, updateSupply(supply._id, _.extend({ changeType: changeType }, flat)).experiments());
			}
		} catch (e) {
			Supplies.update(supply._id, { $set: { needsReview: true } });
			errors.push(supply, { file: e.fileName, line: e.lineNumber, col: e.columnNumber, msg: e.message, stack: e.stack });
		}
	});

	_.each(affectedProtocols, function (protocol) {
		try {
			var obj = manager.getProtocol(protocol._id, undefined, protocol, true);
			var flat = obj.flatten();
			if (!isUnchanged(flat, protocol)) {
				affectedExperiments.push.apply(affectedExperiments, updateProtocol(protocol._id, _.extend({ changeType: changeType }, flat), protocol.v.length - 1).experiments());
			}
		} catch (e) {
			Protocols.update(protocol._id, { $set: { needsReview: true } });
			errors.push(protocol, { file: e.fileName, line: e.lineNumber, col: e.columnNumber, msg: e.message, stack: e.stack });
		}
	});

	for (var experiment; experiment = affectedExperiments.shift();) {
		try {
			var obj = manager.getExperiment(experiment._id, undefined, experiment, true);
			var flat = obj.flatten();
			if (!isUnchanged(flat, experiment)) {
				affectedExperiments.push.apply(affectedExperiments, updateExperiment(experiment._id, _.extend({ changeType: changeType }, flat)).experiments());
			}
		} catch (e) {
			errors.push(experiment, { file: e.fileName, line: e.lineNumber, col: e.columnNumber, msg: e.message, stack: e.stack });
		}
	}

	return errors;
};
