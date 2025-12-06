#!/usr/bin/env python3
import argparse
import random
import sys
from copy import deepcopy
from typing import List, Tuple

FASTARecord = Tuple[str, str]  # (header, seq)


def read_fasta(path: str) -> List[FASTARecord]:
    records = []
    header = None
    seq_chunks = []

    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(seq_chunks)))
                header = line[1:].strip()
                seq_chunks = []
            else:
                seq_chunks.append(line.upper())
        if header is not None:
            records.append((header, "".join(seq_chunks)))
    return records


def write_fasta(records: List[FASTARecord], path: str, width: int = 80) -> None:
    with open(path, "w") as out:
        for header, seq in records:
            out.write(f">{header}\n")
            for i in range(0, len(seq), width):
                out.write(seq[i : i + width] + "\n")


def choose_weighted_index(lengths, rng: random.Random) -> int:
    total = sum(lengths)
    r = rng.randrange(total)
    acc = 0
    for i, L in enumerate(lengths):
        acc += L
        if r < acc:
            return i
    return len(lengths) - 1


def random_insertion_length(min_len: int, max_len: int, rng: random.Random) -> int:
    candidates = [L for L in range(min_len, max_len + 1) if L % 3 != 0]
    if not candidates:
        raise ValueError(
            f"No valid insertion lengths between {min_len} and {max_len} "
            f"that are not multiples of 3."
        )
    return rng.choice(candidates)


def make_polyA_inserted_genome(
    original: List[FASTARecord],
    n_insertions: int,
    min_len: int,
    max_len: int,
    rng: random.Random,
) -> List[FASTARecord]:
    records = deepcopy(original)
    seqs = [list(seq) for _, seq in records]

    for _ in range(n_insertions):
        lengths = [len(s) for s in seqs]
        idx = choose_weighted_index(lengths, rng)
        seq = seqs[idx]

        ins_len = random_insertion_length(min_len, max_len, rng)
        pos = rng.randrange(len(seq) + 1)
        seq[pos:pos] = ["A"] * ins_len

    mutated = []
    for (header, _), seq_list in zip(records, seqs):
        mutated.append((header, "".join(seq_list)))

    return mutated


def main():
    parser = argparse.ArgumentParser(
        description="Create synthetic genomes with random poly-A frameshift insertions."
    )
    parser.add_argument("input_fasta", help="Original genome FASTA")
    parser.add_argument(
        "-o", "--out-prefix", default="genome", help="Output prefix"
    )
    parser.add_argument(
        "--counts",
        type=str,
        default="10,50,100,500,1000,5000,10000",
        help="Comma-separated insertion counts",
    )
    parser.add_argument(
        "--min-len",
        type=int,
        default=1,
        help="Minimum insertion length",
    )
    parser.add_argument(
        "--max-len",
        type=int,
        default=10,
        help="Maximum insertion length",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed",
    )

    args = parser.parse_args()

    rng = random.Random(args.seed)
    counts = [int(x) for x in args.counts.split(",") if x.strip()]

    print(f"Reading original genome from {args.input_fasta}...", file=sys.stderr)
    original = read_fasta(args.input_fasta)

    print(f"Genome size: {sum(len(s) for _, s in original):,} bp", file=sys.stderr)
    print(f"Insertion counts: {counts}", file=sys.stderr)
    print(
        f"Insertion length range: {args.min_len}–{args.max_len} "
        f"(excluding multiples of 3)",
        file=sys.stderr,
    )

    for n_ins in counts:
        mutated = make_polyA_inserted_genome(
            original, n_ins, args.min_len, args.max_len, rng
        )

        out_path = f"{args.out_prefix}.polyA_{n_ins}.fa"
        labeled = [(f"{hdr}|polyA_{n_ins}", seq) for hdr, seq in mutated]
        write_fasta(labeled, out_path)

        print(
            f"Wrote {out_path} "
            f"(+~{n_ins * ((args.min_len + args.max_len) // 2)} bp expected)",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
