import random
import hashlib
import struct
import base64
from StringIO import StringIO
from Crypto.Cipher import AES
from .version import VERSION

__title__ = 'SimpleAES'
__version__ = VERSION
__author__ = 'Vincent Driessen'
__license__ = 'BSD'
__copyright__ = 'Copyright 2012 Vincent Driessen'


def _random_noise(len):
    return ''.join(chr(random.randint(0, 0xFF)) for i in range(len))


class SimpleAES(object):
    def __init__(self, key):
        # First, generate a fixed-length key of 32 bytes (for AES-256)
        self._key = hashlib.sha256(key).digest()
        self.chunksize = 64 * 1024

    def encrypt(self, string):
        """Encrypts a string using AES-256."""
        # Generate a random IV
        iv = _random_noise(16)
        aes = AES.new(self._key, AES.MODE_CBC, iv)

        fin = StringIO(string)
        fout = StringIO()
        try:
            # Fixed-length data encoded in the encrypted string, first
            fout.write(struct.pack('<Q', len(string)))
            fout.write(iv)

            while True:
                chunk = fin.read(self.chunksize)
                chunk_len = len(chunk)
                if chunk_len == 0:
                    break  # done
                elif chunk_len % 16 != 0:
                    chunk += _random_noise(16 - chunk_len % 16)
                fout.write(aes.encrypt(chunk))
            cipherbytes = fout.getvalue()
        finally:
            fin.close()
            fout.close()

        return cipherbytes

    def decrypt(self, cipherbytes):
        """Decrypts a string using AES-256."""
        fin = StringIO(cipherbytes)
        fout = StringIO()

        try:
            input_size = struct.unpack('<Q', fin.read(struct.calcsize('Q')))[0]
            iv = fin.read(16)
            aes = AES.new(self._key, AES.MODE_CBC, iv)

            while True:
                chunk = fin.read(self.chunksize)
                if len(chunk) == 0:
                    break  # done
                fout.write(aes.decrypt(chunk))

            # truncate any padded random noise
            fout.truncate(input_size)

            text = fout.getvalue()
        finally:
            fin.close()
            fout.close()

        return text

    def base64_encrypt(self, string):
        """Encrypts a string using AES-256, but returns the result
        base64-encoded."""
        cipherbytes = self.encrypt(string)
        ciphertext = base64.b64encode(cipherbytes)
        return ciphertext

    def base64_decrypt(self, ciphertext):
        """Decrypts base64-encoded ciphertext using AES-256."""
        cipherbytes = base64.b64decode(ciphertext)
        plaintext = self.decrypt(cipherbytes)
        return plaintext


__all__ = ['SimpleAES']

if __name__ == '__main__':
    key = 'Som3 r4nd0mly g3nera4ted k3y!'
    aes = SimpleAES(key)
    for input_len in range(0, 128):
        for times in range(0, 3):
            input = _random_noise(input_len)
            ciphertext = aes.encrypt(input)
            text = aes.decrypt(ciphertext)
            assert text == input
    print 'All OK'
