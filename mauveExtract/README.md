To extract blocks from a mauve alignment (.xmfa file) and create a concatenated alignment:

1) split the .xmfa into a series of fasta files for each orthologous block

```
perl splitMauveToFasta.pl mauveAlignment.xmfa # this will generate .fasta files in the same directory
```

2) retrieve and concatenate all .fasta files that include a pre-defined set & order of sequences (e.g., line below will require that all orthologous blocks contain sequences 1-12)
`` @sorted ~~ [1,2,3,4,5,6,7,8,9,10,11,12] `` [NOTE: CHANGE THE FOLLOWING LINE IN postProcessFastas.pl FOR YOUR CASE - e.g., change '12' to the number of genomes you want to require in the output]

```
perl postProcessFastas.pl *.fasta >output.aln
```

3) build tree from output.aln
