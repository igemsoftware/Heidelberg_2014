PODType = function (id, name) {
	this.id = id;
	this.name = name;

	PODType.types.push(this);
	PODType.typeMap[id] = this;
};

PODType.types = [];
PODType.typeMap = { };

new PODType('text', 'Text');
new PODType('uint', 'Positive integer');
new PODType('int', 'Integer');
new PODType('ufloat', 'Positive real number');
new PODType('float', 'Real number');
new PODType('%', 'Percentage');
new PODType('bool', 'True/false');
