#!/bin/bash

val="$1"
if [ -z "$*" ]; then

# Enter a validator HEX ID to calculate the min/max/average
# number of validators that miss that validator's blocks
# or enter no parameter to get the average for all
# missed blocks for each validator.

logpath="/path/to/log.txt"

cat $logpath | cut -f 4 -d ',' | grep -v "#" | \
awk 'NR == 1 { max=$1; min=$1; sum=0 } {if ($1>max) max=$1; if ($1<min) min=$1; sum+=$1;} \
END {printf "Min: %d\tMax: %d\tAverage: %f\n", min, max, sum/NR}'

else

cat $logpath | grep $val | grep -v "#" |cut -f 4 -d ',' | \
awk 'NR == 1 { max=$1; min=$1; sum=0 } {if ($1>max) max=$1; if ($1<min) min=$1; sum+=$1;} \
END {printf "Min: %d\tMax: %d\tAverage: %f\n", min, max, sum/NR}'

fi
