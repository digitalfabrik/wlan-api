#!/usr/bin/python

# This script ready a csv like:
# ABCD
# GHJK
# And create a SQL script to import this data into a radius db

import csv
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("voucher_csv")
args = parser.parse_args()

def read_imports(path):
    voucher_imports = []
    with open(path, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in reader:
            voucher_imports.append(row)
    return voucher_imports

voucher_imports = read_imports(args.voucher_csv)
with open("voucher.sql", "w") as text_file:
    for row in voucher_imports:
        voucher = row[0].strip()
        if voucher.startswith('#'):
            continue
        text_file.write("INSERT INTO radcheck (username, attribute, op, value) VALUES ('%s','Max-All-Session',':=','%s');\n" % (voucher, 36 * 24 * 60 * 60))
        text_file.write("INSERT INTO radcheck (username, attribute, op, value) VALUES ('%s','Cleartext-Password', ':=', 'dummy');\n" % (voucher))

