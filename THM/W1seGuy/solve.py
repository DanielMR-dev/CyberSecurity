import socket
import string

HOST = "10.65.174.96"
PORT = 1337

# Step 1: Connect to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Step 2: Receive server response
data = s.recv(4096).decode()
print(f"Server: {data}")

# Step 3: Extract hex-encoded ciphertext
# Response format: "This XOR encoded text has flag 1: <hex>\n"
ct_hex = data.split(": ")[-1].strip()
ciphertext = bytes.fromhex(ct_hex)

# Step 4: Recover first 4 key bytes from known plaintext prefix 'THM{'
known = b"THM{"
key = ""
for i in range(4):
    key += chr(ciphertext[i] ^ known[i]) 

# Step 5: Brute-force the 5th key character
for c in string.ascii_letters + string.digits:
    candidate = key + c
    decrypted = "".join(chr(ciphertext[i] ^ ord(candidate[i % 5])) for i in range(len(ciphertext)))
    if decrypted.startswith("THM{") and decrypted.endswith("}"):
        key = candidate
        print(f"[+] Flag 1: {decrypted}")
        break

# Step 6: Receive prompt "What is the encryption key?"
s.recv(4096)

# Step 7: Send key back to server
s.send((key + "\n").encode())

# Step 8: Receive Flag 2
flag2 = s.recv(4096).decode()
print(f"[+] {flag2}")

s.close()
