# TryHackMe - The-Game

## General Information

- **Challenge:** The-Game
- **Target:** Tetrix.exe (Malware Analysis & Binary Reverse Engineering)
- **Platform:** TryHackMe
- **File Format:** PE32+ executable for MS Windows (GUI), x86-64
- **Difficulty:** Easy / Medium
- **Objectives:** Static analysis of compiled binary, asset dissection, decoy identification, and hidden flag recovery.

---

## 1. Initial Reconnaissance & File Identification

Inspecting the extracted executable format and architecture:

```bash
file extracted/Tetrix.exe
```

**Output:**
```text
extracted/Tetrix.exe: PE32+ executable (GUI) x86-64, for MS Windows
```

---

## 2. String Extraction & Engine Fingerprinting

### String Extraction with Targeted Filters

```bash
strings extracted/Tetrix.exe | grep -iE "(http|flag|key|cert|godot|config)"
```

### Key Findings

- Direct references to **Godot Engine 4.x** (`https://godotengine.org`).
- Resource references for internal game assets (`res://Game.tscn`, `res://blocks/`, `res://assets/`).
- Engine configuration blocks containing `application/config/name = Tetrim`.

---

## 3. Signature & Structural Analysis with Binwalk

Examining embedded payloads and archive signatures:

```bash
binwalk extracted/Tetrix.exe
```

### Observations

- Identified multiple **ESP32** firmware header signatures embedded as decoy/junk data to hinder automated decompilation.
- Searched for Godot pack magic bytes (`GDPC`):
  ```bash
  grep -aob "GDPC" extracted/Tetrix.exe
  ```
  Found `GDPC` signature at offset `46318144`.

---

## 4. Pattern Matching & Flag Extraction

Given the binary's size (~88 MB) and packed engine resources, a Python script was used to scan raw bytes for TryHackMe flag patterns (`THM{...}`):

```python
import re

with open('extracted/Tetrix.exe', 'rb') as f:
    data = f.read()

matches = list(re.finditer(b'THM\\{[^\\}]+\\}', data))
for m in matches:
    offset = m.start()
    flag = m.group(0).decode('utf-8', errors='ignore')
    print(f"[+] Flag discovered at offset {offset}: {flag}")
```

### Output

```text
[+] Flag discovered at offset 93001116: THM{I_CAN_READ_IT_ALL}
```

The flag was stored in plaintext near the end of the executable binary (near EOF).

---

## 5. Summary of Flags

| Flag | Type | Offset | Value |
| :--- | :--- | :--- | :--- |
| **Flag** | Static Binary Plaintext | `93001116` | `THM{I_CAN_READ_IT_ALL}` |

---

## 6. Lessons Learned

1. **Game Engine Executables:** Godot 4.x and Unity binaries bundle both the engine runtime and resource packages into a single PE executable.
2. **Decoy Data in Binaries:** Binary obfuscation often introduces dummy headers (such as ESP32 images) to confuse automated decompilers.
3. **Raw Byte Regex Scanning:** Fast pattern search over raw binary bytes (`re.finditer(b'THM{...')`) is an efficient initial reversing technique for CTF challenges.
