# TryHackMe - W1seGuy

## General Information

- **Challenge:** W1seGuy
- **Category:** Cryptography / Network Sockets
- **Platform:** TryHackMe
- **Target Service:** TCP Port `1337`
- **Difficulty:** Easy
- **Objectives:** Analyze repeating XOR stream encryption, recover the encryption key via Known-Plaintext Attack, and capture both flags.

---

## 1. Server Source Code Analysis

The challenge service implements a socket listener with the following XOR encryption routine:

```python
def setup(server, key):
    flag = 'THM{...}' 
    xored = ""
    for i in range(0, len(flag)):
        xored += chr(ord(flag[i]) ^ ord(key[i % len(key)]))
    return xored.encode().hex()

def start(server):
    res = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
    key = str(res) # Random 5-character alphanumeric key
    hex_encoded = setup(server, key)
    send_message(server, "This XOR encoded text has flag 1: " + hex_encoded + "\n")
    ...
```

### Vulnerability Analysis

1. **Short Repeating Key (5 bytes):** The key cycles with modulo index `i % 5`.
2. **Predictable Flag Header:** TryHackMe flags always begin with the known 4-byte prefix `THM{`.
3. **Commutative Property of XOR ($\oplus$):**
   $$C_i = P_i \oplus K_i \iff K_i = C_i \oplus P_i$$

---

## 2. Cryptanalysis & Attack Strategy

1. **Recovering the First 4 Key Bytes:**
   Using known plaintext bytes ($P_{0..3} = \text{"THM\{"}$), we XOR against ciphertext bytes ($C_{0..3}$):
   $$K_0 = C_0 \oplus \text{'T'}, \quad K_1 = C_1 \oplus \text{'H'}, \quad K_2 = C_2 \oplus \text{'M'}, \quad K_3 = C_3 \oplus \text{'\{'}$$

2. **Brute-Forcing the 5th Key Character:**
   Since $K_4 \in [a-zA-Z0-9]$ (62 candidates), we iterate over all possible characters and decrypt the ciphertext until the recovered plaintext starts with `THM{` and terminates with `}`.

3. **Submitting Key for Flag 2:**
   Once the full 5-character key is identified, send it across the socket connection to trigger the server response containing Flag 2.

---

## 3. Exploit Script (`solve.py`)

```python
import socket
import string

HOST = "10.65.174.96"  # Replace with target room IP
PORT = 1337

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# 1. Receive XOR ciphertext from server
data = s.recv(4096).decode()
ct_hex = data.split(": ")[-1].strip()
ciphertext = bytes.fromhex(ct_hex)

# 2. Derive first 4 key bytes from known plaintext 'THM{'
known = b"THM{"
key = ""
for i in range(4):
    key += chr(ciphertext[i] ^ known[i])

# 3. Brute-force 5th key character
for c in string.ascii_letters + string.digits:
    candidate = key + c
    decrypted = "".join(chr(ciphertext[i] ^ ord(candidate[i % 5])) for i in range(len(ciphertext)))
    if decrypted.startswith("THM{") and decrypted.endswith("}"):
        key = candidate
        print(f"[+] Decrypted Flag 1: {decrypted}")
        print(f"[+] Recovered Key: {key}")
        break

# 4. Send recovered key to obtain Flag 2
s.recv(4096)
s.send((key + "\n").encode())
flag2 = s.recv(4096).decode()
print(f"[+] {flag2.strip()}")

s.close()
```

---

## 4. Summary of Flags

| Flag | Acquisition Vector |
| :--- | :--- |
| **Flag 1** | Decrypted from XOR ciphertext using recovered key |
| **Flag 2** | Returned by server after submitting the valid 5-char key |

---

## 5. Lessons Learned

1. **Weakness of Repeating XOR Keys:** Multi-byte XOR with short repeating keys behaves like a Vigenère cipher and is trivially broken when any plaintext prefix is known.
2. **Socket Automation:** Python's `socket` library allows fast, deterministic interaction with network challenges in real time.
