#!/bin/bash

#get parameters
iwlist wlp5s0 scan | grep 'ESSID\|Quality\|Channel\|Frequency\|Encryption' > data

#split quality and signal level
sed -i 's/Signal level/\nSignal level/g' data

#get rid of all characters but numbers and ESSID

#replace "=" with ":"
sed -i 's/=/:/g' data
#replace """ with ""
sed -i 's/"//g' data
#replace "/" with ","
sed -i 's/\//,/g' data
#deletes everything after GHz 
sed -i 's/.GHz*//' data
#deletes everything in ()
sed -i -e 's/([^()]*)//g' data
#deletes everything after dbm 
sed -i 's/.dBm*//' data

#remove leading spaces
sed -i -e 's/^[ \t]*//' data
#adds --- at the end of each individual network
sed -i 's/^ESSID.*/&---/' data
#deletes everything before the  : 
sed -i 's/^.*://' data
#remove trailng spaces
sed -i 's/[ \t]*$//' data


#add ","
sed -i 's/$/,/g' data
#deletes \n
tr '\n' ' ' < data > data.csv
#removes spaces after ,
sed -i 's/, /,/g' data.csv

#adds a new line at the begining of each network
sed -i 's/---,/\n/g' data.csv
#add new line at the begining
sed -i '1s/^/\n/' data.csv

#adds heather
echo "$(echo -n 'Channel,Frequency,Quality,Quality Max,Signal Level,Encryption,SSID'; cat data.csv)" > data.csv

#deletes last line
sed -i '$d' data.csv

#genrate json
cat data.csv| python3 -c 'import csv, json, sys; print(json.dumps([dict(r) for r in csv.DictReader(sys.stdin)]))' > wifi.json
