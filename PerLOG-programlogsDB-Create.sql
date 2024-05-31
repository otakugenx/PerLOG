-- Create syntax for 'programlog'

CREATE TABLE `programlog` (
  `entryid` int(11) NOT NULL auto_increment,
  `timestamp` timestamp NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `event` varchar(250) NULL default '',
  PRIMARY KEY  (`entryid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1 COMMENT='latin1_swedish_ci';
