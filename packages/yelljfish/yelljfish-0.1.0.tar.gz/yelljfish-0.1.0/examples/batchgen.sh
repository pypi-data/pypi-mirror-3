#!/bin/bash
outdir="$1"
prog="$2"

if [ ! "$prog" ] ; then
    prog="yelljfish"
fi

for i in {3..7} ; do
    for j in {3..7} ; do
        echo "$i starting points, $j runs."
        "$prog" -n $i -t $j "$outdir/$i-$j.png"
    done
done
