#!/usr/bin/python3
import csv
import sys
import argparse
from io import BytesIO
from vpg.VoucherPrint import VoucherPrint

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generates vouchers.')
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('wb'),
                        default=sys.stdout)
    args = parser.parse_args()

    vouchers = []
    with args.infile as rollFile:
        roll = csv.reader(rollFile, delimiter=';', quotechar='"')
        vouchers = list(
            filter(lambda voucher: not voucher[0].startswith('#'), roll))
        vouchers = [voucher[0].strip() for voucher in vouchers]

    buffer = BytesIO()

    report = VoucherPrint(buffer, vouchers)
    pdf = report.print_vouchers()
    buffer.seek(0)

    with args.outfile as f:
        f.write(buffer.read())
