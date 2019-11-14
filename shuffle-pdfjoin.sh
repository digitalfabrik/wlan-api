#!/bin/bash
VOUCHER_PDF=$1
VOUCHER_PDF_PAGES=50
ADS_PDF=$2
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

pdfjoin ${PAGES[@]} --outfile print-me.pdf --paper a5paper --rotateoversize false
