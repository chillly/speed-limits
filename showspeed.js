// Licence: DWYWT v 1.0 See LICENCE file

// the AJaX URI head. Change this if the AJaX server moves. It gets the rest of the URI added later
var ajxuri="getspeeds.php";

var map; // the map variable that holds the map for all Leaflet work
var hull = new L.LatLng(53.775, -0.356); // the place to start displaying the map
var xhspeed; // AJaX variable

function init() {
	// ajax stuff
	xhspeed=GetXmlHttpObject();
	if (xhspeed==null) {
		alert ("This browser does not support HHTP request that the map needs");
		return;
	}
	
	// set up the map
	map = new L.Map('speedmap'); // use the div called speedmap
	
	var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC BY-SA</a>';
	var osm = new L.TileLayer(osmUrl, {minZoom: 14, maxZoom: 18, attribution: osmAttrib});		

	map.setView(hull,15); // set the map to show in Hull and zoom 14
	map.addLayer(osm); // add the base Mapnik layer from OSM
	map.speedLayer = new L.GeoJSON(); // create a new, empty, GeoJSON layer
	map.addLayer(map.speedLayer); // Add the layer for later use
	map.on('moveend', onMapMove); // If the map is moved call onMapMove()
	askForGJ(); // ask for the GeoJSON data
}

function onMapMove(e) {
	askForGJ() // if the map is moved, ask for the updated GeoJSON data
}

function askForGJ() {
	// request the GeoJSON for the map bounds
	var bounds=map.getBounds(); // get the current window the map covers
	var minll=bounds.getSouthWest(); // create W & W limits
	var maxll=bounds.getNorthEast(); // create N & E limits
	
	// build the AJaX URI to send
	var URI=ajxuri+'?bbox=' + minll.lng + ',' + minll.lat + ',' + maxll.lng + ',' + maxll.lat;
	
	// fire off an AJaX request
	// the response will be handled by stateChanged()
	xhspeed.onreadystatechange = stateChanged; 
	xhspeed.open('GET', URI, true);
	xhspeed.send(null);
}

function GetXmlHttpObject() {
	if (window.XMLHttpRequest) {
		// code for IE7+, Firefox, Chrome, Opera, Safari
		return new XMLHttpRequest();
	}
	if (window.ActiveXObject) {
		// code for IE6, IE5
		return new ActiveXObject("Microsoft.XMLHTTP");
	}
	return null;
}

function stateChanged() {
	// if AJAX returned a position, move the map there
	if (xhspeed.readyState==4) {
		//use the info here that was returned
		if (xhspeed.status==200) {
			var ret=eval("(" + xhspeed.responseText + ")");
			var geojsonFeature=ret.featlist;
			
			// clear the old layer ready for the new one
			map.speedLayer.clearLayers();
			
			// add the new features, using the embedded style
			map.speedLayer.on("featureparse", function (e) {
				// make the popup work
				if (e.properties && e.properties.popupContent) {
					e.layer.bindPopup(e.properties.popupContent);
				}
				// apply the style
				if (e.properties && e.properties.style && e.layer.setStyle) {
					e.layer.setStyle(e.properties.style);
				}
			});
		// add the newly generated data to the layer
		map.speedLayer.addGeoJSON(geojsonFeature);
		}
	}
}
