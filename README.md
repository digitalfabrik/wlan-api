# How to generate vouchers

* Generate vouchers using the `voucher.c` file in `sql-generator`: `./voucher -p key.pem 32 200 > vouchers_tatdf_roll32.csv`
* Generate the voucher pdf: `python voucher-pdf-generator/main.py rolls/vouchers_tatdf_roll31.csv rolls/vouchers_tatdf_roll31.csv.pdf`
* Place 4 A5 vouchers on one A4 page: `./to-a4.sh rolls/vouchers_tatdf_roll31.csv.pdf` and move generated file to `./rolls`
* Add ads: `./shuffle-pdfjoin.sh rolls/vouchers_tatdf_roll31.csv-2x2.pdf assets/Voucherwerbung_1.2.pdf`
* The `print-me.pdf` PDF is ready for printing

# How to activate vouchers:

* Run `python sql-generator/import-to-sql.py rolls/vouchers_tatdf_roll31.csv`
* Insert voucher.sql into the database
