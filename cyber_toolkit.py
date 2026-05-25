#!/usr/bin/env python3
"""
Cybersecurity Toolkit
Author: boluwatife06-bit (GitHub)
Description: Educational multi-tool for port scanning, hash cracking,
             password analysis, and file encryption.
Disclaimer: Use only on systems you own or have explicit permission to test.
"""

import sys
import socket
import threading
import queue
import hashlib
import random
import string
import os
import time
from getpass import getpass

# ============================
#  COLOR HELPERS (Optional)
# ============================
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_banner():
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
   ██████╗██╗   ██╗██████╗ ███████╗██████╗     ████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗
  ██╔════╝╚██╗ ██╔╝██╔══██╗██╔════╝██╔══██╗    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝
  ██║      ╚████╔╝ ██████╔╝█████╗  ██████╔╝       ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║
  ██║       ╚██╔╝  ██╔══██╗██╔══╝  ██╔══██╗       ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║
  ╚██████╗   ██║   ██████╔╝███████╗██║  ██║       ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║
   ╚═════╝   ╚═╝   ╚═════╝ ╚══════╝╚═╝  ╚═╝       ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝
{Colors.ENDC}
{Colors.BOLD}Author: boluwatife06-bit (GitHub){Colors.ENDC}
{Colors.WARNING}Educational use only!{Colors.ENDC}
"""
    print(banner)

# ============================
#  1. PORT SCANNER
# ============================
def port_scan(target, port):
    """Attempt a TCP connection to a single port."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        sock.close()
        if result == 0:
            return port
    except Exception:
        pass
    return None

def threader(q, open_ports, target):
    """Worker thread: fetch port from queue and scan."""
    while True:
        port = q.get()
        if port_scan(target, port):
            open_ports.append(port)
        q.task_done()

def port_scanner():
    """Interactive multithreaded port scanner."""
    target = input(f"{Colors.BOLD}Enter target IP/hostname: {Colors.ENDC}").strip()
    start_port = int(input("Start port (default 1): ") or 1)
    end_port = int(input("End port (default 1024): ") or 1024)

    print(f"\n{Colors.CYAN}Scanning {target} from {start_port} to {end_port}...{Colors.ENDC}\n")
    start_time = time.time()

    q = queue.Queue()
    open_ports = []
    threads = []

    for _ in range(100):  # 100 threads
        t = threading.Thread(target=threader, args=(q, open_ports, target))
        t.daemon = True
        t.start()
        threads.append(t)

    for port in range(start_port, end_port + 1):
        q.put(port)

    q.join()

    elapsed = time.time() - start_time
    print(f"{Colors.GREEN}Scan completed in {elapsed:.2f} seconds.{Colors.ENDC}")
    if open_ports:
        print(f"{Colors.BOLD}Open ports:{Colors.ENDC}")
        for p in sorted(open_ports):
            try:
                service = socket.getservbyport(p)
            except:
                service = "unknown"
            print(f"  {Colors.GREEN}Port {p} ({service}){Colors.ENDC}")
    else:
        print(f"{Colors.WARNING}No open ports found.{Colors.ENDC}")

# ============================
#  2. HASH CRACKER
# ============================
def crack_hash(hash_value, hash_type, wordlist_path):
    """Attempt dictionary attack on a hash."""
    if not os.path.isfile(wordlist_path):
        print(f"{Colors.FAIL}Wordlist file not found: {wordlist_path}{Colors.ENDC}")
        return None

    print(f"{Colors.CYAN}Cracking {hash_type.upper()} hash...{Colors.ENDC}")
    try:
        with open(wordlist_path, 'r', encoding='latin-1') as f:
            for word in f:
                word = word.strip()
                if hash_type == 'md5':
                    hashed = hashlib.md5(word.encode()).hexdigest()
                elif hash_type == 'sha1':
                    hashed = hashlib.sha1(word.encode()).hexdigest()
                elif hash_type == 'sha256':
                    hashed = hashlib.sha256(word.encode()).hexdigest()
                else:
                    print(f"{Colors.FAIL}Unsupported hash type.{Colors.ENDC}")
                    return None

                if hashed == hash_value.lower():
                    return word
    except Exception as e:
        print(f"{Colors.FAIL}Error reading wordlist: {e}{Colors.ENDC}")
        return None
    return None

