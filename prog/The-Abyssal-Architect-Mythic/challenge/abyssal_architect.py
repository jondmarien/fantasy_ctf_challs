#!/usr/bin/env python3
"""The Abyssal Architect — custom stack-based VM bytecode programming challenge server."""

import os
import random
import socket
import threading

FLAG = os.environ.get("FLAG", "FantasyCTF{placeholder}")

# ---------------------------------------------------------------------------
# VM Specification
# ---------------------------------------------------------------------------

VM_SPEC = """\
=== THE ABYSSAL ENGINE — INSTRUCTION SET ===

The Abyssal Engine is a stack-based virtual machine.
All values are integers. The stack starts empty.
Input n is pre-loaded into memory slot 0 before execution.

INSTRUCTIONS:
  PUSH <val>  — Push integer <val> onto the stack
  POP         — Remove the top element
  DUP         — Duplicate the top element
  SWAP        — Swap the top two elements
  ROT         — Rotate top three: [a b c] -> [b c a]  (c was on top)
  OVER        — Copy second-from-top onto top: [a b] -> [a b a]
  ADD         — Pop two, push their sum
  SUB         — Pop two, push (second - top)
  MUL         — Pop two, push their product
  MOD         — Pop two, push (second mod top)
  NEG         — Negate the top element
  GT          — Pop two, push 1 if second > top, else 0
  EQ          — Pop two, push 1 if equal, else 0
  JZ <addr>   — Pop top; if zero, jump to instruction <addr>
  JNZ <addr>  — Pop top; if non-zero, jump to instruction <addr>
  LOAD <slot> — Push value from memory slot <slot>
  STORE <slot>— Pop top and store in memory slot <slot>
  HALT        — Stop execution; top of stack is the result

CONSTRAINTS:
  - Maximum 200 instructions
  - Maximum stack depth: 50
  - Maximum 100000 execution steps (prevents infinite loops)
  - Memory slots 0-15 available (slot 0 = input n)
  - Program must HALT with exactly one value on the stack (the result)
"""

INSTRUCTIONS = {
    "PUSH",
    "POP",
    "DUP",
    "SWAP",
    "ROT",
    "OVER",
    "ADD",
    "SUB",
    "MUL",
    "MOD",
    "NEG",
    "GT",
    "EQ",
    "JZ",
    "JNZ",
    "LOAD",
    "STORE",
    "HALT",
}

INSTRUCTIONS_WITH_ARG = {"PUSH", "JZ", "JNZ", "LOAD", "STORE"}
MAX_INSTRUCTIONS = 200
MAX_STACK_DEPTH = 50
MAX_STEPS = 100000
NUM_MEMORY_SLOTS = 16


class VMError(Exception):
    pass


def run_vm(program, input_n):
    """Execute a VM program with input n. Returns the result or raises VMError."""
    stack = []
    memory = [0] * NUM_MEMORY_SLOTS
    memory[0] = input_n
    pc = 0
    steps = 0

    while pc < len(program):
        if steps >= MAX_STEPS:
            raise VMError("Execution limit exceeded (infinite loop?)")
        steps += 1

        instr = program[pc]
        op = instr[0]

        if op == "HALT":
            if len(stack) != 1:
                raise VMError(f"HALT with {len(stack)} values on stack (expected 1)")
            return stack[0]

        elif op == "PUSH":
            stack.append(instr[1])

        elif op == "POP":
            if not stack:
                raise VMError("POP on empty stack")
            stack.pop()

        elif op == "DUP":
            if not stack:
                raise VMError("DUP on empty stack")
            stack.append(stack[-1])

        elif op == "SWAP":
            if len(stack) < 2:
                raise VMError("SWAP requires 2 elements")
            stack[-1], stack[-2] = stack[-2], stack[-1]

        elif op == "ROT":
            if len(stack) < 3:
                raise VMError("ROT requires 3 elements")
            a, b, c = stack[-3], stack[-2], stack[-1]
            stack[-3], stack[-2], stack[-1] = b, c, a

        elif op == "OVER":
            if len(stack) < 2:
                raise VMError("OVER requires 2 elements")
            stack.append(stack[-2])

        elif op == "ADD":
            if len(stack) < 2:
                raise VMError("ADD requires 2 elements")
            b, a = stack.pop(), stack.pop()
            stack.append(a + b)

        elif op == "SUB":
            if len(stack) < 2:
                raise VMError("SUB requires 2 elements")
            b, a = stack.pop(), stack.pop()
            stack.append(a - b)

        elif op == "MUL":
            if len(stack) < 2:
                raise VMError("MUL requires 2 elements")
            b, a = stack.pop(), stack.pop()
            stack.append(a * b)

        elif op == "MOD":
            if len(stack) < 2:
                raise VMError("MOD requires 2 elements")
            b, a = stack.pop(), stack.pop()
            if b == 0:
                raise VMError("MOD by zero")
            stack.append(a % b)

        elif op == "NEG":
            if not stack:
                raise VMError("NEG on empty stack")
            stack[-1] = -stack[-1]

        elif op == "GT":
            if len(stack) < 2:
                raise VMError("GT requires 2 elements")
            b, a = stack.pop(), stack.pop()
            stack.append(1 if a > b else 0)

        elif op == "EQ":
            if len(stack) < 2:
                raise VMError("EQ requires 2 elements")
            b, a = stack.pop(), stack.pop()
            stack.append(1 if a == b else 0)

        elif op == "JZ":
            if not stack:
                raise VMError("JZ on empty stack")
            val = stack.pop()
            if val == 0:
                pc = instr[1]
                continue

        elif op == "JNZ":
            if not stack:
                raise VMError("JNZ on empty stack")
            val = stack.pop()
            if val != 0:
                pc = instr[1]
                continue

        elif op == "LOAD":
            slot = instr[1]
            if slot < 0 or slot >= NUM_MEMORY_SLOTS:
                raise VMError(f"Invalid memory slot {slot}")
            stack.append(memory[slot])

        elif op == "STORE":
            if not stack:
                raise VMError("STORE on empty stack")
            slot = instr[1]
            if slot < 0 or slot >= NUM_MEMORY_SLOTS:
                raise VMError(f"Invalid memory slot {slot}")
            memory[slot] = stack.pop()

        else:
            raise VMError(f"Unknown instruction: {op}")

        if len(stack) > MAX_STACK_DEPTH:
            raise VMError(f"Stack overflow (depth {len(stack)} > {MAX_STACK_DEPTH})")

        pc += 1

    raise VMError("Program ended without HALT")


