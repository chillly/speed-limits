<?php

// Licence: DWYWT v 1.0 See LICENCE file

include "include/db.php";

// check what is passed
$bbox=$_GET['bbox'];

// split the bbox into its parts
list($left,$bottom,$right,$top)=explode(",",$bbox);

//open the database and get the road
$chconn = mysql_connect($hostname, $dbuser, $dbpass) or die(mysql_error());
mysql_select_db($dbname) or die(mysql_error());
$query=sprintf("SELECT * FROM road WHERE east>='%1.7f' AND west<='%1.7f' AND north>='%1.7f' AND south<='%1.7f'",$left,$right,$bottom,$top);
$resroad = mysql_query($query);

$ret=array();

$geofeatures=array();
$geofeatures['type']="FeatureCollection";
$features=array();

// if there are no rows, that's OK, just return an empty object
while ($row=mysql_fetch_array($resroad)) {
	$feature=array();
	$feature['type']="Feature";
	$prop=array();
	$prop['osmid']=$row["osmid"];
	$pstyle=array();
	$pstyle['stroke']=true;
	if ($row["maxspeed"]=='') {
		$pstyle['color']="red";
	} else {
		$pstyle['color']="blue";
	}
	$prop['style']=$pstyle;
	if ($row["maxspeed"]=='') {
		$prop['popupContent']="Not set";
	} else {
		$prop['popupContent']=$row["maxspeed"];
	}
	$feature['properties']=$prop;
	$geom=array();
	$geom['type']="LineString";
	$roadcoords=array();
	
	// get the list of lon/lat for the current road
	$roadid=$row['roadid'];
	
	$ptsquery="SELECT * FROM roadpoints WHERE roadid='{$roadid}' ORDER BY roadpointid";
	$respts=mysql_query($ptsquery);
	while ($ptsrow=mysql_fetch_array($respts)) {
		$ll=array($ptsrow['lon'],$ptsrow['lat']);
		$roadcoords[]=$ll;
	}
	$geom['coordinates']=$roadcoords;
	$feature['geometry']=$geom;
	mysql_free_result($respts);
	
	// add this to the list of features
	$features[]=$feature;
	
}
$geofeatures['features']=$features;
$ret['featlist']=$geofeatures;

// tidy up the DB 
mysql_free_result($resroad);
mysql_close($chconn);

// encode the road array as json and return it. toads can be empty
$encoded = json_encode($ret);
exit($encoded);
?>