def hash_cracker():
    """Interactive hash cracking module."""
    hash_value = input(f"{Colors.BOLD}Enter hash to crack: {Colors.ENDC}").strip()
    hash_type = input("Hash type (md5/sha1/sha256): ").strip().lower()
    wordlist = input("Path to wordlist file: ").strip()

    result = crack_hash(hash_value, hash_type, wordlist)
    if result:
        print(f"{Colors.GREEN}[+] Cracked! Password: {result}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}[-] Password not found in wordlist.{Colors.ENDC}")

# ============================
#  3. PASSWORD STRENGTH & GENERATOR
# ============================
def password_strength(pwd):
    """Evaluate password strength and return score & feedback."""
    score = 0
    feedback = []

    if len(pwd) >= 12:
        score += 2
    elif len(pwd) >= 8:
        score += 1
    else:
        feedback.append("Too short (min 8 chars).")

    if any(c.isupper() for c in pwd):
        score += 1
    else:
        feedback.append("Add uppercase letters.")

    if any(c.islower() for c in pwd):
        score += 1
    else:
        feedback.append("Add lowercase letters.")

    if any(c.isdigit() for c in pwd):
        score += 1
    else:
        feedback.append("Add digits.")

    if any(c in string.punctuation for c in pwd):
        score += 1
    else:
        feedback.append("Add special characters.")

    # Additional checks
    if len(set(pwd)) < len(pwd) / 2:
        feedback.append("Avoid repeated characters.")

    common = ['password', '123456', 'qwerty', 'abc123']
    if pwd.lower() in common:
        feedback.append("Avoid common passwords.")
        score = max(0, score - 2)

    if score <= 2:
        strength = "Weak"
        color = Colors.FAIL
    elif score <= 4:
        strength = "Moderate"
        color = Colors.WARNING
    else:
        strength = "Strong"
        color = Colors.GREEN

    print(f"\n{color}Strength: {strength} ({score}/6){Colors.ENDC}")
    if feedback:
        print(f"{Colors.WARNING}Suggestions:{Colors.ENDC}")
        for f in feedback:
            print(f"  - {f}")

def generate_password(length=16):
    """Generate a strong random password."""
    chars = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(chars) for _ in range(length))
    return password

def password_tool():
    """Interactive password analysis and generation."""
    print(f"{Colors.BOLD}1. Check password strength{Colors.ENDC}")
    print(f"{Colors.BOLD}2. Generate strong password{Colors.ENDC}")
    choice = input("Choose: ").strip()

    if choice == '1':
        pwd = getpass("Enter password (hidden): ")
        password_strength(pwd)
    elif choice == '2':
        length = int(input("Password length (default 16): ") or 16)
        pwd = generate_password(length)
        print(f"{Colors.GREEN}Generated password: {pwd}{Colors.ENDC}")
    else:
        print(f"{Colors.FAIL}Invalid option.{Colors.ENDC}")

# ============================
#  4. FILE ENCRYPTION / DECRYPTION
# ============================
def load_cryptography():
    """Dynamically import Fernet, prompt install if missing."""
    try:
        from cryptography.fernet import Fernet
        return Fernet
    except ImportError:
        print(f"{Colors.FAIL}The 'cryptography' library is required. Install with: pip install cryptography{Colors.ENDC}")
        sys.exit(1)

def generate_key_file(key_path="secret.key"):
    """Generate a symmetric key and save to file."""
    Fernet = load_cryptography()
    key = Fernet.generate_key()
    with open(key_path, 'wb') as key_file:
        key_file.write(key)
    print(f"{Colors.GREEN}Key saved to {key_path}{Colors.ENDC}")
    return key

