# security.py
import os
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Hash import SHA256

# --- Constants for the new professional file format ---
MAGIC = b"AESGCMv1"      # 8 bytes identifier to recognize our encrypted files
SALT_SIZE = 16
NONCE_SIZE = 12         # Recommended 96-bit for GCM
TAG_SIZE = 16
KEY_SIZE = 32           # 256-bit key
PBKDF2_ITERS = 100_000  # Iterations for key derivation
CHUNK_SIZE = 64 * 1024  # Process files in 64 KB chunks

def derive_key(passphrase: str, salt: bytes) -> bytes:
    """Derives a strong key from a passphrase using PBKDF2."""
    return PBKDF2(passphrase.encode('utf-8'), salt, dkLen=KEY_SIZE, count=PBKDF2_ITERS, hmac_hash_module=SHA256)

def encrypt_file(in_path: str, out_path: str, passphrase: str):
    """Encrypts a file from in_path to out_path using a streaming approach."""
    salt = get_random_bytes(SALT_SIZE)
    key = derive_key(passphrase, salt)
    nonce = get_random_bytes(NONCE_SIZE)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    with open(in_path, 'rb') as fin, open(out_path, 'wb') as fout:
        # Write the professional header: magic + salt + nonce
        fout.write(MAGIC)
        fout.write(salt)
        fout.write(nonce)

        # Encrypt in chunks (streaming)
        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break
            ct = cipher.encrypt(chunk)
            fout.write(ct)

        # Finalize and get the authentication tag
        tag = cipher.digest()
        fout.write(tag)

def decrypt_file(in_path: str, out_path: str, passphrase: str):
    """Decrypts a file from in_path to out_path, verifying its integrity."""
    filesize = os.path.getsize(in_path)
    header_len = len(MAGIC) + SALT_SIZE + NONCE_SIZE
    if filesize < header_len + TAG_SIZE:
        raise ValueError("Input file is too small to be a valid encrypted file.")

    with open(in_path, 'rb') as fin:
        # Read and verify the header
        magic = fin.read(len(MAGIC))
        if magic != MAGIC:
            raise ValueError("Invalid file format or not an encrypted file (bad magic number).")
        
        salt = fin.read(SALT_SIZE)
        nonce = fin.read(NONCE_SIZE)
        
        # Derive the key and set up the cipher
        key = derive_key(passphrase, salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
        
        # Calculate ciphertext size
        ciphertext_len = filesize - header_len - TAG_SIZE
        bytes_left = ciphertext_len
        
        # Decrypt in chunks and write to output file
        with open(out_path, 'wb') as fout:
            while bytes_left > 0:
                to_read = min(CHUNK_SIZE, bytes_left)
                chunk = fin.read(to_read)
                if not chunk:
                    raise ValueError("Unexpected end of file while reading ciphertext.")
                
                pt = cipher.decrypt(chunk)
                fout.write(pt)
                bytes_left -= len(chunk)
            
            # Read the tag from the end of the file
            tag = fin.read(TAG_SIZE)
            if len(tag) != TAG_SIZE:
                raise ValueError("Authentication tag is missing or incomplete.")
            
            # Verify the tag (this will raise ValueError on mismatch)
            try:
                cipher.verify(tag)
            except ValueError:
                # If verification fails, delete the partially written (and incorrect) output file
                fout.close()
                os.remove(out_path)
                raise ValueError("Authentication failed: The data is corrupted or the password is incorrect.")