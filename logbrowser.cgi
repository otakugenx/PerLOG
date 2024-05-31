#!/usr/bin/perl
#	
#		PerLOG v0.71
#		Copyright 2010 Chris Brandstetter
#
#
#	Load Modules
use DBI;
use CGI;
use CGI::Carp 'fatalsToBrowser';
use CGI qw|:standard|;
#use HTML::Entities;
use ConfigReader::Simple;
#
#	Load config file
#
my $config = ConfigReader::Simple->new("perlog.conf");
die "Could not read the config file! $ConfigReader::Simple::ERROR\n" unless ref $config;
#
#	Get config variables
#
my $browserdbtype=$config->get("browserdbtype");
my $browserdbname=$config->get("browserdbname");
my $browserdbuser=$config->get("browserdbuser");
my $browserdbpassword=$config->get("browserdbpassword");
my $browserdbhost=$config->get("browserdbhost");
my $browserdbport=$config->get("browserdbport");
my $url=$config->get("url");
my $systemwidekey=$config->get("systemwidekey");
my $logintype=$config->get("logintype");
my $refreshrate=$config->get("refreshrate");
#
#
#
@facilitydef=("Kernel","User","Mail","System","Security","Syslog","Printer","News","UUCP","Clock","Security","FTP","NTP","Audit","Alert","Clock","Local0","Local1","Local2","Local3","Local4","Local5","Local6","Local7");
@severitydef=("Emergancy","Alert","Critical","Error","Warning","Notice","Info","Debug");
#
#
#
$cgi = new CGI;
for $key ( $cgi->param() ) {
        $input{$key} = $cgi->param($key);
}
#
#       We need to know where to go
#
$section=$input{section};
#
#	If undefined go to Login
#
if ($section eq "") {
        $section = "index";
};
#
#
#
$browserdsn = "DBI:$browserdbtype:$browserdbname:$browserdbhost";
$dsn = "DBI:$admindbtype:$admindbname:$admindbhost";
#
#
#
print header();
&$section;
#
#

sub index
	{
	print "<HTML><head><title>PerLOG</title></head>\n";
	print "<frameset rows=\"60,*\"><frame src=\"logbrowser.cgi?section=menu\" name=\"menu\" /><frame src=\"logbrowser.cgi?section=tail\" name=\"main\" /></frameset> </HTML>\n";
	}
sub menu
	{
	print "<HTML><body bgcolor=\"dcdcdc\"><table border=\"0\"><tr><td width=\"75\"><img src=\"perlog.png\"></td>\n";
	print "<td width=\"100\"><center><a href=\"logbrowser.cgi?section=admin\" target=\"main\">Administration</a></center></td>\n";
	print "<td width=\"100\"><center><a href=\"logbrowser.cgi?section=tail\" target=\"main\">Tail</a></center></td>\n";
	print "<td width=\"100\"><center><a href=\"logbrowser.cgi?section=filter\" target=\"main\">Filter</a></center></td>\n";
	print "<td width=\"100\"><center><a href=\"logbrowser.cgi?section=search\" target=\"main\">Search</a></center></td>\n";
	print "</tr></table></body></HTML>\n";

	}
sub login
	{
	print "<HTML><HEAD></HEAD><BODY>We Made it here</BODY></HTML> \n";

	}
sub admin
	{


	}