def load_key(key_path="secret.key"):
    """Load the key from file."""
    if not os.path.exists(key_path):
        print(f"{Colors.FAIL}Key file not found. Generate one first.{Colors.ENDC}")
        return None
    with open(key_path, 'rb') as f:
        return f.read()

def encrypt_file(file_path, key):
    """Encrypt a file using Fernet."""
    Fernet = load_cryptography()
    f = Fernet(key)
    with open(file_path, 'rb') as original:
        original_data = original.read()
    encrypted = f.encrypt(original_data)
    with open(file_path + '.enc', 'wb') as enc_file:
        enc_file.write(encrypted)
    print(f"{Colors.GREEN}Encrypted file saved as {file_path}.enc{Colors.ENDC}")

def decrypt_file(enc_path, key):
    """Decrypt a .enc file."""
    Fernet = load_cryptography()
    f = Fernet(key)
    with open(enc_path, 'rb') as enc_file:
        encrypted_data = enc_file.read()
    try:
        decrypted = f.decrypt(encrypted_data)
    except Exception:
        print(f"{Colors.FAIL}Decryption failed: invalid key or corrupted file.{Colors.ENDC}")
        return
    orig_name = enc_path.replace('.enc', '')
    with open(orig_name, 'wb') as dec_file:
        dec_file.write(decrypted)
    print(f"{Colors.GREEN}Decrypted file restored as {orig_name}{Colors.ENDC}")

def file_encryption_menu():
    """Interactive file encryption/decryption."""
    print(f"{Colors.BOLD}1. Generate encryption key{Colors.ENDC}")
    print(f"{Colors.BOLD}2. Encrypt a file{Colors.ENDC}")
    print(f"{Colors.BOLD}3. Decrypt a file{Colors.ENDC}")
    choice = input("Choose: ").strip()

    if choice == '1':
        key_path = input("Key file name (default: secret.key): ").strip() or "secret.key"
        generate_key_file(key_path)
    elif choice == '2':
        key_path = input("Key file (default: secret.key): ").strip() or "secret.key"
        key = load_key(key_path)
        if not key:
            return
        file_path = input("File to encrypt: ").strip()
        if not os.path.exists(file_path):
            print(f"{Colors.FAIL}File not found.{Colors.ENDC}")
            return
        encrypt_file(file_path, key)
    elif choice == '3':
        key_path = input("Key file (default: secret.key): ").strip() or "secret.key"
        key = load_key(key_path)
        if not key:
            return
        enc_path = input("Encrypted file (.enc): ").strip()
        if not os.path.exists(enc_path):
            print(f"{Colors.FAIL}File not found.{Colors.ENDC}")
            return
        decrypt_file(enc_path, key)
    else:
        print(f"{Colors.FAIL}Invalid option.{Colors.ENDC}")

# ============================
#  MAIN MENU
# ============================
def main():
    while True:
        print_banner()
        print(f"{Colors.BOLD}1. Port Scanner{Colors.ENDC}")
        print(f"{Colors.BOLD}2. Hash Cracker{Colors.ENDC}")
        print(f"{Colors.BOLD}3. Password Strength & Generator{Colors.ENDC}")
        print(f"{Colors.BOLD}4. File Encryption/Decryption{Colors.ENDC}")
        print(f"{Colors.BOLD}5. Exit{Colors.ENDC}")

        choice = input(f"\n{Colors.CYAN}>> {Colors.ENDC}").strip()

        if choice == '1':
            port_scanner()
        elif choice == '2':
            hash_cracker()
        elif choice == '3':
            password_tool()
        elif choice == '4':
            file_encryption_menu()
        elif choice == '5':
            print(f"{Colors.GREEN}Goodbye!{Colors.ENDC}")
            sys.exit(0)
        else:
            print(f"{Colors.FAIL}Invalid choice, try again.{Colors.ENDC}")

        input(f"\n{Colors.BOLD}Press Enter to continue...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted. Exiting.{Colors.ENDC}")
        sys.exit(0)
