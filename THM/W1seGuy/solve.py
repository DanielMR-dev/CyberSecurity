import socket
import string

HOST = "10.65.174.96"
PORT = 1337

# Paso 1: Conectarse al servidor
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

# Paso 2: Recibir la respuesta del servidor
data = s.recv(4096).decode()
print(f"Sevidor: {data}")

# PASO 3: Extraer el hex de la respuesta
# La respuesta es algo como:
# "This XOR encoded text has flag 1: 3a78354e...\n"
# Pista: usa .split(": ") y queda en la última parte
ct_hex = data.split(": ")[-1].strip()
ciphertext = bytes.fromhex(ct_hex)

# PASO 4: Recuperar 4 chars de la clave (ya lo hiciste antes!)
known = b"THM{"
key = ""
for i in range(4):
    key += chr(ciphertext[i] ^ known[i]) 

# PASO 5: Fuerza bruta del 5to carácter
for c in string.ascii_letters + string.digits:
    candidate = key + c
    decrypted = "".join(chr(ciphertext[i] ^ ord(candidate[i % 5])) for i in range(len(ciphertext)))
    if decrypted.startswith("THM{") and decrypted.endswith("}"):
        key = candidate
        print(f"[+] Flag 1: {decrypted}")
        break

# PASO 6: Recibir "What is the encryption key?"
s.recv(4096)

# PASO 7: Enviar la clave al servidor
s.send((key + "\n").encode())

# PASO 8: Recibir Flag 2
flag2 = s.recv(4096).decode()
print(f"[+] {flag2}")

s.close()
