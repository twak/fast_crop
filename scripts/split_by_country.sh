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

for value in uk austria usa egypt other all
do
  shuf $value.txt > ${value}_shuf.txt
  head -n 1200  ${value}_shuf.txt > ${value}_tmp.txt
  tail -n 176   ${value}_tmp.txt  > ${value}_val.txt
  head -n 1024  ${value}_tmp.txt  > ${value}_train.txt
  tail -n 300   ${value}_shuf.txt > ${value}_test.txt
  rm ${value}_tmp.txt
done