sub tail
	{
	print "<html><head><META HTTP-EQUIV=\"CACHE-CONTROL\" CONTENT=\"NO-CACHE\"><meta http-equiv=\"refresh\" content=\"$refreshrate\"></head><body>\n";
	print "<table><tr><th>Time</th><th>IP</th><th>Hotname</th><th>Facility</th><th>Severity</th><th>Program</th><th>Message</th></tr>\n";
	my $dbh = DBI->connect ($browserdsn, $browserdbuser, $browserdbpassword) or die "Can't Connect." .$sth->errstr;
	$sth = $dbh->prepare ("select * from logs order by entryid DESC Limit 50") or die "Can't prepare statement." .$sth->errstr;
	$sth->execute() or die "Can't Execute." .$sth->errstr;
	while (@row = $sth->fetchrow_array) {
		#
		#	If the severity is certain levels give the whole row a certain color
		#
		if ($row[8]<=1) {
			print "<tr bgcolor=\"red\">\n";			
		} elsif ($row[8]==2) {
			print "<tr bgcolor=\"fuchsia\">\n";
		} elsif ($row[8]==3 || $row[8]==4) {
			print "<tr bgcolor=\"yellow\">\n";
		} else {
			print "<tr>\n";
		};
		#
		#	Print the Timestamp RemoteIP and Givenhostname
		#
		print "<td>$row[1]</td>\n";
		print "<td>$row[2]</td>\n";
		print "<td>$row[4]</td>\n";
		#
		#	Certain facilities get special colors
		#
		if ($row[7]=~/^(0|3|4|10|13|14)/) {
			print "<td bgcolor=\"yellow\">\n";
		} else {
			print "<td>\n";
		};
		#
		#	Change the facility from numbers to words
		#
		if (@row[7]=~/None/ig) {
			print "$row[7]</td>\n";
		} else {
			$facility=$facilitydef[$row[7]];
			print "$facility</td>\n";
		};
		#
		#	Change the severity level from numbers to words
		#
		if (@row[8]=~/None/ig) {
			print "<td>$row[8]</td>\n";
		} else {
			$severity=$severitydef[$row[8]];
			print "<td>$severity</td>\n";
		};
		#
		#	Look for keywords, if found change the cell color to red
		#
		print "<td>$row[9]</td>\n";
		if (($row[10]=~/Failed/ig && $row[10]=~/Password/ig)||($row[10]=~/Failed/ig && $row[10]=~/Login/ig)||($row[10]=~/authentication/ig && $row[10]=~/failure/ig)) {
			print "<td bgcolor=\"red\">\n";
		} else {
			print "<td>\n";
		};
		print "$row[10]</td>\n";
		#
		#	We are done with this Row
		#
		print "</tr>\n";
		

	};	
	print "</table></body></html>\n";


	}
sub filter
	{
	print "<HTML><center><h2>PerLOG Filter</h2><form action\"logbrowser.cgi\" method=\"GET\" target=\"main\"><br /><br /><br />\n";
	print "<input type=\"hidden\" name=\"section\" value=\"filterout\" />\n";
	print "<table>\n";
	print "<tr><td>What System Do you want to watch\?</td><td><select name=\"remoteip\" /><option value=\"all\">All</option>\n";
	my $dbh = DBI->connect ($browserdsn, $browserdbuser, $browserdbpassword) or die "Can't Connect." .$sth->errstr;
	$sth = $dbh->prepare ("select distinct remoteip from logs order by remoteip DESC") or die "Can't prepare statement." .$sth->errstr;
	$sth->execute() or die "Can't Execute." .$sth->errstr;
	while ($row = $sth->fetchrow_array) {
		print "<option value=\"$row\">$row</option>\n";
	};
	print "</select></td></tr>\n";
	print "<tr><td>What Facility Do you want to watch\?</td><td><select name=\"facility\" /><option value=\"99\">All</option>\n";
	$count="0";
	while (@facilitydef[$count]) {
		print "<option value=\"$count\">@facilitydef[$count]</option>\n";
		$count++;
	};
	print "</select></td></tr>\n";
	print "<tr><td>What Level of Severity or Greater do you want to watch\?</td><td><select name=\"severity\" /><option value=\"99\">All</option>\n";
	$count="0";
	while (@severitydef[$count]) {
		print "<option value=\"$count\">@severitydef[$count]</option>\n";
		$count++;
	};	
	print "</select></td></tr>\n";
	print "<tr><td colspan=\"2\"><center><input type=\"submit\" value=\"Submit\" /></center></td></tr>\n";
	print "</table></form></center>\n";



	}
