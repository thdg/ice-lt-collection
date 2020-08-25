#!/usr/bin/python3
"""
Randomly sample transcriptions with sound.

Author: Þorsteinn Daði Gunnarsson
"""

import argparse
import csv
import os
import subprocess

from random import shuffle

CONVERT_CMD = os.getenv(
    "CONVERT_CMD",
    'ffmpeg -nostats -hide_banner -y -i "{audio}" -ss {start} -to {stop} -q:a 0 -map a {output}',
)
PLAY_CMD = os.getenv(
    "PLAY_CMD", 'ffplay -nodisp -autoexit "{output}" -ss {start_f} -t {duration_f}'
)


def read_from_file(fname, header=True):
    """Get csv reader.

    Args: 
        fname: name of file
        header: whether or not the file has a header

    Returns:
        List of rows as dict or list
    """
    with open(fname) as fin:
        delimiter = "," if fname.endswith(".csv") else "\t"
        if header:
            reader = csv.DictReader(fin, delimiter=delimiter, quotechar='"')
        else:
            reader = csv.reader(fin, delimiter=delimiter, quotechar='"')
        return list(reader)


def parse_time(stamp):
    """Read time in seconds from HH:MM:SS:XXX.

    Args: 
        stamp: timestamp string

    Returns:
        Time in seconds
    """
    hours, minutes, seconds, _ = stamp.split(":")
    return int(hours) * 60 * 60 + int(minutes) * 60 + int(seconds)


def print_time(sec):
    """Format time from seconds to ffmpeg-utils format (HH:MM:SS.mmm).

    Args:
        sec: time in seconds

    Returns:
        Time in ffmpeg-utils format
    """
    hours, minutes, seconds = int(sec / 3600), int((sec % 3600) / 60), int(sec % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.000"


def play(
    row,
    audio_column,
    text_column,
    folder,
    column_start=None,
    column_end=None,
    convert=True,
):
    """Play audio file."""
    start = parse_time(row[column_start]) if column_start else None
    stop = parse_time(row[column_end]) if column_end else None
    duration = stop - start if start and stop else None

    start_f = print_time(start) if start else None
    stop_f = print_time(stop) if stop else None
    duration_f = print_time(duration) if duration else None

    output = audio = os.path.join(folder, row[audio_column])

    if convert:
        output = "output.mp3"
        subprocess.run(
            [
                CONVERT_CMD.format(
                    audio=audio,
                    start=start,
                    stop=stop,
                    duration=duration,
                    start_f=start_f,
                    stop_f=stop_f,
                    duration_f=duration_f,
                    output=output,
                )
            ],
            shell=True,
        )

    print("=" * 30)
    print(row[text_column])
    print("=" * 30, flush=True)
    subprocess.run(
        [
            PLAY_CMD.format(
                output=output,
                start=start,
                stop=stop,
                duration=duration,
                start_f=start_f,
                stop_f=stop_f,
                duration_f=duration_f,
            )
        ],
        shell=True,
    )


def main():
    """Randomly sample transcriptions with sound from file."""
    parser = argparse.ArgumentParser(
        description="Randomly sample transcriptions with sound."
    )
    parser.add_argument(
        "info", type=str, help="Info file containing transcriptions and file name"
    )
    parser.add_argument("audio_folder", type=str, help="Base folder for audio")
    parser.add_argument("audio_column", type=str, help="Column for sound file name")
    parser.add_argument("text_column", type=str, help="Column for transcription")

    parser.add_argument(
        "-c", "--count", type=int, default=20, help="Number of samples to play"
    )
    parser.add_argument(
        "-s", "--start", type=str, help="Start column name, whole file if skipped"
    )
    parser.add_argument(
        "-e", "--end", type=str, help="End column name, whole file if skipped"
    )

    parser.add_argument("--convert", dest="convert", action="store_true")
    parser.add_argument("--no-convert", dest="convert", action="store_false")
    parser.set_defaults(convert=False)

    parser.add_argument("--shuffle", dest="shuffle", action="store_true")
    parser.add_argument("--header", dest="header", action="store_true")

    args = parser.parse_args()
    info = args.info
    audio_folder = args.audio_folder
    count = args.count
    shuffle_samples = args.shuffle

    if args.header:
        audio_column = args.audio_column
        text_column = args.text_column
        start = args.start
        end = args.end
    else:
        audio_column = int(args.audio_column)
        text_column = int(args.text_column)
        start = int(args.start) if args.start else None
        end = int(args.end) if args.end else None

    if (start or end) and not (start and end):
        print("Needs both start and end times if either is present")
        exit()

    rows = read_from_file(info, header=args.header)

    if shuffle_samples:
        shuffle(rows)

    try:
        print("Playing random samples...")
        for row in rows[:count]:
            play(
                row,
                audio_column,
                text_column,
                folder=audio_folder,
                column_start=start,
                column_end=end,
                convert=args.convert,
            )
    except KeyboardInterrupt:
        print()  # Fail silently with newline on ^C


if __name__ == "__main__":
    main()
