# security.py
import os
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

MAGIC = b"AESGCMv1"
SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
KEY_SIZE = 32
PBKDF2_ITERS = 100_000
CHUNK_SIZE = 64 * 1024

def derive_key(passphrase: str, salt: bytes) -> bytes:
    return PBKDF2(passphrase.encode('utf-8'), salt, dkLen=KEY_SIZE, count=PBKDF2_ITERS, hmac_hash_module=SHA256)

def encrypt_file(in_path: str, out_path: str, passphrase: str):
    salt = get_random_bytes(SALT_SIZE)
    key = derive_key(passphrase, salt)
    nonce = get_random_bytes(NONCE_SIZE)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    with open(in_path, 'rb') as fin, open(out_path, 'wb') as fout:
        fout.write(MAGIC)
        fout.write(salt)
        fout.write(nonce)
        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk: break
            ct = cipher.encrypt(chunk)
            fout.write(ct)
        tag = cipher.digest()
        fout.write(tag)

def decrypt_file(in_path: str, out_path: str, passphrase: str):
    filesize = os.path.getsize(in_path)
    header_len = len(MAGIC) + SALT_SIZE + NONCE_SIZE
    if filesize < header_len + TAG_SIZE:
        raise ValueError("Input file too small.")

    with open(in_path, 'rb') as fin:
        magic = fin.read(len(MAGIC))
        if magic != MAGIC: raise ValueError("Invalid file format.")
        
        salt = fin.read(SALT_SIZE)
        nonce = fin.read(NONCE_SIZE)
        key = derive_key(passphrase, salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        ciphertext_len = filesize - header_len - TAG_SIZE
        bytes_left = ciphertext_len
        
        with open(out_path, 'wb') as fout:
            while bytes_left > 0:
                to_read = min(CHUNK_SIZE, bytes_left)
                chunk = fin.read(to_read)
                if not chunk: raise ValueError("Unexpected EOF.")
                pt = cipher.decrypt(chunk)
                fout.write(pt)
                bytes_left -= len(chunk)
            
            tag = fin.read(TAG_SIZE)
            if len(tag) != TAG_SIZE: raise ValueError("Missing tag.")
            try:
                cipher.verify(tag)
            except ValueError:
                fout.close()
                os.remove(out_path)
                raise ValueError("Authentication failed (Data corrupted).")