def parse_program(text):
    """Parse a program from text. Returns list of (op, [arg]) tuples."""
    program = []
    for i, line in enumerate(text.strip().split("\n")):
        line = line.strip()
        if not line or line.startswith("//"):
            continue
        parts = line.split()
        op = parts[0].upper()
        if op not in INSTRUCTIONS:
            raise VMError(f"Line {i}: Unknown instruction '{op}'")
        if op in INSTRUCTIONS_WITH_ARG:
            if len(parts) != 2:
                raise VMError(f"Line {i}: {op} requires an argument")
            try:
                arg = int(parts[1])
            except ValueError:
                raise VMError(f"Line {i}: Invalid argument '{parts[1]}'")
            program.append((op, arg))
        else:
            if len(parts) != 1:
                raise VMError(f"Line {i}: {op} takes no arguments")
            program.append((op,))

    if len(program) > MAX_INSTRUCTIONS:
        raise VMError(
            f"Program too long ({len(program)} > {MAX_INSTRUCTIONS} instructions)"
        )

    return program


# ---------------------------------------------------------------------------
# Target function: compute the nth triangular number T(n) = n*(n+1)/2
# Also: for n < 0, return 0
# ---------------------------------------------------------------------------

TARGET_NAME = "Triangular Number"
TARGET_DESC = """\
TARGET FUNCTION: Triangular Number
  T(n) = n * (n + 1) / 2    for n >= 0
  T(n) = 0                  for n < 0

Examples:
  T(0)  = 0
  T(1)  = 1
  T(5)  = 15
  T(10) = 55
  T(-3) = 0
"""


def target_function(n):
    if n < 0:
        return 0
    return n * (n + 1) // 2


def generate_test_cases():
    """Generate 10 random test cases."""
    cases = []
    # Always include edge cases
    cases.append(0)
    cases.append(1)
    cases.append(-1)
    # Random positive
    for _ in range(5):
        cases.append(random.randint(2, 500))
    # Random negative
    for _ in range(2):
        cases.append(random.randint(-100, -1))
    random.shuffle(cases)
    return cases


# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------


