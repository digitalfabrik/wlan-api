import base64
import random
import hmac


def generate_vouchers(roll, count, key, alphabet, length):
    mac = hmac.new(base64.b64decode(key), roll.to_bytes(2, byteorder='little'), "SHA256")
    random.seed(mac.digest())

    vouchers = []
    for i in range(count):
        output = "".join(random.choices(alphabet, k=length))
        vouchers.append(output)

    return vouchers
