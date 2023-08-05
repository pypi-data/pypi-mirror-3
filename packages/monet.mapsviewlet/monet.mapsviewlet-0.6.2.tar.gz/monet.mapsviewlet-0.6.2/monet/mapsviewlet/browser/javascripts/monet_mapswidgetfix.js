/**
 * Google Map Viewlet bugfix for Products.Maps widget 
 * See http://plone.org/products/maps/issues/35/
 */

jq(document).ready(function() {
	
	var fieldset = jq('.formTab #fieldsetlegend-geolocation');
	var handler = function(event) {
		jq('.googleMapPane').css('width','100%').css('height', '');
		fieldset.unbind('click', handler);
	}
	if (fieldset.length==1) {
		fieldset.click(handler);
	}

});

