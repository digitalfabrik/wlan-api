#!/bin/bash
roll=$1
count=$2

./sql-generator/voucher -c ./sql-generator/voucher.cfg -p ./sql-generator/key.pem $roll $count > rolls/vouchers_tatdf_roll${roll}.csv

echo "Generating vouchers"
python src/main.py rolls/vouchers_tatdf_roll${roll}.csv rolls/vouchers_tatdf_roll${roll}.csv.pdf

echo "Converting every 4 A5 vouchers to A4"
./to-a4.sh rolls/vouchers_tatdf_roll${roll}.csv.pdf

echo "Adding ads"
./shuffle-pdfjoin.sh rolls/vouchers_tatdf_roll${roll}.csv-2x2.pdf ads/Voucherwerbung_1.3-2x2.pdf

echo "Generating SQL"
python ./sql-generator/import-to-sql.py rolls/vouchers_tatdf_roll${roll}.csv rolls/vouchers_tatdf_roll${roll}.sql

