# BreachLab - Ghost Track: Level 4 → 5 (Signal in the Noise)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 4 → 5 (Signal in the Noise)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost4`
- **Goal:** Retrieve the password / credentials for `ghost5`
- **Next Connection:** `ssh ghost5@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

Analyst **Kael** dumped hundreds of noisy log records into a storage directory named `vault/`. The challenge hints that one record differs in format and content from the rest ("The real signal has a different format. Find it."). The objective is to filter through hundreds of log files using tools like `grep`, `find`, or size analysis to extract the valid credential for `ghost5`.

---

## 2. Reconnaissance & Directory Analysis

Logging in via SSH as `ghost4` and inspecting directory contents:

```bash
ghost4@breachlab:~$ ls -la
total 80
drwx------ 1 ghost4 ghost4  4096 Jun  1 20:59 .
drwxr-xr-x 1 root   root    4096 May 19 12:05 ..
...
drwx------ 2 ghost4 ghost4 20480 Jun  3 17:35 vault
```

### Entering `vault/`

Listing files inside `vault/` reveals 500 individual records (`record_0001` through `record_0500`):

```bash
ghost4@breachlab:~$ cd vault/
ghost4@breachlab:~/vault$ ls -la
```

---

## 3. Signal Filtering & File Analysis

### Approach 1: File Size Anomaly Analysis

Almost all 500 records have an identical size of **63 bytes**, except for a few anomalies:

```bash
ghost4@breachlab:~/vault$ ls -la | awk '{print $5, $9}' | sort -n | uniq -c
```

Anomalous files identified:
- `record_0056` (42 bytes)
- `record_0073`, `record_0182`, `record_0291`, `record_0404`, `record_0477` (48 bytes each)

### Approach 2: Pattern Search with `grep`

Using `grep` to filter for unique formatting or keyword indicators across all files:

```bash
ghost4@breachlab:~/vault$ grep -rn "CREDENTIAL" .
./record_0056:1:[CLASSIFIED] CREDENTIAL: Gr3p_F1nds_Truth
```

Or filtering out standard timestamped noise lines:

```bash
ghost4@breachlab:~/vault$ grep -v "\[2026-03-28" *
record_0056:[CLASSIFIED] CREDENTIAL: Gr3p_F1nds_Truth
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost5` |
| **Password / Flag** | `Gr3p_F1nds_Truth` |
| **Source File** | `vault/record_0056` |
| **Target SSH Command** | `ssh ghost5@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Techniques Reference

- `grep -r "<pattern>" .`: Recursively search for a specific keyword in all files within the current directory.
- `grep -v "<pattern>" *`: Invert matching to display lines that do not match the standard log noise.
- `find . -type f ! -size 63c`: Find files whose exact size in bytes differs from the common 63-byte noise.

---

## 6. Lessons Learned

1. **Noise Filtering at Scale:** When dealing with hundreds of dumped files, manual inspection is infeasible; shell pipelines with `grep`, `awk`, and `find` quickly isolate statistical and format anomalies.
2. **Format Discrepancies:** Identifying pattern mismatches (e.g., non-standard header formats) is a key log analysis skill during forensic and CTF investigations.
