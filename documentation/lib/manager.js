OMManager = function () {
	this.types = { };
	this.supplies = { };
	this.protocols = { };
	this.experiments = { };
};
OMManager.prototype.constructor = OMManager;

OMManager.prototype.getType = function (id, version, data) {
	var newVersion = version === undefined ? '' : version;
	if (!this.types[id]) this.types[id] = { };
	if (!this.types[id][newVersion]) {
		this.types[id][newVersion] = new Type(this, data || Types.findOne(id), version);
	}
	return this.types[id][newVersion];
};

OMManager.prototype.getSupply = function (id, version, data, tryUpdate) {
	var newVersion = (tryUpdate || version === undefined) ? '' : version;
	if (!this.supplies[id]) this.supplies[id] = { };
	if (!this.supplies[id][newVersion] || tryUpdate) {
		this.supplies[id][newVersion] = new Supply(this, data || Supplies.findOne(id), version, tryUpdate);
	}
	return this.supplies[id][newVersion];
};

OMManager.prototype.getProtocol = function (id, version, data, tryUpdate) {
	var newVersion = (tryUpdate || version === undefined) ? '' : version;
	if (!this.protocols[id]) this.protocols[id] = { };
	if (!this.protocols[id][newVersion]) {
		this.protocols[id][newVersion] = new Protocol(this, data || Protocols.findOne(id), version, tryUpdate);
	}
	return this.protocols[id][newVersion];
};

OMManager.prototype.getExperiment = function (id, version, data, tryUpdate) {
	var newVersion = (tryUpdate || version === undefined) ? '' : version;
	if (!this.experiments[id]) this.experiments[id] = { };
	if (!this.experiments[id][newVersion]) {
		this.experiments[id][newVersion] = new Experiment(this, { experiment: data || Experiments.findOne(id) }, version, tryUpdate);
	}
	return this.experiments[id][newVersion];
};
