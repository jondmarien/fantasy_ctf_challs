"""
Consolidated Prog Challenge Server (Advanced)
Two beyond-Expert challenges served from one process with port-based routing:
  Port 1338 — Legendary (The Chronomancer's Gauntlet)
  Port 1339 — Mythic (The Abyssal Architect)
"""

import os
import sys
import threading

from importlib.machinery import SourceFileLoader

BASE = os.path.dirname(__file__)

# Add challenge dirs to path
sys.path.insert(
    0, os.path.join(BASE, "The-Chronomancers-Gauntlet-Legendary", "challenge")
)
sys.path.insert(0, os.path.join(BASE, "The-Abyssal-Architect-Mythic", "challenge"))


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


def main():
    # Start both servers in separate threads
    t1 = threading.Thread(
        target=chronomancer_mod.main,
        kwargs={"port": 1338},
        daemon=True,
        name="chronomancer",
    )
    t2 = threading.Thread(
        target=architect_mod.main, kwargs={"port": 1339}, daemon=True, name="architect"
    )

    t1.start()
    t2.start()

    print("Consolidated prog server running:")
    print("  Port 1338 — The Chronomancer's Gauntlet (Legendary)")
    print("  Port 1339 — The Abyssal Architect (Mythic)")

    # Keep main thread alive
    t1.join()
    t2.join()


if __name__ == "__main__":
    main()