sub filterout
	{
	$remoteip=$input{remoteip};
	$facilityin=$input{facility};
	$severityin=$input{severity};
	print "<html><head><META HTTP-EQUIV=\"CACHE-CONTROL\" CONTENT=\"NO-CACHE\"><meta http-equiv=\"refresh\" content=\"$refreshrate\"></head><body>\n";
	print "<table><tr><th>Time</th><th>IP</th><th>Hotname</th><th>Facility</th><th>Severity</th><th>Program</th><th>Message</th></tr>\n";
	if ($remoteip=~/all/ig) {
		my $dbh = DBI->connect ($browserdsn, $browserdbuser, $browserdbpassword) or die "Can't Connect." .$sth->errstr;
		$sth = $dbh->prepare ("select * from logs where facility<=? and severity<=? order by entryid DESC Limit 50") or die "Can't prepare statement." .$sth->errstr;
		$sth->execute($facilityin,$severityin) or die "Can't Execute." .$sth->errstr;
	} else {
		my $dbh = DBI->connect ($browserdsn, $browserdbuser, $browserdbpassword) or die "Can't Connect." .$sth->errstr;
		$sth = $dbh->prepare ("select * from logs where remoteip=? and facility<=? and severity<=? order by entryid DESC Limit 50") or die "Can't prepare statement." .$sth->errstr;
		$sth->execute($remoteip,$facilityin,$severityin) or die "Can't Execute." .$sth->errstr;
	};
	while (@row = $sth->fetchrow_array) {
		#
		#	If the severity is certain levels give the whole row a certain color
		#
		if ($row[8]<=1) {
			print "<tr bgcolor=\"red\">\n";			
		} elsif ($row[8]==2) {
			print "<tr bgcolor=\"fuchsia\">\n";
		} elsif ($row[8]==3 || $row[8]==4) {
			print "<tr bgcolor=\"yellow\">\n";
		} else {
			print "<tr>\n";
		};
		#
		#	Print the Timestamp RemoteIP and Givenhostname
		#
		print "<td>$row[1]</td>\n";
		print "<td>$row[2]</td>\n";
		print "<td>$row[4]</td>\n";
		#
		#	Certain facilities get special colors
		#
		if ($row[7]=~/^(0|3|4|10|13|14)/) {
			print "<td bgcolor=\"yellow\">\n";
		} else {
			print "<td>\n";
		};
		#
		#	Change the facility from numbers to words
		#
		if (@row[7]=~/None/ig) {
			print "$row[7]</td>\n";
		} else {
			$facility=$facilitydef[$row[7]];
			print "$facility</td>\n";
		};
		#
		#	Change the severity level from numbers to words
		#
		if (@row[8]=~/None/ig) {
			print "<td>$row[8]</td>\n";
		} else {
			$severity=$severitydef[$row[8]];
			print "<td>$severity</td>\n";
		};
		#
		#	Look for keywords, if found change the cell color to red
		#
		print "<td>$row[9]</td>\n";
		if (($row[10]=~/Failed/ig && $row[10]=~/Password/ig)||($row[10]=~/Failed/ig && $row[10]=~/Login2/ig)||($row[10]=~/authentication/ig && $row[10]=~/failure/ig)) {
			print "<td bgcolor=\"red\">\n";
		} else {
			print "<td>\n";
		};
		print "$row[10]</td>\n";
		#
		#	We are done with this Row
		#
		print "</tr>\n";
		

	};	
	print "</table></body></html>\n";
	}
sub search
	{
	print "<HTML><center><h2>PerLOG Search</h2><form action\"logbrowser.cgi\" method=\"GET\" target=\"main\"><br /><br /><br />\n";
	print "<input type=\"hidden\" name=\"section\" value=\"searchout\" />\n";
	print "<table>\n";
	print "<tr><td>What System Do you want to watch\?</td><td><select name=\"remoteip\" /><option value=\"all\">All</option>\n";
	my $dbh = DBI->connect ($browserdsn, $browserdbuser, $browserdbpassword) or die "Can't Connect." .$sth->errstr;
	$sth = $dbh->prepare ("select distinct remoteip from logs order by remoteip DESC") or die "Can't prepare statement." .$sth->errstr;
	$sth->execute() or die "Can't Execute." .$sth->errstr;
	while ($row = $sth->fetchrow_array) {
		print "<option value=\"$row\">$row</option>\n";
	};
	print "</select></td></tr>\n";
	print "<tr><td>What Facility Do you want to watch\?</td><td><select name=\"facility\" /><option value=\"99\">All</option>\n";
	$count="0";
	while (@facilitydef[$count]) {
		print "<option value=\"$count\">@facilitydef[$count]</option>\n";
		$count++;
	};
	print "</select></td></tr>\n";
	print "<tr><td>What Level of Severity or Greater do you want to watch\?</td><td><select name=\"severity\" /><option value=\"99\">All</option>\n";
	$count="0";
	while (@severitydef[$count]) {
		print "<option value=\"$count\">@severitydef[$count]</option>\n";
		$count++;
	};	
	print "</select></td></tr>\n";
	print "<tr><td>Message Keyword\(s\)\?</td><td><input type=\"text\" name=\"keyword\"></td></tr>\n";
	print "<tr><td colspan=\"2\"><center><input type=\"submit\" value=\"Submit\" /></center></td></tr>\n";
	print "</table></form></center>\n";

	}
