import os
import uuid
import argparse

from prep_lobe_data import normalize

def main():
    parser = argparse.ArgumentParser(description='Create corpus for aligning from LOBE format.')
    parser.add_argument('alignments', type=str, help='Full path to alignments')
    parser.add_argument('corpus', type=str, help='Destination data folder')

    args = parser.parse_args()
    data = args.data
    corpus = args.corpus

    f = open(os.path.join(data, "index.tsv"))
    lines = f.readlines()

    norm2nat = dict()
    for l in lines:
        speaker, recording, text = l.strip().split("\t")

        text_file = os.path.join(data, "text", text) 
        with open(text_file) as fi:
            text = fi.read()
            norm_text = normalize(text).strip()
            norm2nat[norm_text] = text.strip()

    index = open(os.path.join(corpus, "index.tsv"))
    fixed = open(os.path.join(corpus, "index.nat.tsv"), "w")
    for l in index.readlines():
        rid, norm = l.split("\t")
        fixed.write("\t".join([
            rid,
            norm2nat[norm.strip()],
            norm.strip(),
        ]) + "\n")


if __name__ == "__main__":
    main()
