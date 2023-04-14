from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA224
from Crypto.Cipher import PKCS1_OAEP  # RSA with padding
from Crypto.Util.Padding import pad, unpad


def encrypt_aes(message, cipher_info):
    if cipher_info["block_cipher"] == "CBC":
        cipher = AES.new(cipher_info["session_key"], AES.MODE_CBC, cipher_info["initial_vector"])
    else:
        cipher = AES.new(cipher_info["session_key"], AES.MODE_ECB)

    ciphertext = cipher.encrypt(pad(bytes(message, 'utf-8'), AES.block_size))
    return ciphertext


def decrypt_aes(ciphertext, cipher_info):
    if cipher_info["block_cipher"] == "CBC":
        cipher = AES.new(cipher_info["session_key"], AES.MODE_CBC, cipher_info["initial_vector"])
    else:
        cipher = AES.new(cipher_info["session_key"], AES.MODE_ECB)

    message = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return message.decode(encoding='utf-8')


def encrypt_rsa(message, public_key):
    cipher = PKCS1_OAEP.new(public_key)
    ciphertext = cipher.encrypt(message)

    return ciphertext


def decrypt_rsa(ciphertext, private_key):
    cipher = PKCS1_OAEP.new(private_key)
    message = cipher.decrypt(ciphertext)
    return message


def create_mac(message, private_key):
    h = SHA224.new()
    h.update(bytes(message, 'utf-8'))
    byte_hash = h.digest()
    mac = encrypt_rsa(byte_hash, private_key)
    return mac


def validate_mac(message, public_key, mac):
    h = SHA224.new()
    h.update(bytes(message, 'utf-8'))
    byte_hash = h.digest()
    recived_byte_hash = decrypt_rsa(mac, public_key)

    return byte_hash == recived_byte_hash


def gen_key_rsa(key_length):
    if key_length != 1024 and key_length != 2048 and key_length != 3072 and key_length != 4096:
        raise ValueError('RSA key length should be equal to 1024 or 2048 or 3072 or 4096')
    key = RSA.generate(key_length)
    private_key = key
    public_key = key.public_key()

    return private_key, public_key


def gen_key_rsa_files(key_length, public_key_file, private_key_file):
    private_key, public_key = gen_key_rsa(key_length)

    with open(public_key_file, 'wb') as f:
        f.write(public_key.exportKey())

    with open(private_key_file, 'wb') as f:
        f.write(private_key.exportKey())
