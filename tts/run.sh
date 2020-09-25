CORPUS=33
MAX=100
EXP=exp2

mkdir -p $EXP
python3 prep_lobe_data.py --max $MAX --rate 16000 --index $EXP/index.tsv data/$CORPUS/ $EXP/$CORPUS/
awk '{print $0}' $EXP/$CORPUS/*.lab | grep -o "[^ ,\.?-]*" | sort | uniq > $EXP/vocabulary.txt
g2p.py --model g2p.mdl --apply $EXP/vocabulary.txt --encoding utf-8 > $EXP/dictionary.tsv

../montreal-forced-aligner/bin/mfa_train_and_align -o $EXP/models -j 4 $EXP/33/ $EXP/dictionary.tsv $EXP/alignments

mkdir -p $EXP/final
python3 trim_sound.py $EXP/index.tsv $EXP/alignments/ $EXP/final
cp $EXP/$CORPUS/*.lab $EXP/final/

