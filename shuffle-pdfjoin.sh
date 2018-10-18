#!/bin/bash
VOUCHER_PDF=vouchers_tatdf_roll24.csv.pdf
VOUCHER_PDF_PAGES=200
ADS_PDF=ads.pdf
ADS_PDF_PAGES=4

PAGES=()
for k in $(seq 1 ${VOUCHER_PDF_PAGES}); do
    PAGES+=($VOUCHER_PDF);
    PAGES+=($k);
    PAGES+=($ADS_PDF);
    PAGES+=($(($k % ($ADS_PDF_PAGES - 1) + 1)));
done

pdfjoin ${PAGES[@]} --outfile shuffled.pdf --paper a5paper --rotateoversize false
