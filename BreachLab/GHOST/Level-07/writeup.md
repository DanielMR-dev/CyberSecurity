# BreachLab - Ghost Track: Level 7 → 8 (Lost in Translation)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 7 → 8 (Lost in Translation)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost7`
- **Goal:** Retrieve the password / credentials for `ghost8`
- **Next Connection:** `ssh ghost8@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

Analyst **Kael** implemented multi-layered obfuscation for operational transmissions ("one layer was never enough"). The transmission file is formatted as an ASCII hexdump embedding an encoded payload. The objective is to reverse the hexdump layer using `xxd -r` and decode the resulting Base64 payload to retrieve the credentials for `ghost8`.

---

## 2. Reconnaissance & Artifact Inspection

Logging in via SSH as `ghost7` and inspecting the home directory:

```bash
ghost7@breachlab:~$ ls -la
total 56
drwx------ 1 ghost7 ghost7 4096 Jun  4 04:54 .
drwxr-xr-x 1 root   root   4096 May 19 12:05 ..
...
-rw-r----- 1 ghost7 ghost7  125 May 19 12:05 transmission.dat
```

### Inspecting `transmission.dat`

Viewing the raw contents of `transmission.dat`:

```bash
ghost7@breachlab:~$ cat transmission.dat
00000000: 5244 4e6a 4d47 517a 587a 4279 5830 5178  RDNjMGQzXzByX0Qx
00000010: 4d77 3d3d 0a                              Mw==.
```

The file is an ASCII text representation of a traditional `xxd` hexdump. Notice the printable ASCII column on the right displays `RDNjMGQzXzByX0QxMw==`, which ends with the distinctive Base64 padding `==`.

---

## 3. Multi-Layer Deobfuscation & Flag Extraction

### Layer 1: Reversing the Hexdump (`xxd -r`)

Using `xxd` with the `-r` (*reverse*) flag transforms the plaintext hexdump back into its underlying raw byte sequence:

```bash
ghost7@breachlab:~$ xxd -r transmission.dat
RDNjMGQzXzByX0QxMw==
```

### Layer 2: Decoding Base64 (`base64 -d`)

Piping the resulting byte stream into `base64 -d` decodes the final plaintext secret:

```bash
ghost7@breachlab:~$ xxd -r transmission.dat | base64 -d
D3c0d3_0r_D13
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost8` |
| **Password / Flag** | `D3c0d3_0r_D13` |
| **Intermediate Representation** | Base64 (`RDNjMGQzXzByX0QxMw==`) |
| **Target SSH Command** | `ssh ghost8@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `xxd -r <file>`: Revert an ASCII hexdump back into binary/raw format.
- `base64 -d`: Decode Base64 data from standard input.
- `xxd -r <file> | base64 -d`: Pipeline combining multi-stage decoding without writing intermediate artifacts to disk.

---

## 6. Lessons Learned

1. **Multi-Stage Encoding Pipelines:** Threat actors and wargames commonly layer encodings (Hexdump → Base64 → Plaintext) to evade simple signature scanners.
2. **Reversing Hex Dumps:** The `xxd -r` utility is invaluable for reconstructing binaries and structured strings from text-based representations.
