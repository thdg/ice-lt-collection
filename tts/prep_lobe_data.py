import os
import uuid
import argparse


def normalize(transcription):
    transcription = transcription\
        .replace("H.Í.", "H Í")\
        .replace("OJ", "ó djey")\
        .replace("EmJ", "em djay")\
        .replace("ÁM", "Á M")\
        .replace(", ", " ")\
        .replace(",", " ")\
        .replace(".", "")\
        .replace("!", "")\
        .replace("?", "")\
        .replace(":", "")\
        .replace("\"", "")\
        .replace("'", "")\
        .replace("(", "")\
        .replace(")", "")\
        .replace("%", "")\
        .replace("„", "")\
        .replace(" - ", " ")\
        .replace("-", " ")\
        .replace("“", "")\
        .replace(" – ", " ")\
        .replace("–", " ")\
        .replace(";", "")\
        .lower()
    return transcription + "\n"



def main():
    parser = argparse.ArgumentParser(description='Create corpus for aligning from LOBE format.')
    parser.add_argument('data', type=str, help='Full path to dataset')
    parser.add_argument('corpus', type=str, help='Destination data folder')
    parser.add_argument('--max', type=int, help='sum the integers (default: find the max)')
    parser.add_argument('--rate', type=int, default=16000, help='Output sample rate (default: 16000')
    parser.add_argument('--index', type=str, help='Index file')

    args = parser.parse_args()
    data = args.data
    corpus = args.corpus
    n = args.max

    try:
        os.mkdir(corpus)
    except FileExistsError:
        print("Corpus folder already exists. Exiting.")
        exit()

    f = open(os.path.join(data, "index.tsv"))
    
    lines = f.readlines()
    if n:
        if len(lines) < n:
            print("Subset specified is larger than the dataset, using full corpus.")
        lines = lines[:n]

    index = None
    if args.index:
        index = open(args.index, "w")

    for l in lines:
        speaker, recording, text = l.strip().split("\t")

        recording_id, _ = os.path.splitext(recording)
        audio_file = os.path.join(data, "audio", speaker, recording) 
        new_audio_file = os.path.join(corpus, recording_id + ".wav")
        print(audio_file, new_audio_file)
        os.system(f"sox {audio_file} -c 1 -r 16000 {new_audio_file}")
        
        text_file = os.path.join(data, "text", text) 
        new_text_file = os.path.join(corpus, recording_id + ".lab")
        print(text_file, new_text_file)
        with open(text_file) as fi:
            with open(new_text_file, "w") as fo:
                text = fi.read()
                norm_text = normalize(text)
                fo.write(norm_text)
        # os.system(f"cp {text_file} {new_text_file}")
        if index:
            index.write("\t".join([
                recording_id,
                audio_file,
                new_audio_file,
                text_file,
                new_text_file,
                text.strip(),
                norm_text.strip(),
            ]) + "\n")

if __name__ == "__main__":
    main()
