#!/usr/bin/perl
#	
#		LogListener v0.7
#		Copyright 2010 Chris Brandstetter
#			Copyrighted under the GPLv3
#
#	Load Modules
#use warnings;
use IO::Socket;
use DBI;
use ConfigReader::Simple;
use NetAddr::IP;
#
#	Tell them we are starting
#
print "\n\n ----====STARTING PerLOG Server====---- \n\n";
#
#	Load config file
#
print "Reading Config file\n\n";
my $config = ConfigReader::Simple->new("perlog.conf");
die "Could not read the config file! $ConfigReader::Simple::ERROR\n" unless ref $config;
#
#	Grab variables for processing
#
my $localaddress=$config->get("localaddress");
my $localport=$config->get("localport");
my $protocol=$config->get("protocol");
my $maxlength=$config->get("maxlength");
my $dbtype=$config->get("logdbtype");
my $dbname=$config->get("logdbname");
my $dbuser=$config->get("logdbuser");
my $dbpassword=$config->get("logdbpassword");
my $dbhost=$config->get("logdbhost");
my $dbport=$config->get("logdbport");
my $os=$config->get("os");
my $logtolocal=$config->get("logtolocal");
my $display=$config->get("display");
my $debug=$config->get("debug");
my $acceptedipcidr=$config->get("acceptedipcidr");
#
#	If debug is set to 1 or greater display general messages no matter what the $display variable says
#
if ($debug >= 1) {
	$display="yes";
};
#
#	Setup our IP restrictions
#
my $acceptedips=NetAddr::IP->new($acceptedipcidr);
#
#	Config up dsn 
#
if ($debug >= 2) {
	print "DBBrand is $dbtype DBName is $dbname DBHost is $dbhost\n";
};
if ($dbtype=~/mysql/i) {
	$dbbrand="mysql";
	$dsn = "DBI:$dbbrand:$dbname:$dbhost";
} elsif ($dbtype=~/postgresql/i) {
	$dbbrand="Pg";
	$dsn = "DBI:$dbbrand:$dbname:$dbhost";
} elsif ($dbtype=~/postgres/i) {
	$dbbrand="Pg";
	$dsn = "DBI:$dbbrand:$dbname:$dbhost";	
} elsif ($dbtype=~/pg/i) {
	$dbbrand="Pg";
	$dsn = "DBI:$dbbrand:$dbname:$dbhost";
} elsif ($dbtype=~/None/i) {
	print "Screen Output Only no Database Configured!!!\n";
	#
	#	Reconfigure Display to make sure we are showing otherwise what are we doing?????
	#
	$display="yes";	
} else {
	print "----==== ERROR!!!!! Database type not correctly identified please use MySQL, PostgreSQL, or PG case insensitive====---- \n";
	die
};
#
#	Check DB Config
#
if ($dbtype!~/None/i) {
	if ($display =~/yes/i) {
		print "Checking DB Config\n";
		print "Connecting to $dbtype Database $dbname on host $dbhost\:$dbport.\n\n";
	};
	if ($debug >= 2) {
		print "DBUser is $dbuser DBPassword is $dbpassword\n";
	};
	if ($dbtype=~/mysql/i) {
		$dbh1 = DBI->connect ($dsn, $dbuser, $dbpassword) or die "Can't Connect." .$sth1->errstr;
		$sth1 = $dbh1->prepare ("INSERT INTO `programlog` (`event`) VALUES (?)") or die "Can't Prepare Statement." .$sth1->errstr;
		$sth1->execute("started") or die "Can't Execute Insert Statement." .$sth1->errstr;
		$dbh1->disconnect;
	} elsif ($dbtype=~/postgresql/i) {
	
	} elsif ($dbtype=~/postgres/i) {
	
	} elsif ($dbtype=~/pg/i) {
	
	} else {
		print "----==== ERROR!!!!! Database type not correctly identified please use MySQL, PostgreSQL, or PG case insensitive====---- \n";
		die
	};
};
#
#	Start up Listener
#
if ($display =~/yes/i) {
	print "Starting Listener on Port $localport using $protocol on Address $localaddress\n\n";
};
$socket = IO::Socket::INET->new(LocalPort => $localport, LocalAddr => $localaddress, Proto => $protocol, Reuse => 1)||die("Socket: $@");
#
#	Start loop to listen with
#
while ($socket->recv($buffer, $maxlength)) {
	if ($debug >= 3) {
		print "Buffer is $buffer\n";
		$originalmessage = $buffer;
		print "Pre-Sub Message is $originalmessage\n";
		($port, $ipaddress) = sockaddr_in($socket->peername);
		$connectingip = inet_ntoa($ipaddress);
		processor($originalmessage,$connectingip);
	} else {
		$originalmessage = $buffer;
		($port, $ipaddress) = sockaddr_in($socket->peername);
		$connectingip = inet_ntoa($ipaddress);
		processor($originalmessage,$connectingip);
	};	
};
#
#	sub processor actually logs the syslog messages
#
sub processor
	{
	#	Pull in the Message buffer
	my $originalmessage=shift;
	$message=$originalmessage;
	my $connectingip=shift;
	#	Debug Section
	if ($debug >= 1) {
		print "IP Address is $connectingip Original Message=$message\n";
	};
	#	Macs add new lines at the end, lets get rid of those
	chomp $message;
	#	Get IP Address that connected
	my $incomingip=NetAddr::IP->new($connectingip);
	#
	$nonrfc="";
	#
	#	Clean up and organize the Message buffer
	#
	# Variables we end up with: $facility $severity $date $hostname $message
	#
	if ($incomingip->within($acceptedips)) {
		#
		#
		#
		eval {
			$message=~/^\<(.|..|...)\>/;				# Get the Facility/Severity from the beggining of the Message buffer
			$facserv=$1;
			$severity=$facserv % 8;				# Calc remainder to determine Severity
			$facility=($facserv-$severity) / 8;			# Calc Facility by div by 8
			$facservlength= (length ($facserv))+2;		# Calculate the length of the Facility/Severity add 2 for the containing symbols
			$date= substr($message, $facservlength, 15);		# Grab the date by counting in the length of the Facility/Severity and then grabbing 15 Chars
			$message=~s/\<$facserv\>$date\s//g;			# Remove Facility/Severity and date/time from the Message buffer
			@datesplit = (split " ",$date);				# Split Date and Time on spaces
			$date="$datesplit[0] $datesplit[1]";			# Recombine Month and Date
			if ($date !~ /\w{3}\s.\d/) {
				$nonrfc="True";
				};		
			$time=$datesplit[2];					# Set Time
			if ($time !~ /\d{2}:\d{2}:\d{2}/) {
				$nonrfc="True";
				};		
	
			$message=~/^(\S+)\s/;					# Select all to the first space
			$hostname=$1;
			$message=~s/$hostname\s//g;				# remove hostname from Message buffer
			$message=~/^(\S+)\:/;					# Select all to the first colon for program reporting
			$program=$1;
			if ($program=~/\[\d+\]/) {				# If program has PID in [] remove them
				$program=~/^(\S+)\[/;
				$program=$1;
				$message=~s/$program\[\d+\]\://;
			}elsif ($program=~/\-\d+/) {				# If program has PID after - remove it
				$program=~/^(\S+)\-/;
				$program=$1;
				$message=~s/$program\-\d+\://;
			} else {
				$message=~s/$program\://;
			};
			if ($message=~/^\:/) {					# Remove any leading : in the Message buffer leftover from removing the program 
				$message=~s/^\://g;
			};
			while ($message=~/^\s/) {					# Remove any leading spaces
				$message=~s/^\s//;
			};
		# End of eval
		};
		#
		#	This is for Non-RFC Compliant messages
		#
		if ($@ =~ /\S{1,}/g || $nonrfc =~ "True") {
			#
			#	Reset Message Variable
			#
			$message=$originalmessage;
			#
			#
			#
			$message=~/^\<(.|..|...)\>/;				# Get the Facility/Severity from the beggining of the Message buffer
			$facserv=$1;
			$severity=$facserv % 8;				# Calc remainder to determine Severity
			$facility=($facserv-$severity) / 8;			# Calc Facility by div by 8
			$facservlength= (length ($facserv))+2;		# Calculate the length of the Facility/Severity add 2 for the containing symbols
			$message=~s/\<$facserv\>//g;			# Remove Facility/Severity and date/time from the Message buffer
			$hostname="None";
			$date="None";
			$time="None";
			$program="None";
		};
		#
		#	Insert Variables into DB
		#
		if ($dbtype!~/None/i) {
			if ($dbtype=~/mysql/i) {
				$dbh2 = DBI->connect ($dsn, $dbuser, $dbpassword) or die "Can't Connect." .$sth2->errstr;
				$sth2 = $dbh2->prepare ("INSERT INTO `logs` (`remoteip`, `givenhostname`, `givendate`, `giventime`, `facility`, `severity`, `program`, `message`) VALUES (?,?,?,?,?,?,?,?)") or die "Can't Prepare Statement." .$sth2->errstr;
				$sth2->execute($connectingip,$hostname,$date,$time,$facility,$severity,$program,$message) or die "Can't Execute Insert Statement." .$sth2->errstr;
				$dbh2->disconnect;
			} elsif ($dbtype=~/postgresql/i) {

			} elsif ($dbtype=~/postgres/i) {
		
			} elsif ($dbtype=~/pg/i) {	

			} else {
				print " How did we get here??????  This should be caught at the begining!!! \n";
				die
			};
		};
		#
		#	If set log Messages to local syslog also
		#
		if ($logtolocal =~/yes/i) {
			if ($os =~ /linux/i) {
			#
			#	Logging local in Linux
			#

		};
		};
		#
		#	If Display is set to yes
		#
		if ($display =~/yes/i) {
			print "RemoteIP=$connectingip Facility=$facility Severity=$severity Date=$date Time=$time Hostname=$hostname Program=$program Message=$message\n";
		};
	} else {
		#
		#	IP Not allowed log illegal connection
		#
		if ($dbtype!~/None/i) {
			if ($display =~/yes/i) {
				print "Illegal Connection from $connectingip\n";
			};
			if ($dbtype=~/mysql/i) {
				$event="Illegal Connection from $connectingip";
				$dbh1 = DBI->connect ($dsn, $dbuser, $dbpassword) or die "Can't Connect." .$sth1->errstr;
				$sth1 = $dbh1->prepare ("INSERT INTO `programlog` (`event`) VALUES (?)") or die "Can't Prepare Statement." .$sth1->errstr;
				$sth1->execute($event) or die "Can't Execute Insert Statement." .$sth1->errstr;
				$dbh1->disconnect;
			} elsif ($dbtype=~/postgresql/i) {
	
			} elsif ($dbtype=~/postgres/i) {
	
			} elsif ($dbtype=~/pg/i) {
	
			} else {

			};
		} else {
			if ($display =~/yes/i) {
				print "Illegal Connection from $connectingip\n";
			};
		};
	};	
	#	End of sub processor
	};
#
#	The End
#

