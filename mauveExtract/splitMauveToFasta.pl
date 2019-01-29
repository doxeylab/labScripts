open FILE,$ARGV[0];

$filename = 0;

open (FH,">", $filename . ".fasta");

while (<FILE>)

{	
	unless (substr($_,0,1) eq "#")
	{

		if (substr($_,0,1) eq "=")
		{	$filename ++;
			close FH;
			open (FH,">", $filename . ".fasta");
			#print FH $_;
		}
		else
		{	print FH $_;
		}
	}
}
