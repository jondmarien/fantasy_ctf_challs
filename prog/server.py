"""
Consolidated Prog Challenge Server (Advanced)
Both challenges served on a single port (1338) with a selector menu.
Player chooses which challenge to enter at connect time.
"""

import os
import socket
import threading

from importlib.machinery import SourceFileLoader

BASE = os.path.dirname(__file__)
PORT = int(os.environ.get("PORT", 1338))


def _load_module(challenge_dir, module_file):
    """Load a module from a challenge's challenge/ directory."""
    path = os.path.join(BASE, challenge_dir, "challenge", module_file)
    mod_name = challenge_dir.replace("-", "_").lower()
    return SourceFileLoader(mod_name, path).load_module()


# Load challenge modules
chronomancer_mod = _load_module(
    "The-Chronomancers-Gauntlet-Legendary", "chronomancer.py"
)
architect_mod = _load_module("The-Abyssal-Architect-Mythic", "abyssal_architect.py")

# Inject flags from environment
chronomancer_mod.FLAG = os.environ.get("FLAG_CHRONOMANCER", "FantasyCTF{placeholder}")
architect_mod.FLAG = os.environ.get("FLAG_ARCHITECT", "FantasyCTF{placeholder}")


def handle_client(conn: socket.socket, addr):
    """Show a selector menu and route to the chosen challenge handler."""
    try:
        conn.settimeout(30)
        banner = (
            b"\n"
            b"=== The Advanced Prog Challenges ===\n"
            b"\n"
            b"  [1] The Chronomancer's Gauntlet  (Legendary)\n"
            b"  [2] The Abyssal Architect         (Mythic)\n"
            b"\n"
            b"Select a challenge: "
        )
        conn.sendall(banner)
        choice = conn.recv(16).decode(errors="ignore").strip()
        if choice == "1":
            chronomancer_mod.handle_client(conn, addr)
        elif choice == "2":
            architect_mod.handle_client(conn, addr)
        else:
            conn.sendall(b"Invalid choice. Disconnecting.\n")
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass


def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("0.0.0.0", PORT))
    server.listen(32)
    print(f"Consolidated prog server listening on port {PORT}")
    print("  [1] The Chronomancer's Gauntlet (Legendary)")
    print("  [2] The Abyssal Architect (Mythic)")

    while True:
        conn, addr = server.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        t.start()


if __name__ == "__main__":
    main()
