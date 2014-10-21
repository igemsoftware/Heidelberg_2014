'use strict';

// Internal, private KO utility for updating model properties from within bindings
// property:            If the property being updated is (or might be) an observable, pass it here
//                      If it turns out to be a writable observable, it will be written to directly
// allBindings:         An object with a get method to retrieve bindings in the current execution context.
//                      This will be searched for a '_ko_property_writers' property in case you're writing to a non-observable
// key:                 The key identifying the property to be written. Example: for { hasFocus: myValue }, write to 'myValue' by specifying the key 'hasFocus'
// value:               The value to be written
// checkIfDifferent:    If true, and if the property being written is a writable observable, the value will only be written if
//                      it is !== existing value on that writable observable
ko.expressionRewriting.writeValueToProperty = function(property, allBindings, key, value, checkIfDifferent) {
	if (!property || !ko.isObservable(property)) {
		var propWriters = allBindings.get('_ko_property_writers');
		if (propWriters && propWriters[key])
			propWriters[key](value);
	} else if (ko.isWriteableObservable(property) && (!checkIfDifferent || property.peek() !== value)) {
		property(value);
	}
}
