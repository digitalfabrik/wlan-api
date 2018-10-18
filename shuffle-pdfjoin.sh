#!/bin/bash
VOUCHER_PDF=vouchers_tatdf_roll24.csv-2x2.pdf
VOUCHER_PDF_PAGES=50
ADS_PDF=ads-2x2.pdf
ADS_PDF_PAGES=1

PAGES=()
for k in $(seq 1 ${VOUCHER_PDF_PAGES}); do
    PAGES+=($VOUCHER_PDF);
    PAGES+=($k);
    PAGES+=($ADS_PDF);
    AD_PAGE_MODULO=$(($ADS_PDF_PAGES - 1))
    if [ "$AD_PAGE_MODULO" -eq "0" ]; then
        PAGES+=(1);
    else
        PAGES+=($(($k % $AD_PAGE + 1)));
    fi
done

pdfjoin ${PAGES[@]} --outfile shuffled.pdf --paper a5paper --rotateoversize false
