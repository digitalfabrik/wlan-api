import csv
import os
import subprocess
from io import StringIO

VOUCHER_PRIVATE_KEY = os.environ['VOUCHER_PRIVATE_KEY']
VOUCHER_CFG = os.environ['VOUCHER_CFG']
VOUCHER_BIN = os.environ['VOUCHER_BIN']


def generate_vouchers(roll, count):
    # WRONG CODE BELOW
    voucher = bytearray(os.urandom(13))

    alphabet = "2345678ABCDEFGHKLMNPQRSTUVWXYZ"
    output = ""

    for b in voucher:
        output = output + alphabet[b % len(alphabet)]

    return output


def generate_vouchers_pfsense(roll, count):
    roll_csv = subprocess.check_output(
        [VOUCHER_BIN, '-c', VOUCHER_CFG, '-p', VOUCHER_PRIVATE_KEY, str(roll), str(count)])

    vouchers_reader = csv.reader(StringIO(roll_csv.decode('utf-8')), delimiter=';', quotechar='"')
    vouchers = list(
        filter(lambda voucher: not voucher[0].startswith('#'), vouchers_reader))
    vouchers = [voucher[0].strip() for voucher in vouchers]

    return vouchers
