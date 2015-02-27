#!/bin/bash
echo Compile with gcc -O2
rm -f *.bin
rm -f ../scattnlay
#g++ -Ofast -std=c++11 compare.cc nmie.cc nmie-wrapper.cc -lm -lrt -o scattnlay.bin -static
# g++ -Ofast -std=c++11 compare.cc nmie.cc nmie-wrapper.cc -lm -lrt -o scattnlay-pg.bin -static -pg

#google profiler
# g++ -Ofast -std=c++11 compare.cc nmie.cc nmie-wrapper.cc -lm -lrt -o scattnlay.bin /usr/lib/libtcmalloc.so.4 -fno-builtin-malloc -fno-builtin-calloc -fno-builtin-realloc -fno-builtin-free 
 g++ -Ofast -std=c++11 compare.cc nmie.cc nmie-wrapper.cc -lm -lrt -o scattnlay.bin -ltcmalloc -fno-builtin-malloc -fno-builtin-calloc -fno-builtin-realloc -fno-builtin-free 

#clang++ -g -O1 -fsanitize=address  -fno-optimize-sibling-calls -fno-omit-frame-pointer -std=c++11 compare.cc nmie.cc nmie-wrapper.cc -lm -lrt -o scattnlay.bin

cp scattnlay.bin ../scattnlay
cp scattnlay-pg.bin ../scattnlay-pg
cd tests/shell
# for file in `ls *.sh`;  do 
#     if [ "$file" != "test03.sh" ]; then
# 	./$file > /dev/null
# 	echo $file
#     fi
# done
 PROGRAM='../../../scattnlay'
# time ASAN_SYMBOLIZER_PATH=/usr/bin/llvm-symbolizer-3.4 
#time 
time $PROGRAM -l 5 0.4642 1.8000 1.7000 0.7114 0.8000 0.7000 0.7393 1.2000 0.0900 0.9168 2.8000 0.2000 1.0000 1.5000 0.4000  -t 0.0 90.0 5 -c test01

echo valgring
# valgrind --tool=callgrind $PROGRAM -l 5 0.4642 1.8000 1.7000 0.7114 0.8000 0.7000 0.7393 1.2000 0.0900 0.9168 2.8000 0.2000 1.0000 1.5000 0.4000  -t 0.0 90.0 5 -c test01
# rm out.dot
# ./gprof2dot.py --output=out.dot --format=callgrind callgrind.out.*
# mv callgrind.out.* callgrind
# dot -Tsvg out.dot -o graph.svg

# rm *.aprof
# /home/mmedia/soft/aprof-0.2.1/inst/bin/valgrind --tool=aprof  $PROGRAM -l 5 0.4642 1.8000 1.7000 0.7114 0.8000 0.7000 0.7393 1.2000 0.0900 0.9168 2.8000 0.2000 1.0000 1.5000 0.4000  -t 0.0 90.0 5 -c test01


# rm gmon.out
# rm analysis.txt
# PROGRAM='../../../scattnlay-pg'
# time $PROGRAM -l 5 0.4642 1.8000 1.7000 0.7114 0.8000 0.7000 0.7393 1.2000 0.0900 0.9168 2.8000 0.2000 1.0000 1.5000 0.4000  -t 0.0 90.0 5 -c test01
# gprof $PROGRAM gmon.out > analysis.txt

# repeats=30
# echo Run test for $repeats times
# time for i in `seq $repeats`; do ./test01.sh; done
# echo Run test with original binary for $repeats times
# cp ../../../scattnlay-0.3.0 ../../../scattnlay
# time for i in `seq $repeats`; do ./test01.sh; done
