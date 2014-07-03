VersionVM = function(version, index, href) {
	var self = this;
	self.version = version;
	self.versionNr = index;
	self.href = href;
};

VersionVM.prototype.isCurrent = function (currentVersionNr) {
	return this.versionNr == currentVersionNr;
};

VersionVM.prototype.hideModal = function() {
	$("#versionsModal").modal('hide');
	return true; // Allow standard event handler for href
};
