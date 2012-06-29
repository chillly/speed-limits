CREATE TABLE IF NOT EXISTS roadpoints (
  roadpointid int(11) NOT NULL AUTO_INCREMENT,
  roadid int(11) NOT NULL,
  lon double NOT NULL,
  lat double NOT NULL,
  PRIMARY KEY (roadpointid),
  KEY roadid (roadid)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 ;
