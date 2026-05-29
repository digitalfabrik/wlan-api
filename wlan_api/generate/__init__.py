import base64
import random
import hmac


def generate_vouchers(roll, count, key, alphabet, length):
    if not 0 <= roll < (1 << 16):
        raise ValueError(f"roll out of range [0, 65535]: {roll}")
    if not 0 <= count < (1 << 16):
        raise ValueError(f"count out of range [0, 65535]: {count}")

    vouchers = []
    for i in range(count):
        mac = hmac.new(base64.b64decode(key),
                       roll.to_bytes(2, byteorder='little') + i.to_bytes(2, byteorder="little"),
                       "SHA256")
        random.seed(mac.digest())
        output = "".join(random.choices(alphabet, k=length))
        vouchers.append(output)

    return vouchers
