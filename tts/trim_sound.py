import argparse
import csv
import os

from textgrid import TextGrid


MAX_PADDING = 300
MAX_PAUSE = 300


def main():
    parser = argparse.ArgumentParser(description='.')
    parser.add_argument('index', type=str, help='')
    parser.add_argument('alignments', type=str, help='')
    parser.add_argument('output', type=str, help='')
    parser.add_argument('--max-padding', type=int, default=300, help='')
    parser.add_argument('--max-pause', type=int, default=300, help='')
    parser.add_argument('--rate', type=int, default=44100, help='')

    args = parser.parse_args()

    max_padding = args.max_padding / 1000
    max_pause = args.max_pause / 1000

    with open(args.index) as fi:
        index = csv.reader(fi, delimiter="\t")
        for line in index:
            try:
                rid = line[0]
                tg = TextGrid.fromFile(os.path.join(args.alignments, rid + ".TextGrid"))
                first = tg[0][0]
                last = tg[0][-1] 
                assert first.mark == "", "ERROR: Alignment does not start with a silence"
                assert last.mark == "", "ERROR: Alignment does not end with a silence"
                start = max(0, first.maxTime - max_padding)
                end = min(last.minTime +  max_padding, last.maxTime)
                cuts = []
                for interval in tg[0][1:-1]:
                    time = (interval.maxTime - interval.minTime)
                    if interval.mark == "" and time > max_pause:
                        cuts.extend((
                            interval.minTime + max_pause / 2,
                            interval.maxTime - max_pause / 2,
                        ))
                cuts = [start] + cuts + [end]
                lengths = [cuts[0]] + [b - a for a, b in zip(cuts[:-1], cuts[1:])]
                print(rid, cuts)
                assert len(cuts) % 2 == 0, "ERROR: Odd number of cuts"
                c = " ".join(map(lambda s: f"{s:.2f}", lengths))
                output = os.path.join(args.output, rid + ".wav")
                sox_call = f"sox {line[1]} {output} rate {args.rate} trim {c}"
                print(sox_call)
                os.system(sox_call)
            except Exception as e:
                print("TextGrid not found probably", e)


if __name__ == "__main__":
    main()
