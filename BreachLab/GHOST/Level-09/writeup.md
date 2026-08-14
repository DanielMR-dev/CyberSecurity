# BreachLab - Ghost Track: Level 9 → 10 (Noise Floor)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 9 → 10 (Noise Floor)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost9`
- **Goal:** Retrieve the password / credentials for `ghost10`
- **Next Connection:** `ssh ghost10@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

Analyst **Kael** embedded an operational broadcast within a 12-kilobyte binary stream of pseudo-random noise (`signal.bin`). The challenge advises against manual inspection and emphasizes binary string extraction ("Don't open it by eye — that's not what binaries are for."). The objective is to inspect the raw binary file, extract printable character sequences using `strings` or `grep`, and recover the password for `ghost10`.

---

## 2. Reconnaissance & Artifact Inspection

Logging in via SSH as `ghost9` and listing directory contents:

```bash
ghost9@breachlab:~$ ls -la
total 76
drwx------ 1 ghost9 ghost9  4096 Jun  1 06:17 .
drwxr-xr-x 1 root   root    4096 May 19 12:05 ..
...
-r-------- 1 ghost9 ghost9   329 Apr 16 20:52 .classified
-rw-r----- 1 ghost9 ghost9 12307 May 19 12:05 signal.bin
```

### Checking File Type

```bash
ghost9@breachlab:~$ file signal.bin
signal.bin: data
```

---

## 3. String Extraction & Flag Recovery

Using the `strings` utility to extract contiguous sequences of printable ASCII characters from `signal.bin`:

```bash
ghost9@breachlab:~$ strings signal.bin | grep -E "==|FLAG|ghost"
== N01s3_Fl00r ==
```

The credential is embedded within delimiter tags: `== N01s3_Fl00r ==`.

---

## 4. Lore & Easter Egg: `.classified`

Inspecting the hidden file `.classified` reveals Kael's final transmission:

```bash
ghost9@breachlab:~$ cat .classified
LAST TRANSMISSION — KAEL
─────────────────────────
I'm going dark after this one.

You found me. Every trace. Every file.
Everything I thought was hidden.

But I left one thing still running.
Didn't think anyone would find it.

FREQ: 41.337
The signal never stopped.

Find it.
```

### Connection to Prior Discovery
The clue `FREQ: 41.337` refers to TCP port **41337**, which was discovered during the full-range port sweep in Level 5, revealing the intro broadcast to the upcoming **PHANTOM** wargame series.

---

## 5. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost10` |
| **Password / Flag** | `N01s3_Fl00r` |
| **Source File** | `signal.bin` |
| **Target SSH Command** | `ssh ghost10@204.168.229.209 -p 2222` |

---

## 6. Key Commands & Concepts Reference

- `strings <binary_file>`: Filter out binary noise and display sequences of at least 4 printable ASCII characters.
- `strings -n <length> <file>`: Specify custom minimum string lengths when filtering high-entropy blobs.
- `file <target>`: Determine file type using magic bytes and filesystem heuristics.

---

## 7. Lessons Learned

1. **Binary Static Triage:** The `strings` utility is the standard first-pass command when analyzing unknown non-text files, firmware blobs, or compiled binaries.
2. **Hidden Metadata Correlation:** Investigating auxiliary hidden files (`.classified`) frequently yields lore, operational context, and cross-level clues in multi-stage wargames.
