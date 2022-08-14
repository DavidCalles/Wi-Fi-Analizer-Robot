#!/bin/bash

#PROJECT_DIR='/home/davidcalles/Documents/Wi-Fi-Analizer-Robot/'
PROJECT_DIR=''
OUTPUT_DIR='Retrieve_Wi-Fi_Data/'

#get parameters
iwlist wlp5s0 scan | grep 'ESSID\|Quality\|Channel\|Frequency\|Encryption' > "${PROJECT_DIR}${OUTPUT_DIR}data.txt"

#split quality and signal level
sed -i 's/Signal level/\nSignal level/g' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"

#get rid of all characters but numbers and ESSID

#replace "=" with ":"
sed -i 's/=/:/g' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"
#replace """ with ""
sed -i 's/"//g' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"
#replace "/" with ","
sed -i 's/\//,/g' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"
#deletes everything after GHz 
sed -i 's/.GHz*//' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"
#deletes everything in ()
sed -i -e 's/([^()]*)//g' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"
#deletes everything after dbm 
sed -i 's/.dBm*//' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"

#remove leading spaces
sed -i -e 's/^[ \t]*//' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"
#adds --- at the end of each individual network
sed -i 's/^ESSID.*/&---/' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"
#deletes everything before the  : 
sed -i 's/^.*://' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"
#remove trailng spaces
sed -i 's/[ \t]*$//' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"


#add ","
sed -i 's/$/,/g' "${PROJECT_DIR}${OUTPUT_DIR}data.txt"
#deletes \n
tr '\n' ' ' < "${PROJECT_DIR}${OUTPUT_DIR}data.txt" > "${PROJECT_DIR}${OUTPUT_DIR}data.csv"
#removes spaces after ,
sed -i 's/, /,/g' "${PROJECT_DIR}${OUTPUT_DIR}data.csv"

#adds a new line at the begining of each network
sed -i 's/---,/\n/g' "${PROJECT_DIR}${OUTPUT_DIR}data.csv"
#add new line at the begining
sed -i '1s/^/\n/' "${PROJECT_DIR}${OUTPUT_DIR}data.csv"

#adds heather
echo "$(echo -n 'Channel,Frequency,Quality,Quality Max,Signal Level,Encryption,SSID'; cat ${PROJECT_DIR}${OUTPUT_DIR}data.csv)" > "${PROJECT_DIR}${OUTPUT_DIR}data.csv"

#deletes last line
#sed -i '$d' data.csv