sub searchout
	{
	$remoteip=$input{remoteip};
	$facilityin=$input{facility};
	$severityin=$input{severity};
	$keyword=$input{keyword};
	print "<html><head></head><body><center><h2>PerLOG Search Results</h2></center>\n";
	print "<table><tr><th>Time</th><th>IP</th><th>Hotname</th><th>Facility</th><th>Severity</th><th>Program</th><th>Message</th></tr>\n";
	my $dbh = DBI->connect ($browserdsn, $browserdbuser, $browserdbpassword) or die "Can't Connect." .$sth->errstr;
	#
	#	If $remoteip is all we do not look for RemoteIP
	#
	if ($remoteip=~/all/ig) {
		#
		#	If $keyword is not defined we need to not do the boolean search
		#
		if ($keyword=~/\w/g) {
			$sth = $dbh->prepare ("SELECT * from logs WHERE MATCH (message) AGAINST (? IN BOOLEAN MODE) and facility<=? and severity<=? order by entryid DESC") or die "Can't prepare statement." .$sth->errstr;
			$sth->execute($keyword,$facilityin,$severityin) or die "Can't Execute." .$sth->errstr;
		} else {
			$sth = $dbh->prepare ("SELECT * from logs WHERE facility<=? and severity<=? order by entryid DESC") or die "Can't prepare statement." .$sth->errstr;
			$sth->execute($facilityin,$severityin) or die "Can't Execute." .$sth->errstr;
		};
	} else {
		if ($keyword=~/\w/g) {
			$sth = $dbh->prepare ("SELECT * from logs WHERE MATCH (message) AGAINST (? IN BOOLEAN MODE) and remoteip=? and facility<=? and severity<=? order by entryid DESC") or die "Can't prepare statement." .$sth->errstr;
			$sth->execute($keyword,$remoteip,$facilityin,$severityin) or die "Can't Execute." .$sth->errstr;
		} else {
			$sth = $dbh->prepare ("SELECT * from logs WHERE remoteip=? and facility<=? and severity<=? order by entryid DESC") or die "Can't prepare statement." .$sth->errstr;
			$sth->execute($remoteip,$facilityin,$severityin) or die "Can't Execute." .$sth->errstr;
		}
	};
	#
	#	End $keyword and $remoteip if statements
	#
	while (@row = $sth->fetchrow_array) {
		#
		#	If the severity is certain levels give the whole row a certain color
		#
		if ($row[8]<=1) {
			print "<tr bgcolor=\"red\">\n";			
		} elsif ($row[8]==2) {
			print "<tr bgcolor=\"fuchsia\">\n";
		} elsif ($row[8]==3 || $row[8]==4) {
			print "<tr bgcolor=\"yellow\">\n";
		} else {
			print "<tr>\n";
		};
		#
		#	Print the Timestamp RemoteIP and Givenhostname
		#
		print "<td>$row[1]</td>\n";
		print "<td>$row[2]</td>\n";
		print "<td>$row[4]</td>\n";
		#
		#	Certain facilities get special colors
		#
		if ($row[7]=~/^(0|3|4|10|13|14)/) {
			print "<td bgcolor=\"yellow\">\n";
		} else {
			print "<td>\n";
		};
		#
		#	Change the facility from numbers to words
		#
		if (@row[7]=~/None/ig) {
			print "$row[7]</td>\n";
		} else {
			$facility=$facilitydef[$row[7]];
			print "$facility</td>\n";
		};
		#
		#	Change the severity level from numbers to words
		#
		if (@row[8]=~/None/ig) {
			print "<td>$row[8]</td>\n";
		} else {
			$severity=$severitydef[$row[8]];
			print "<td>$severity</td>\n";
		};
		#
		#	Look for keywords, if found change the cell color to red
		#
		print "<td>$row[9]</td>\n";
		if (($row[10]=~/Failed/ig && $row[10]=~/Password/ig)||($row[10]=~/Failed/ig && $row[10]=~/Login2/ig)||($row[10]=~/authentication/ig && $row[10]=~/failure/ig)) {
			print "<td bgcolor=\"red\">\n";
		} else {
			print "<td>\n";
		};
		print "$row[10]</td>\n";
		#
		#	We are done with this Row
		#
		print "</tr>\n";
		

	};	
	print "</table></body></html>\n";

	}





