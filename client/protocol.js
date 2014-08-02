'use strict';

function ProtocolVM(data) {
	var self = this;
	self.editMode = data.editMode;
	Protocol.call(this, data.protocol(), ko.unwrap(data.version), self.editMode());

	self.versions = self.DBData && _.map(self.DBData.v, function (version, index) {
		return new VersionVM(version, index, Router.path('viewProtocol', { id: self._id() }, { query: { v: index } }));
	}).reverse();

	self.multiParams = ko.computed(function () {
		return _.filter(self.params(), function (param) {
			return param.multi();
		});
	});

	self.performHref = Router.path('performProtocol', { id: self._id() });
}
ProtocolVM.prototype = new Protocol();
ProtocolVM.prototype.constructor = ProtocolVM;

ProtocolVM.prototype.edit = function () {
	Router.go('viewProtocol', { id: this._id() }, { query: { edit: 1 } });
};

ProtocolVM.prototype.save = function () {
	var self = this;
	var flat;
	try {
		flat = self.flatten();
	} catch (e) {
		// The result being thrown as an exception signals a failed cascading update, but this doesn't matter here
		// Check if the exception really is the result first
		if (e instanceof Error) throw e;
		flat = e;
	}

	if (!self._id()) {
		Meteor.call('insertProtocol', flat, function (error, result) {
			if (!error) {
				self._id(result);
				Router.go('viewProtocol', { id: self._id() });
			}
		});
	} else if (!isUnchanged(flat, self.DBData)) {
		var xs = Experiments.find({ 'protocol._id': self._id(), 'protocol.v': self.DBData.v.length - 1 });
		var xCount = xs.count();
		if (xCount > 0) {
			var cannotUpdate = false;
			var needsMapping = false;

			var paramMappings = [];
			if (!isUnchanged(flat.params, self.DBData.params)) {
				var oldParams = { };
				var oldParamsByType = { };
				_.each(self.DBData.params, function (oldParam) {
					oldParam = _.clone(oldParam);
					oldParam.allTypes = _.pluck(Types.findOne(oldParam.type._id).allBaseTypes, '_id');
					oldParam.allTypes.push(oldParam.type._id);
					oldParam.allTypesMap = { };

					_.each(oldParam.allTypes, function (typeId) {
						oldParam.allTypesMap[typeId] = 1;
						if (!oldParamsByType[typeId]) oldParamsByType[typeId] = { 0: [], 1: [] };
						oldParamsByType[typeId][oldParam.multi ? 1 : 0].push(oldParam);
					});
					oldParams[oldParam.name] = oldParam;
				});

				_.each(self.params(), function (param) {
					var oldParam = oldParams[param.name()];
					var typeMatchingOldParams = _.clone(oldParamsByType[param.type()._id()]) || { 0: [], 1: [] };
					_.each(param.type().allBaseTypes(), function (type) {
						if (oldParamsByType[type._id()]) {
							Array.prototype.push.apply(typeMatchingOldParams[0], oldParamsByType[type._id()][0]);
							Array.prototype.push.apply(typeMatchingOldParams[1], oldParamsByType[type._id()][1]);
						}
					});

					if (!typeMatchingOldParams[0] && !param.multi()) {
						cannotUpdate = true;
					} else {
						var obj = {
							param: param,
							possibleMappings: typeMatchingOldParams[param.multi() ? 1 : 0] || [],
						};
						obj.source = ko.observable(_.contains(obj.possibleMappings, oldParam) && oldParam);
						obj.blank = ko.observable(param.multi() && !obj.source.peek());
						paramMappings.push(obj);
						if (!param.multi() && (!oldParam || !oldParam.allTypesMap[param.type()._id()] || !oldParam.allTypesMap[param.type()._id()][0])) needsMapping = true;
					}
				});
			}

			var inputMappings = [];
			if (!isUnchanged(flat.steps, self.DBData.steps)) {
				var oldInputs = { };
				var oldInputsByDesc = { };
				var oldInputsByType = { };

				_.each(self.DBData.steps, function (oldStep, oldStepIdx) {
					oldInputs[oldStep.desc] = { };
					_.each(oldStep.inputs, function (oldInput, oldInputIdx) {
						oldInput = _.clone(oldInput);
						oldInput.stepIdx = oldStepIdx;
						oldInput.inputIdx = oldInputIdx;
						oldInput.longDesc = oldInput.desc + ' of step "' + oldStep.desc + '"';
						oldInputs[oldStep.desc][oldInput.desc] = oldInput;
						if (!oldInputsByDesc[oldInput.desc]) oldInputsByDesc[oldInput.desc] = { };
						oldInputsByDesc[oldInput.desc][oldStepIdx] = oldInput;
						if (!oldInputsByType[oldInput.type]) oldInputsByType[oldInput.type] = [];
						oldInputsByType[oldInput.type].push(oldInput);
					});
				});

				_.each(self.steps(), function (step, stepIdx) {
					_.each(step.inputs(), function (input, inputIdx) {
						var oldInput = oldInputs[step.desc()] && oldInputs[step.desc()][input.desc()];
						if (input.required() && !oldInputsByType[input.type().id]) {
							cannotUpdate = true;
						} else {
							var obj = {
								stepIdx: stepIdx,
								step: step,
								inputIdx: inputIdx,
								input: input,
								possibleMappings: oldInputsByType[input.type().id] || [],
								source: ko.observable(oldInput || (oldInputsByDesc[input.desc()] && oldInputsByDesc[input.desc()][stepIdx])),
							};
							obj.blank = ko.observable(!input.required() && !obj.source.peek());
							inputMappings.push(obj);
							if (!oldInput || oldInput.type != input.type().id) needsMapping = true;
						}
					});
				});
			}

			if (cannotUpdate) {
				self.cannotCascadeModalVM({
					protocol: self,
					xCount: xCount,
					save: function () {
						Meteor.call('updateProtocol', self._id(), flat, self.DBData.v.length - 1);
						$('#cannotCascadeModal').on('hidden.bs.modal', function () {
							Router.go('viewProtocol', { id: self._id() });
						});
					}
				});
				$('#cannotCascadeModal').modal();
			} else if (needsMapping) {
				self.mappingsModalVM({
					protocol: self,
					xCount: xCount,
					cascade: ko.observable(true),
					paramMappings: paramMappings,
					inputMappings: inputMappings,
					save: function () {
						if (this.cascade()) {
							var flatParamMappings = [];
							_.each(paramMappings, function (paramMapping) {
								if (!paramMapping.blank()) flatParamMappings.push({ param: paramMapping.param.name(), source: paramMapping.source().name });
							});

							var inputMappingsMap = { };
							_.each(inputMappings, function (inputMapping) {
								if (!inputMapping.blank()) {
									if (!inputMappingsMap[inputMapping.stepIdx]) inputMappingsMap[inputMapping.stepIdx] = { };
									inputMappingsMap[inputMapping.stepIdx][inputMapping.inputIdx] = { step: inputMapping.source().stepIdx, input: inputMapping.source().inputIdx };
								}
							});

							flat.versionMappings = {
								params: flatParamMappings,
								inputs: inputMappingsMap,
							};
							Meteor.call('updateProtocol', self._id(), flat, self.DBData.v.length - 1);
						} else {
							Meteor.call('updateProtocol', self._id(), flat, self.DBData.v.length - 1);
						}
						$('#mappingsModal').on('hidden.bs.modal', function () {
							Router.go('viewProtocol', { id: self._id() });
						});
					}
				});
				$('#mappingsModal').modal();
			} else {
				Meteor.call('updateProtocol', self._id(), flat, self.DBData.v.length - 1);
				Router.go('viewProtocol', { id: self._id() });
			}
		} else {
			Meteor.call('updateProtocol', self._id(), flat, self.DBData.v.length - 1);
			Router.go('viewProtocol', { id: self._id() });
		}
	} else {
		Router.go('viewProtocol', { id: self._id() });
	}
};

