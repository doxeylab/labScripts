#!/usr/bin/env python3
import sys
from collections import defaultdict

if len(sys.argv) != 4:
    print(f"Usage: {sys.argv[0]} hits.tsv asm1_label asm2_label", file=sys.stderr)
    sys.exit(1)

hits_file, asm1, asm2 = sys.argv[1], sys.argv[2], sys.argv[3]

# cross_maps[asm_label][gene] = set of partner genes in the OTHER assembly
cross_maps = {
    asm1: defaultdict(set),
    asm2: defaultdict(set),
}

# self_maps[asm_label][gene] = set of partner genes in the SAME assembly
# (including itself if self-alignments are present)
self_maps = {
    asm1: defaultdict(set),
    asm2: defaultdict(set),
}

with open(hits_file) as fh:
    for line in fh:
        if not line.strip():
            continue
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 2:
            continue
        a, b = parts[0], parts[1]
        if "|" not in a or "|" not in b:
            continue

        lab_a, gene_a = a.split("|", 1)
        lab_b, gene_b = b.split("|", 1)

        # same-assembly hits → record as self hits (undirected)
        if lab_a == lab_b and lab_a in (asm1, asm2):
            self_maps[lab_a][gene_a].add(gene_b)
            self_maps[lab_a][gene_b].add(gene_a)
            continue

        # cross-assembly hits → record in both directions
        if lab_a == asm1 and lab_b == asm2:
            cross_maps[asm1][gene_a].add(gene_b)
            cross_maps[asm2][gene_b].add(gene_a)
        elif lab_a == asm2 and lab_b == asm1:
            cross_maps[asm2][gene_a].add(gene_b)
            cross_maps[asm1][gene_b].add(gene_a)
        # ignore hits involving other labels

def count_splits(label_self, label_other):
    """
    For genes in label_self:
      - ignore genes with >1 self-match (i.e. likely paralogs/repeats)
      - count those that map to >=2 genes in label_other
    """
    n = 0
    for gene, partners in cross_maps[label_self].items():
        # how many same-assembly partners?
        self_partners = self_maps[label_self].get(gene, set())
        # keep only "unique" genes: at most one self partner (itself)
        if len(self_partners) <= 1 and len(partners) >= 2:
            n += 1
    return n

asm1_split = count_splits(asm1, asm2)
asm2_split = count_splits(asm2, asm1)

print(f"{asm1}: {asm1_split} (self-unique) genes map to >=2 genes in {asm2}")
print(f"{asm2}: {asm2_split} (self-unique) genes map to >=2 genes in {asm1}")
