#!/usr/bin/env python3
"""The Prophecy Engine — black-box multi-stage transformation server."""

import os
import socket
import threading

FLAG = os.environ.get("FLAG", "FantasyCTF{placeholder}")

# Secret transformation constants (players must deduce these)
STAGE1_MULT = 7
STAGE1_MOD = 65537
STAGE2_XOR = 0xDEAD
STAGE3_ADD = 31337

# The target value: transform(SECRET_INPUT) = TARGET
# Players must find SECRET_INPUT given TARGET
SECRET_INPUT = 48879  # 0xBEEF


def forward_transform(x: int) -> int:
    """Apply the 3-stage transformation: multiply mod → XOR → add."""
    # Stage 1: Modular multiplication
    x = (x * STAGE1_MULT) % STAGE1_MOD
    # Stage 2: XOR with constant
    x = x ^ STAGE2_XOR
    # Stage 3: Addition with constant
    x = x + STAGE3_ADD
    return x


TARGET = forward_transform(SECRET_INPUT)


def handle_client(conn: socket.socket, addr):
    try:
        conn.sendall(b"=== The Prophecy Engine ===\n")
        conn.sendall(b"I transform what you give me, step by step.\n")
        conn.sendall(b"Learn how I see, then prove your understanding.\n\n")
        conn.sendall(b"Commands:\n")
        conn.sendall(b"  ORACLE <integer>  - I will show you the transformed result\n")
        conn.sendall(b"  CHALLENGE         - I will give you a target to invert\n")
        conn.sendall(b"  QUIT              - Leave the sanctum\n\n")

        oracle_queries = 0
        max_queries = 100

        while True:
            conn.sendall(b"> ")
            data = conn.recv(4096).decode().strip()

            if not data:
                break

            if data.upper() == "QUIT":
                conn.sendall(b"The Engine falls silent.\n")
                break

            elif data.upper().startswith("ORACLE"):
                parts = data.split()
                if len(parts) != 2:
                    conn.sendall(b"Usage: ORACLE <integer>\n")
                    continue

                if oracle_queries >= max_queries:
                    conn.sendall(b"The Engine grows weary. No more oracle queries.\n")
                    continue

                try:
                    x = int(parts[1])
                    if x < 0 or x > 2**32:
                        conn.sendall(b"Input must be between 0 and 2^32.\n")
                        continue
                    result = forward_transform(x)
                    oracle_queries += 1
                    conn.sendall(f"RESULT: {result}\n".encode())
                    conn.sendall(
                        f"(Queries used: {oracle_queries}/{max_queries})\n".encode()
                    )
                except ValueError:
                    conn.sendall(b"Invalid integer.\n")

            elif data.upper() == "CHALLENGE":
                conn.sendall(f"TARGET: {TARGET}\n".encode())
                conn.sendall(b"What input produces this output?\n")
                conn.sendall(b"ANSWER: ")
                answer = conn.recv(4096).decode().strip()

                try:
                    answer_int = int(answer)
                    if answer_int == SECRET_INPUT:
                        conn.sendall(b"\nThe Engine acknowledges your vision.\n")
                        conn.sendall(f"Flag: {FLAG}\n".encode())
                    else:
                        conn.sendall(b"\nIncorrect. The Engine sees differently.\n")
                except ValueError:
                    conn.sendall(b"Invalid integer.\n")

            else:
                conn.sendall(b"Unknown command. Use ORACLE, CHALLENGE, or QUIT.\n")

    except Exception as e:
        try:
            conn.sendall(f"Engine error: {e}\n".encode())
        except Exception:
            pass
    finally:
        conn.close()


def main():
    host = "0.0.0.0"
    port = 1337
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Prophecy Engine listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    main()
