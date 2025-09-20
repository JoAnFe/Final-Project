import hmac, hashlib, os
from hashlib import sha256
from typing import Tuple

def derive_device_psk(device_mac: str, enrollment_salt: bytes) -> bytes:
    """
    Fallback software KDF (stand-in for PUF FE KDF):
    PSK = HKDF-SHA256( IKM=device_mac, salt=enrollment_salt, info="SMART-AGRI-PSK", L=32 )
    """
    prk = hmac.new(enrollment_salt, device_mac.encode(), hashlib.sha256).digest()
    t = b""
    okm = b""
    info = b"SMART-AGRI-PSK"
    while len(okm) < 32:
        t = hmac.new(prk, t + info + b"\x01", hashlib.sha256).digest()
        okm += t
    return okm[:32]

if __name__ == "__main__":
    salt = os.urandom(16)
    print(derive_device_psk("AA:BB:CC:DD:EE:FF", salt).hex())