ProtocolVM.prototype.cancel = function () {
	if (this._id()) {
		Router.go('viewProtocol', { id: this._id() });
	} else {
		Router.go('protocolList');
	}
};

ProtocolVM.prototype.displayVersions = function() {
	$("#versionModal").modal();
};

Template.protocol.rendered = function () {
	var self = this;
	var cannotCascadeModalVM = ko.observable();
	var mappingsModalVM = ko.observable();
	self.vm = ko.computed(function () {
		var vm = new ProtocolVM(self.data);
		vm.cannotCascadeModalVM = cannotCascadeModalVM;
		vm.mappingsModalVM = mappingsModalVM;
		return vm;
	});

	self.nodesToClean = [];
	setTimeout(function () {
		for (var node = self.firstNode; node; node = node.nextSibling) {
			// apply bindings to each direct child element of the template
			// this does not apply to comments, i. e. containerless binding syntax!
			// to enable both, we'd need to parse the comments ourselves
			if (node.nodeType == Node.ELEMENT_NODE) {
				ko.applyBindings(self.vm, node);
				self.nodesToClean.push(node);
			}
		}
	}, 0);
};

Template.protocol.destroyed = function () {
	_.each(this.nodesToClean, function (node) {
		ko.cleanNode(node);
	});
	this.vm.dispose();
};
