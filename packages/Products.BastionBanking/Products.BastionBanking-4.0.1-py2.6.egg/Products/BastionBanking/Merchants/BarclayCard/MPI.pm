#    Copyright (C) 2003  Corporation of Balclutha and contributors.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

package MPI;

use HTTP::Request;
use HTTP::Request::Common;
use LWP::UserAgent;
use XML::Parser;

use Data::Dumper;

use constant BARCLAYS_URI => 'https://secure2.epdq.co.uk:11500';

#
# XML Parser + state machine info ...
#
my @stack = ();
my $interested = 0;
my %results = ();
my $parser = new XML::Parser(ErrorContext => 2, Style => 'Subs', Handlers => { Char => \&Char });

#BEGIN {
#    open DEBUG, ">/tmp/MPI.pm.txt";
#    DEBUG->autoflush(1);
#}

#END {
#    close DEBUG;
#}

sub send {
    my ($text) = @_;	
    $text = 'CLRCMRC_XML=' . $text;

    my $ua = new LWP::UserAgent( timeout=> 30 );

    my $new_request = HTTP::Request->new(POST=>BARCLAYS_URI);
    $new_request->header('Content-Type' => 'text/xml');
    $new_request->header('Content-Length' => length($text));
    $new_request->content($text);
 
    my $response = $ua->request($new_request);
    # $response->status_line
    if ( $response->is_success ) {
	@stack = ();
	$interested = 0;
	%results = ();
	$parser->parse($response->content);
	return [$results{'Id'}, 
		$results{'Total'}, 
		$results{'ProcReturnCode'},
		$results{'MaxSev'},
		$results{'Text'},
		$response->content];
    }
    else {
	return [undef, undef, undef, $response->code, $response->message, undef];
    }
}

#
# XML Parser Handlers ...
#

# we have to manually join words ...
sub Char {
    my ($expat, $value) = @_;
    if ($interested) {
        #print DEBUG "$value\n"; 
	$value =~ s/\n//g;
	$tag = $stack[scalar(@stack) - 1];
        if (exists $results{$tag}) {
             $results{ $tag } .= $value;
        }
	else {
	     $results{ $tag } = $value;
        }
    }
}

#
# These handlers all relate to the XML tags we're interested in ...
#

sub MaxSev {
    # message severity 
    $interested = 1;
    push @stack, $_[1];
}
sub MaxSev_ {
    pop @stack;
    $interested = 0;
}

sub Text {
    # message text - just last msg in MessageList ...
    $interested = 1;
    push @stack, $_[1];
}
sub Text_ {
    pop @stack;
    $interested = 0;
}

sub Id {
    # ePDQ txn id ...
    $interested = 1;
    push @stack, $_[1];
}
sub Id_ {
    pop @stack;
    $interested = 0;
}

sub Total {
    # transaction total 
    $interested = 1;
    push @stack, $_[1];
}
sub Total_ {
    pop @stack;
    $interested = 0;
}

sub ProcReturnCode {
    # transaction return code
    $interested = 1;
    push @stack, $_[1];
}
sub ProcReturnCode_ {
    pop @stack;
    $interested = 0;
}


1;
