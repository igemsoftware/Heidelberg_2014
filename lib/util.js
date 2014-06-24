isUnchanged = function (newVersion, oldVersion) {
	return _.all(_.map(newVersion, function (value, key) {
		if (key == 'mtime' || key == 'changeType') return true;
		if (value === undefined || value === null) {
			return oldVersion[key] === undefined || oldVersion[key] === null;
		} else if (oldVersion[key] === undefined || oldVersion[key] === null) {
			return false;
		}

		if (value instanceof Array) {
			return oldVersion[key] instanceof Array && value.length == oldVersion[key].length && _.all(_.map(value, function (aValue, idx) {
				return isUnchanged(aValue, oldVersion[key][idx]);
			}));
		}

		if (value instanceof Date) {
			return oldVersion[key] instanceof Date && value.getTime() == oldVersion[key].getTime();
		}

		if (value instanceof Object) {
			return oldVersion[key] instanceof Object && isUnchanged(value, oldVersion[key]);
		}

		return value === oldVersion[key];
	}));
};
