import os


def generate_code():
    voucher = bytearray(os.urandom(13))

    alphabet = "2345678ABCDEFGHKLMNPQRSTUVWXYZ"
    output = ""

    for b in voucher:
        output = output + alphabet[b % len(alphabet)]

    return output


print(generate_code())
