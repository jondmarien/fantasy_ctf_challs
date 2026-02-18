#!/usr/bin/env python3
"""The Arcane Protocol — TCP handshake server requiring HMAC-SHA256 authentication."""

import os
import hmac
import hashlib
import socket
import threading

# The secret key embedded in the server binary
ARCANE_KEY = b"ObsidianCitadel_S3cretKey_2024"
FLAG = os.environ.get("FLAG", "FantasyCTF{placeholder}")


def handle_client(conn: socket.socket, addr):
    try:
        # Step 1: Send greeting and nonce
        nonce = os.urandom(16).hex()
        conn.sendall(b"=== The Arcane Server ===\n")
        conn.sendall(b"I speak in riddles of keys and echoes.\n")
        conn.sendall(b"Prove you understand my tongue.\n\n")
        conn.sendall(f"NONCE: {nonce}\n".encode())
        conn.sendall(b"\nCompute the seal and send it back.\n")
        conn.sendall(b"> ")

        # Step 2: Receive response
        response = conn.recv(4096).decode().strip()

        # Step 3: Verify HMAC-SHA256
        expected = hmac.new(ARCANE_KEY, nonce.encode(), hashlib.sha256).hexdigest()

        if hmac.compare_digest(response, expected):
            conn.sendall(b"\nThe seal is valid. The door opens.\n")
            conn.sendall(f"Flag: {FLAG}\n".encode())
        else:
            conn.sendall(b"\nInvalid seal. The door remains shut.\n")

    except Exception as e:
        conn.sendall(f"Server error: {e}\n".encode())
    finally:
        conn.close()


def main():
    host = "0.0.0.0"
    port = 1337
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Arcane Server listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    main()
