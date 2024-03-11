from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15
from Crypto.Cipher import PKCS1_OAEP
import hmac
import os
import random
from hashlib import sha256

def crypto_hash(msg):
    return int(SHA256.new(msg.encode("utf-8")).hexdigest(), 16)

def keyed_hash(key, msg):
    return int(hmac.new(key.export_key(), msg.encode("utf-8"), sha256).hexdigest(), 16)

def rsa_encrypt_or_decrypt(msg, key):
    cipher = PKCS1_OAEP.new(key)
    if key.has_private():
        # Decryption
        return cipher.decrypt(msg)
    else:
        # Encryption
        return cipher.encrypt(msg)

def xor(a, b):
    a_int = int.from_bytes(a, byteorder='big')
    b_int = int.from_bytes(b, byteorder='big')
    result = a_int ^ b_int
    return result.to_bytes(max(len(a), len(b)), byteorder='big')

def sign(msg, signer_key, other_public_keys):
    ring_size = len(other_public_keys) + 1
    key = crypto_hash(msg)
    u = random.randint(0, pow(2, 1023)).to_bytes(128, byteorder='big')
    v = [b'0' * 128] * ring_size
    v[0] = keyed_hash(signer_key, u.hex()).to_bytes(128, byteorder='big')

    s = [b'0' * 128] + [random.randint(0, pow(2, 1023)).to_bytes(128, byteorder='big') for _ in range(1, ring_size)]
    for i in range(1, ring_size):
        enc = rsa_encrypt_or_decrypt(xor(v[i - 1], s[i]), other_public_keys[i - 1])
        v[i] = keyed_hash(signer_key, enc.hex()).to_bytes(128, byteorder='big')
    s[0] = xor(v[ring_size - 1], u)

    signature = {
        'msg': msg,
        's': [int.from_bytes(s[i], byteorder='big') for i in range(ring_size)],
        'v': int.from_bytes(v[ring_size - 1], byteorder='big')
    }

    return signature

def verify(signature, public_keys):
    ring_size = len(public_keys)
    key = crypto_hash(signature['msg'])
    v = signature['v'].to_bytes(128, byteorder='big')
    s = [si.to_bytes(128, byteorder='big') for si in signature['s']]
    
    for i in range(ring_size):
        enc = rsa_encrypt_or_decrypt(s[i], public_keys[i])
        v = keyed_hash(public_keys[i], enc.hex()).to_bytes(128, byteorder='big')
    return int.from_bytes(v, byteorder='big') == signature['v']
