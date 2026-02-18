#!/usr/bin/env python3
"""The Lich's Cursed Oracle — CBC token validation service."""

import os
import socket
import threading
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

KEY = os.urandom(16)
FLAG = os.environ.get("FLAG", "FantasyCTF{placeholder}")

BLOCK_SIZE = 16


def encrypt_token(plaintext: bytes) -> tuple[bytes, bytes]:
    iv = os.urandom(BLOCK_SIZE)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext, BLOCK_SIZE))
    return iv, ciphertext


def decrypt_token(iv: bytes, ciphertext: bytes) -> bytes:
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(ciphertext), BLOCK_SIZE)
    return plaintext


def handle_client(conn: socket.socket, addr):
    try:
        # Issue a guest token
        guest_token = b"role=guest;name=adventurer;access=vault"
        iv, ct = encrypt_token(guest_token)

        conn.sendall(b"=== The Lich's Cursed Oracle ===\n")
        conn.sendall(b"You have been issued an access token.\n")
        conn.sendall(f"IV:  {iv.hex()}\n".encode())
        conn.sendall(f"CT:  {ct.hex()}\n".encode())
        conn.sendall(b"\nSubmit a forged token to gain admin access.\n")
        conn.sendall(b"Format: <iv_hex>:<ct_hex>\n")
        conn.sendall(b"> ")

        data = conn.recv(4096).decode().strip()
        if ":" not in data:
            conn.sendall(b"Invalid format. The oracle is displeased.\n")
            return

        try:
            iv_hex, ct_hex = data.split(":", 1)
            new_iv = bytes.fromhex(iv_hex)
            new_ct = bytes.fromhex(ct_hex)
        except (ValueError, Exception):
            conn.sendall(b"Corrupted input. The oracle rejects your offering.\n")
            return

        try:
            decrypted = decrypt_token(new_iv, new_ct)
        except Exception:
            conn.sendall(b"Decryption failed. The token is cursed beyond repair.\n")
            return

        token_str = decrypted.decode(errors="replace")
        conn.sendall(f"Decrypted token: {token_str}\n".encode())

        if "role=admin" in token_str:
            conn.sendall(
                f"Access granted. The vault opens before you.\n{FLAG}\n".encode()
            )
        else:
            conn.sendall(b"Access denied. You are not worthy.\n")

    except Exception as e:
        conn.sendall(f"Oracle error: {e}\n".encode())
    finally:
        conn.close()


def main():
    host = "0.0.0.0"
    port = 1337
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Oracle listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    main()
