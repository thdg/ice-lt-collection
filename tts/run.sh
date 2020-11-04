CORPUS=267
MAX=20000
EXP=$(pwd)/full267
G2P=/media/thorsteinn/THOR/data/ipd_clean_slt2018.mdl
MFA=/home/thorsteinn/ru/t1/montreal-forced-aligner

base_dir=$(dirname $0)

mkdir -p $EXP
python3 $base_dir/prep_lobe_data.py --max $MAX --rate 16000 --index $EXP/index.tsv data/$CORPUS/ $EXP/$CORPUS/
awk '{print $0}' $EXP/$CORPUS/*.lab | grep -o "[^ ,\.?-]*" | sort | uniq > $EXP/vocabulary.txt
python -m g2p --model $G2P --apply $EXP/vocabulary.txt --encoding utf-8 > $EXP/dictionary.tsv

$MFA/bin/mfa_train_and_align -o $EXP/models -j 4 $EXP/$CORPUS/ $EXP/dictionary.tsv $EXP/alignments

mkdir -p $EXP/final
python3 $base_dir/trim_sound.py $EXP/index.tsv $EXP/alignments/$CORPUS $EXP/final
cp $EXP/$CORPUS/*.lab $EXP/final/

