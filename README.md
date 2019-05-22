# How to generate vouchers

* Get a csv from the pfsense with generated vouchers and place it in the `./rolls` directory
* Generate the voucher pdf: `python src/main.py rolls/vouchers_tatdf_roll31.csv rolls/vouchers_tatdf_roll31.csv.pdf`
* Place 4 A5 vouchers on one A4 page: `./to-a4.sh rolls/vouchers_tatdf_roll31.csv.pdf` and move generated file to `./rolls`
* Add ads: `/shuffle-pdfjoin.sh rolls/vouchers_tatdf_roll31.csv-2x2.pdf assets/Voucherwerbung_1.2.pdf`
* The `shuffled.pdf` PDF is ready for printing

# How to activate vouchers:

* Run `python sql-generator/import-to-sql.py rolls/vouchers_tatdf_roll31.csv`
* Insert voucher.sql into the database
