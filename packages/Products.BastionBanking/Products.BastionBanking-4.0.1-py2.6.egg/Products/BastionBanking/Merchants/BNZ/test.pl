#
# This is a crufty test script copied (and slightly modified) from
# BNZ's Perl API documentation.
#

use webpayperl;
use strict;

# 
# Declare constants here... 
# modify these for your own use. 
# 
use constant THE_CLIENT_ID => "10009999";       # your merchant id here
use constant THE_CERT_PATH => "gateway.cer";
use constant THE_CERT_PASSWORD => "xxxxxxxx";   # your certificate password here
use constant THE_PORT => "3007";
#use constant THE_SERVER => "trans1.buylineplus.co.nz,trans2.buylineplus.co.nz";
use constant THE_SERVER => "trans2.buylineplus.co.nz";

BEGIN {
    webpayperl::init_client() or die "webpayperl::init_client() failed!\n$?\n";
}

END {
    webpayperl::free_client() or die "webpayperl::free_client() failed!\n$?\n";
}

for (my $loop_index = 1;
     $loop_index <= 2;
     $loop_index++) { 
    print "-------------------------------------------------\n";
    print "Doing transaction number $loop_index\n";
    my $webpayRef = webpayperl::newBundle();
    webpayperl::setUp($webpayRef, THE_SERVER, THE_PORT, THE_CERT_PATH, THE_CERT_PASSWORD, THE_CLIENT_ID);
    webpayperl::setAttr($webpayRef, "TOTALAMOUNT", "12.00");
    webpayperl::setAttr($webpayRef, "CARDDATA", "4564456445644564");
    webpayperl::setAttr($webpayRef, "CARDEXPIRYDATE", "0505");
    webpayperl::setAttr($webpayRef, "COMMENT", "Testing the webpayPerl api");
    webpayperl::setAttr($webpayRef, "INTERFACE", "CREDITCARD");
    webpayperl::setAttr($webpayRef, "TRANSACTIONTYPE", "PURCHASE");
    my $tranProcessed = webpayperl::execute( $webpayRef );
    if ($tranProcessed) { 
	# If the execute method returns successfully this indicates
	# that communication with the Payment Gateway has been successful. 
	# A further test of the Response Code and Response Text will be 
	# required to determine if the Payment has been successfully 
	# Authorised. Please see the developers guide for more details. 
	print "Successfully communicated with the WTS.\n";
    } else { 
	# There has been a problem during the execute call. 
	# Log message. 
	print "Unable to communicate with the WTS.\n";
	# Try transaction recovery 
	my $txnRef = webpayperl::getAttr( $webpayRef, "TXNREFERENCE");
	if($txnRef){ 
	    # We have a trans reference so attempt a status transaction. 
	    print "Performing status check with TransRef = [$txnRef]\n";
	    if(doStatusCheck($webpayRef)) { 
		print "Status Check Successful - Details below.\r\n";
	    } else { 
		print "Status check failed: Unknown transaction ";
		print "status. Please wait a short while and try ";
		print "status check again using Transaction Ref ";
		print "[$txnRef].\r\n" ;
	    } 
	} else { 
	    # There is no transaction reference number so the transaction 
	    # has failed completely. It can be safely reprocessed. 
	    print "The transaction can be safely reprocessed ";
	    print "as no Transaction Reference Number exists.\n";
	}
    }
    
    displayResults($webpayRef);
    webpayperl::cleanup( $webpayRef );
}


sub doStatusCheck($) { 
    my $webpayRef = $_[0];
    my $txnRef = webpayperl::getAttr( $webpayRef, "TXNREFERENCE");
    if ($txnRef) { 
	# We have a transaction reference so attempt a status transaction. 
	webpayperl::setAttr( $webpayRef, "TRANSACTIONTYPE", "STATUS" );
	  return webpayperl::execute( $webpayRef );
      } else { 
	  # No txnref number so we can not do a status check. 
	  return 0;
      } 
} 

sub displayResults($) { 
    my $webpayRef = $_[0];
    my $txnRef = webpayperl::getAttr( $webpayRef, "TXNREFERENCE");
    my $result = webpayperl::getAttr( $webpayRef, "RESULT");
    my $authCode = webpayperl::getAttr( $webpayRef, "AUTHCODE");
    my $responseText = webpayperl::getAttr( $webpayRef, "RESPONSETEXT");
    my $responseCode = webpayperl::getAttr( $webpayRef, "RESPONSECODE");
    my $error = webpayperl::getAttr( $webpayRef, "ERROR");
    print "--------------------------------------\n";
    if (approvedTransaction($responseCode)) { 
	print "-------- TRANSACTION APPROVED --------\n";
    } else { 
	print "------ TRANSACTION NOT APPROVED ------\n";
    } 
    print "--------------------------------------\n";
    print "Transaction Reference\t : [$txnRef]\r\n";
    print "Result\t\t\t : [$result]\r\n";
    print "Auth Code\t\t : [$authCode]\r\n";
    print "Response Text\t\t : [$responseText]\r\n";
    print "Response Code\t\t : [$responseCode]\r\n";
    print "Error Message\t\t : [$error]\r\n";
    print "--------------------------------------\n";
} 

sub approvedTransaction($) { 
    my $responseCode = $_[0];
    # 
    # Check the returned response Code against the list of 
    # known Approved Response Codes 
    # 
    # Please check the documentation to ensure that you have the 
    # latest list of approved response codes. 
    # 
    if ($responseCode) { 
	my @listOfApprovedResponseCodes;
	my $count = 0;
	my $testThisCode;
	$count = push (@listOfApprovedResponseCodes, "00");
	# Transaction Approved 
	$count = push (@listOfApprovedResponseCodes, "08");
	# Approved Signature 
	$count = push (@listOfApprovedResponseCodes, "77");
	# Approved 
	for(my $i = 0;
	    $i < $count;
	    $i++) { 
	    $testThisCode = pop(@listOfApprovedResponseCodes);
	    if( $responseCode eq $testThisCode){ 
		# we have a match 
		return 1;
	    } 
	} 
    } 
    return 0;
}

