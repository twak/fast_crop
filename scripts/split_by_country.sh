cat argentina.txt  > other.txt
cat bangladesh.txt >> other.txt
cat brazil.txt     >> other.txt
cat cyprus.txt     >> other.txt
cat czechia.txt    >> other.txt
cat denmark.txt    >> other.txt
cat germany.txt    >> other.txt
cat greece.txt     >> other.txt
cat ireland.txt    >> other.txt
cat macedonia.txt  >> other.txt
cat poland.txt     >> other.txt
cat thailand.txt   >> other.txt

cat misc.txt       >> other.txt

shuf all.txt > all_shuf.txt

shuf all.txt > all_shuf.txt
head -n 4501 all_shuf.txt > train.txt
tail -n 4501 all_shuf.txt > test.txt

shuf all.txt > all_shuf.txt
head -n 8102 all_shuf.txt > train_10.txt
tail -n 900 all_shuf.txt > test_10.txt

for value in uk austria usa egypt other all
do
  shuf $value.txt > ${value}_shuf.txt
  head -n 1200  ${value}_shuf.txt  > ${value}_train.txt
  tail -n 300   ${value}_shuf.txt > ${value}_test.txt
  rm ${value}_shuf.txt
done


