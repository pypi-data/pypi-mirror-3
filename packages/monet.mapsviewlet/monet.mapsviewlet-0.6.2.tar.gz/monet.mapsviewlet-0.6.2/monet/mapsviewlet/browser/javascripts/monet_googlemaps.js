/**
 * Google Map Viewlet support for Plone
 */

// Yes... global for now. This way I can quick fix the Products.Maps.widget bug
// See also http://plone.org/products/maps/issues/35/
var monetmap = null;

jq(document).ready(function() {
	
	var geocoder = null;
	var marker;
	
	var geocoder;
	
	var geoXml = [];
	var markers = [];
	
	/**
	 * 
	 * @param {String} The address to point the map onto
	 * @param {String} The content of the baloon
	 * @param {Bool} reverse If True, don't show the "content" parameter directly but reverse-geocode it before
	 */
	var showAddress = function(address, content, reverse) {
		geocoder.getLatLng(address, function(point){
			if (!point) {
				alert(address + " not found");
			}
			else {
				monetmap.setCenter(point, parseInt(document.getElementById('gmaps-zoom-level').innerHTML));
				var marker = new GMarker(point);
				monetmap.addOverlay(marker);
				monetmap.enableScrollWheelZoom();
				if (content && !reverse) {
					marker.openInfoWindowHtml(content);
				} else if (content && reverse) {
					geocoder.getLocations(content, function(response) {
						if (response && response.Status.code==200) {
							var place = response.Placemark[0];
							marker.openInfoWindowHtml(place.address);
						}
					});
				} else if (content == '') {
					// nop
				} else {
					marker.openInfoWindowHtml(address);
				}
			}
		});
	}
	
	var loadGM = function() {
		if (window.GBrowserIsCompatible && GBrowserIsCompatible()) {
			monetmap = new GMap2(document.getElementById("googlemaps"));
				
			// Use Small instead of Large for detailed zoom
			//monetmap.addControl(new GSmallMapControl());
			monetmap.addControl(new GLargeMapControl());
			monetmap.addControl(new GScaleControl());
			// kind of map
			monetmap.addControl(new GMapTypeControl());
			// show overview area map
			//monetmap.addControl(new GOverviewMapControl());
	
			geocoder = new GClientGeocoder();
			
			var addr = document.getElementById("gmaps-location").innerHTML;
			var officialLocation = document.getElementById("gmaps-official-location").innerHTML;
			var locationType = document.getElementById("gmaps-popup-type").innerHTML;
			if (locationType=='location' && officialLocation) {
				showAddress(addr, officialLocation);
			} else if (locationType=='location' && !officialLocation) {
				showAddress(addr, addr, true);				
			} else if (locationType=='text') {
				var markerText = document.getElementById('gmaps-popup-text').value;
				showAddress(addr, markerText);
			} 
			
			// BBB: very very very ugly, but IE seems to have some bad, non-predictable bug here
			//loadKml();
			setTimeout(loadKml, 3000);
			
			// If map has been loaded, I'll hide related contents
			jq("#relatedItemBox").hide();
		}
		else {
			jq("#googlemaps").text("Seems that your browser doesn't support Google Maps.");
		}
	}	
	
	var addAddressToCenterMap = function(response) {
	   if (!response || response.Status.code != 200) {
			//alert("Sorry, we were unable to geocode that address");
		} else {
			place = response.Placemark[0];
			point = new GLatLng(place.Point.coordinates[1], place.Point.coordinates[0]);
			monetmap.setCenter(point, parseInt(document.getElementById('gmaps-zoom-level').innerHTML));
		}
	}
		   
	var loadKml = function() {
		// Center and zoom on the map
		// geocoder.getLocations(addr, addAddressToCenterMap);
		
		var kmls = jq("span.kmlurl");
		
		for (var i=0;i<kmls.length;i++) {
			geoXml.push(kmls[i].innerHTML);
			ngeo = new GGeoXml(geoXml[i]);
			markers.push(ngeo);
			monetmap.addOverlay(ngeo);
		}
	}
	
	/**
	 * Enable/disable a overlay on the map.
	 * Overlays are all saved in the "markers" array.
	 * @param {CheckBox} check The checkbox that trigger the event.
	 * @param {Integer} id index of the overlay.
	 */
	jq(".kmlTrigger").each(function() {
		jq(this).click(function(event) {
			var $this = jq(this);
			var this_checked = $this.attr("checked");
			var id = $this.attr('id').substr(4);
			if (this_checked) {
				monetmap.addOverlay(markers[id]);
			}
			else {
				monetmap.removeOverlay(markers[id]);
			}
		});
	});
	
	registerEventListener(window, 'unload', GUnload);
	loadGM();
});

