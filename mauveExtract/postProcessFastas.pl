foreach $file (@ARGV)
{	open FILE,$file;
	@numbers = ();
	while (<FILE>)
	{
		if (substr($_,0,1) eq ">")
		{	substr($_,0,1) = "";
			@lines = split(":",$_);
			push (@numbers,$lines[0]);
		}
	}
	@sorted  = ();
	@sorted = sort { $a <=> $b } @numbers;
	if (@sorted ~~ [1..12])  # change as needed
	{	push (@filesToMerge,$file);
	}
}

foreach $file (@filesToMerge)
{	open FILE,$file;
	while (<FILE>)
	{	if (substr($_,0,1) eq ">")
		{	substr($_,0,1) = "";
        @lines = split(":",$_);
        $currSeq = $lines[0];	
		}
		else
		{	chomp;
			$_ =~ s/^\s+//;
			$seq{$currSeq} .= $_;
		}
	}
}

foreach $key (keys %seq)
{
	print ">$key\n";
	print $seq{$key},"\n";
}
