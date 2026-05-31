use strict;
use warnings;

my @nums = (1, 2, 3);
my $total = 0;
$total += $_ for @nums;
print "$total\n";
