#!/bin/bash


#get parameters
iwlist wlp5s0 scan | grep 'ESSID\|Quality\|Channel\|Frequency\|Encryption' > /home/someone/Desktop/Network/RAW/data

#split quality and signal level
sed -i 's/Signal level/\nSignal level/g' /home/someone/Desktop/Network/RAW/data

#replace "=" with ":"
sed -i 's/=/:/g' /home/someone/Desktop/Network/RAW/data
#replace """ with ""
sed -i 's/"//g' /home/someone/Desktop/Network/RAW/data 

#remove leading spaces
sed -i -e 's/^[ \t]*//' /home/someone/Desktop/Network/RAW/data
#remove trailng spaces
sed -i 's/[ \t]*$//' /home/someone/Desktop/Network/RAW/data

#add ","
sed -i 's/$/,/g' /home/someone/Desktop/Network/RAW/data

#adds --- at the end of each individual network
sed -i 's/^ESSID.*/&---/' /home/someone/Desktop/Network/RAW/data
#deletes everything before the  : 
sed -i 's/^.*://' /home/someone/Desktop/Network/RAW/data

#deletes \n
tr '\n' ' ' < /home/someone/Desktop/Network/RAW/data > /home/someone/Desktop/Network/RAW/data.csv

#removes spaces after ,
sed -i 's/, /,/g' /home/someone/Desktop/Network/RAW/data.csv

#adds a new line at the begining of each network
sed -i $'s/,---/\\\n/g' /home/someone/Desktop/Network/RAW/data.csv
#add new line at the begining
sed -i '1s/^/\n/' /home/someone/Desktop/Network/RAW/data.csv

#adds heather
echo "$(echo -n 'Channel,Frequency,Quality,Signal Level,Encryption,SSID'; cat /home/someone/Desktop/Network/RAW/data.csv)" > /home/someone/Desktop/Network/RAW/data.csv

#deletes last line
sed -i '$d' /home/someone/Desktop/Network/RAW/data.csv

#remove leading spaces
sed -i -e 's/^[ \t]*//' /home/someone/Desktop/Network/RAW/data.csv

#genrate json
cat /home/someone/Desktop/Network/RAW/data.csv| python3 -c 'import csv, json, sys; print(json.dumps([dict(r) for r in csv.DictReader(sys.stdin)]))' > /home/someone/Desktop/Network/output/wifi.json

