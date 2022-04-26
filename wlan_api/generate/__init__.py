import os
import random
import hmac

alphabet = "2345678ABCDEFGHKLMNPQRSTUVWXYZ"
length = 16
key = os.urandom(64)  # key is assumed to stay the same


def generate_vouchers(roll, count):
    mac = hmac.new(key, roll.to_bytes(2, byteorder='little'), "SHA256")
    random.seed(mac.digest())

    vouchers = []
    for i in range(count):
        output = "".join(random.choices(alphabet, k=length))
        vouchers.append(output)

    return vouchers
