#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 assembly1.fasta assembly2.fasta" >&2
  exit 1
fi

ASM1="$1"
ASM2="$2"

# Nice short names for output files (no paths, just basenames)
B1=$(basename "$ASM1")
B2=$(basename "$ASM2")

# Unique cluster file name
CLUSTERS="${B1}.${B2}.clusters.tsv"

# Temporary working directory for all intermediate junk
WORKDIR=$(mktemp -d)
TMP_MMSEQ="${WORKDIR}/mmseqs_tmp"
mkdir -p "$TMP_MMSEQ"

echo "Working in: $WORKDIR" >&2

########################################
# 1. Prodigal gene calling
########################################

prodigal -i "$ASM1" -a "${WORKDIR}/${B1}.faa" -d "${WORKDIR}/${B1}.ffn" \
         -o "${WORKDIR}/${B1}.genes" -p single -f gff -q

prodigal -i "$ASM2" -a "${WORKDIR}/${B2}.faa" -d "${WORKDIR}/${B2}.ffn" \
         -o "${WORKDIR}/${B2}.genes" -p single -f gff -q

########################################
# 2. Label proteins with asm1/asm2 and concat
########################################

sed 's/^>/\>asm1|/' "${WORKDIR}/${B1}.faa" > "${WORKDIR}/${B1}.labeled.faa"
sed 's/^>/\>asm2|/' "${WORKDIR}/${B2}.faa" > "${WORKDIR}/${B2}.labeled.faa"

cat "${WORKDIR}/${B1}.labeled.faa" "${WORKDIR}/${B2}.labeled.faa" > "${WORKDIR}/all_proteins.faa"

########################################
# 3. MMseqs clustering (everything stays in WORKDIR)
########################################

mmseqs createdb "${WORKDIR}/all_proteins.faa" "${WORKDIR}/allDB"

mmseqs cluster "${WORKDIR}/allDB" "${WORKDIR}/allClu" "$TMP_MMSEQ" \
  --min-seq-id 0.95 -c 0.95 --cov-mode 1

mmseqs createtsv "${WORKDIR}/allDB" "${WORKDIR}/allDB" "${WORKDIR}/allClu" "$CLUSTERS"

########################################
# 4. Run the Python script on the clusters
########################################

python count_splits_unique.py "$CLUSTERS" asm1 asm2

########################################
# 5. Cleanup everything except the clusters file
########################################

rm -rf "$WORKDIR"

echo "Kept clusters file: $CLUSTERS" >&2
