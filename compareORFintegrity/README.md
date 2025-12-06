# Workflow for estimating split ORFs across assemblies

This workflow was developed to compare genome assemblies before and after polishing. 
The goal is to detect ORFs unique to genome 1 that are split into 2 or more ORFs in genome 2, which can result from frameshifts after homopolymer errors.

To compare two files run:

`bash compare_orf_integrity.sh [genome1.fa] [genome2.fa]`

-- where genome1 is the polished/corrected one and genome 2 is the unpolished one

This will return output like:

```
asm1: 86 (self-unique) genes map to >=2 genes in asm2
asm2: 10 (self-unique) genes map to >=2 genes in asm1
```

Theoretically, we should see more self-unique ORFs from genome 1 that map to two or more ORFs in genome 2.

## Testing workflow on simulated set genomes with varying levels of homopolymer-induced frameshifts

To test the above program, we can do:

```
# this will generate a set of 7 pseudogenomes where n = 10, 50, 100, 500, 1000, 5000, and 10000 homopolymer errors have been introduced to genome.fa 
python make_polyA_insertion_genomes.py genome.fa -o testgenome --seed $RANDOM

for n in 10 50 100 500 1000 5000 10000; do
    bash compare_orf_integrity.sh genome.fa testgenome.polyA_${n}.fa
done

```
