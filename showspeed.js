// the AJaX URI head. Change this if the AJaX server moves. It gets the rest of the URI added later
var ajxuri="getspeeds.php";

var map;
var hull = new L.LatLng(53.775, -0.356);
var xhspeed;

function init() {
	// ajax stuff
	xhspeed=GetXmlHttpObject();
	if (xhspeed==null) {
		alert ("This browser does not support HHTP request that the map needs");
		return;
	}
	
	// set up the map
	map = new L.Map('speedmap');
	
	var osmUrl='http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC BY-SA</a>';
	var osm = new L.TileLayer(osmUrl, {minZoom: 8, maxZoom: 18, attribution: osmAttrib});		
	
	//cen = new L.LatLng(lat,lng);
	//map.scrollWheelZoom.disable();
	map.setView(hull,14);
	map.addLayer(osm);
	map.speedLayer = new L.GeoJSON();
	map.addLayer(map.speedLayer);
	map.on('moveend', onMapMove);
	askForGJ();
}

function onMapMove(e) {
	askForGJ()
}

function askForGJ() {
	// request the GeoJSON for the map bounds
	var bounds=map.getBounds();
	var minll=bounds.getSouthWest();
	var maxll=bounds.getNorthEast();
	var URI=ajxuri+'?bbox=' + minll.lng + ',' + minll.lat + ',' + maxll.lng + ',' + maxll.lat;
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
			
			// clear the old layer
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
		map.speedLayer.addGeoJSON(geojsonFeature);
		}
	}
}
