import argparse
import csv
import os
import subprocess

from random import shuffle

CONVERT_CMD = os.getenv("CONVERT_CMD", 'ffmpeg -nostats -hide_banner -y -i "{audio}" -ss {start} -to {stop} -q:a 0 -map a {output}')
PLAY_CMD = os.getenv("PLAY_CMD", 'ffplay -nodisp -autoexit "{output}" -ss {start_f} -t {duration_f}')


def read_from_file(fname):
    with open(fname) as fin:
        reader = csv.DictReader(fin, delimiter=",", quotechar="\"")
        return list(reader)


def parse_time(stamp):
    """
    Accepts time in format HH:MM:SS:XXX
    and returns the time in whole seconds
    """
    hours, minutes, seconds, _ = stamp.split(":")
    return int(hours) * 60*60 + int(minutes) * 60 + int(seconds)


def print_time(sec):
    """
    Prints out time in HH:MM:SS.XXX format from seconds
    """
    hours, minutes, seconds = int(sec / 3600), int((sec % 3600) / 60), int(sec % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.000"


def play_part(row, audio_column, text_column, folder, column_start=None, column_end=None, convert=True):
    start = parse_time(row[column_start])
    stop = parse_time(row[column_end])
    duration = stop - start

    start_f = print_time(start)
    stop_f = print_time(stop)
    duration_f = print_time(duration)

    output = audio = os.path.join(folder, row[audio_column])
    
    if convert:
        output = "output.mp3"
        subprocess.run([CONVERT_CMD.format(
            audio=audio,
            start=start,
            stop=stop,
            duration=duration,
            start_f=start_f,
            stop_f=stop_f,
            duration_f=duartion_f,
            output=output,
        )], shell=True)

    print("="*30)
    print(row[text_column])
    print("="*30, flush=True)
    subprocess.run([PLAY_CMD.format(
        output=output,
        start=start,
        stop=stop,
        duration=duration,
        start_f=start_f,
        stop_f=stop_f,
        duration_f=duration_f,
    )], shell=True)


def main():
    parser = argparse.ArgumentParser(description='Randomly sample transcriptions with sound.')
    parser.add_argument('info', type=str, help='Info file containing transcriptions and file name')
    parser.add_argument('audio_folder', type=str, help='Base folder for audio')
    parser.add_argument('audio_column', type=str, help='Column for sound file name')
    parser.add_argument('text_column', type=str, help='Column for transcription')

    parser.add_argument('-c', '--count', type=int, default=20, help='Number of samples to play')
    parser.add_argument('-s', '--start', type=str, help='Start column name, whole file if skipped')
    parser.add_argument('-e', '--end', type=str, help='End column name, whole file if skipped')

    parser.add_argument('--convert', dest='convert', action='store_true')
    parser.add_argument('--no-convert', dest='convert', action='store_false')
    parser.set_defaults(convert=False)

    args = parser.parse_args()
    info = args.info
    audio_folder = args.audio_folder
    audio_column = args.audio_column
    text_column = args.text_column
    count = args.count
    shuffle_samples = True

    start = args.start
    end = args.end

    if (start or end) and not (start and end):
        print("Needs both start and end times if either is present")
        exit()
    
    rows = read_from_file(info)

    if shuffle_samples:
        shuffle(rows)

    print("Playing random samples...")
        
    for row in rows[:count]:
        play_part(row, audio_column, text_column, folder=audio_folder, column_start=start, column_end=end, convert=args.convert)


if __name__ == "__main__":
    main()


# python3 review.py "data/SÍM-gögn_20200703 Fasi2 byrjun.csv" "data/Upptokur-fasi2-byrjun/" "skra" "texti" -c 20 -s "byrjar" -e "endar"