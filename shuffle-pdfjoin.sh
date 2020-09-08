#!/bin/bash
VOUCHER_PDF=$2
VOUCHER_PDF_PAGES=$3
ADS_PDF=$1
ADS_PDF_PAGE=1

PAGES=()
for k in $(seq 1 ${VOUCHER_PDF_PAGES}); do
    PAGES+=($VOUCHER_PDF);
    PAGES+=($k);
    PAGES+=($ADS_PDF);
    PAGES+=($ADS_PDF_PAGE);
done

pdfjam ${PAGES[@]} --outfile /dev/stdout --paper a4paper --rotateoversize false
