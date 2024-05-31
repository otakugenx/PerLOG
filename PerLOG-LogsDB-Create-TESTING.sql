-- Create syntax for 'logs'

CREATE TABLE `logs` (
  `entryid` int(11) NOT NULL auto_increment,
  `timestamp` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `remoteip` char(16) default NULL,
  `alert` char(1) default 'n',
  `givenhostname` char(250) NULL,
  `givendate` char(6) NULL,
  `giventime` time NULL,
  `facility` int(3) NULL,
  `severity` int(2) NULL,
  `program` char(250) NULL default 'Program Name Not Given',
  `message` mediumtext NULL,
  PRIMARY KEY  (`entryid`)
  FULLTEXT (`message`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COMMENT='latin1_swedish_ci';