def handle_client(conn: socket.socket, addr):
    try:
        conn.settimeout(300)  # 5 min total session timeout

        conn.sendall(b"=== The Abyssal Architect's Forge ===\n")
        conn.sendall(b"A machine of obsidian and void-crystal awaits your commands.\n")
        conn.sendall(b"Craft a program in its tongue to prove your mastery.\n\n")

        # Send VM spec
        conn.sendall(VM_SPEC.encode())
        conn.sendall(b"\n")

        # Send target function
        conn.sendall(TARGET_DESC.encode())
        conn.sendall(b"\n")

        conn.sendall(b"COMMANDS:\n")
        conn.sendall(b"  TEST     - Submit a program for testing (3 attempts max)\n")
        conn.sendall(b"  SUBMIT   - Submit your final program for validation\n")
        conn.sendall(b"  QUIT     - Leave the forge\n\n")

        test_attempts = 0
        max_tests = 3

        while True:
            conn.sendall(b"> ")
            try:
                data = conn.recv(4096).decode().strip()
            except socket.timeout:
                conn.sendall(b"\nThe forge grows cold. Session expired.\n")
                return

            if not data:
                continue

            cmd = data.upper()

            if cmd == "QUIT":
                conn.sendall(b"You leave the forge. The Architect watches.\n")
                return

            elif cmd == "TEST":
                if test_attempts >= max_tests:
                    conn.sendall(b"No test attempts remaining. SUBMIT or QUIT.\n")
                    continue

                test_attempts += 1
                conn.sendall(f"Test attempt {test_attempts}/{max_tests}.\n".encode())
                conn.sendall(b"Enter your program (one instruction per line).\n")
                conn.sendall(b"Send END on its own line when done.\n\n")

                # Receive program
                prog_lines = []
                while True:
                    try:
                        line = conn.recv(4096).decode()
                    except socket.timeout:
                        conn.sendall(b"\nTimeout receiving program.\n")
                        return
                    for l in line.split("\n"):
                        l = l.strip()
                        if l.upper() == "END":
                            break
                        prog_lines.append(l)
                    else:
                        continue
                    break

                prog_text = "\n".join(prog_lines)

                try:
                    program = parse_program(prog_text)
                except VMError as e:
                    conn.sendall(f"Parse error: {e}\n".encode())
                    continue

                conn.sendall(
                    f"Program parsed ({len(program)} instructions).\n".encode()
                )

                # Run 3 test cases
                test_inputs = [0, 5, 10]
                passed = 0
                for n in test_inputs:
                    expected = target_function(n)
                    try:
                        result = run_vm(program, n)
                        if result == expected:
                            conn.sendall(f"  T({n}) = {result} [PASS]\n".encode())
                            passed += 1
                        else:
                            conn.sendall(
                                f"  T({n}) = {result} [FAIL] (expected {expected})\n".encode()
                            )
                    except VMError as e:
                        conn.sendall(f"  T({n}) -> Runtime error: {e}\n".encode())

                conn.sendall(f"Test: {passed}/{len(test_inputs)} passed.\n\n".encode())

            elif cmd == "SUBMIT":
                conn.sendall(b"Enter your final program (one instruction per line).\n")
                conn.sendall(b"Send END on its own line when done.\n\n")

                # Receive program
                prog_lines = []
                while True:
                    try:
                        line = conn.recv(4096).decode()
                    except socket.timeout:
                        conn.sendall(b"\nTimeout receiving program.\n")
                        return
                    for l in line.split("\n"):
                        l = l.strip()
                        if l.upper() == "END":
                            break
                        prog_lines.append(l)
                    else:
                        continue
                    break

                prog_text = "\n".join(prog_lines)

                try:
                    program = parse_program(prog_text)
                except VMError as e:
                    conn.sendall(f"Parse error: {e}\n".encode())
                    continue

                conn.sendall(
                    f"Program parsed ({len(program)} instructions). Validating...\n".encode()
                )

                # Run against 10 random test cases
                cases = generate_test_cases()
                all_passed = True
                for n in cases:
                    expected = target_function(n)
                    try:
                        result = run_vm(program, n)
                        if result == expected:
                            conn.sendall(f"  T({n}) = {result} ✓\n".encode())
                        else:
                            conn.sendall(
                                f"  T({n}) = {result} ✗ (expected {expected})\n".encode()
                            )
                            all_passed = False
                    except VMError as e:
                        conn.sendall(f"  T({n}) → Runtime error: {e}\n".encode())
                        all_passed = False

                if all_passed:
                    conn.sendall(b"\n=== ALL TESTS PASSED ===\n")
                    conn.sendall(b"The Abyssal Architect acknowledges your mastery.\n")
                    conn.sendall(b"The forge yields its final secret.\n")
                    conn.sendall(f"Flag: {FLAG}\n".encode())
                    return
                else:
                    conn.sendall(
                        b"\nValidation failed. The Architect is not impressed.\n"
                    )
                    conn.sendall(
                        b"You may TEST again (if attempts remain) or SUBMIT again.\n\n"
                    )

            else:
                conn.sendall(b"Unknown command. Use TEST, SUBMIT, or QUIT.\n")

    except Exception as e:
        try:
            conn.sendall(f"Forge error: {e}\n".encode())
        except Exception:
            pass
    finally:
        conn.close()


def main(port=1339):
    host = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Abyssal Architect listening on {host}:{port}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    main()
