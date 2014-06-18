'use strict';

UI.registerHelper('experiments', function () {
	return Experiments.find({ }, { sort: { finishDate: -1 } });
});
