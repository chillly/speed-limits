CREATE TABLE IF NOT EXISTS road (
  roadid int(11) NOT NULL AUTO_INCREMENT,
  osmid int(11) NOT NULL,
  north double NOT NULL,
  south double NOT NULL,
  east double NOT NULL,
  west double NOT NULL,
  highway varchar(20) NOT NULL,
  maxspeed varchar(12) NOT NULL,
  PRIMARY KEY (roadid)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 ;
