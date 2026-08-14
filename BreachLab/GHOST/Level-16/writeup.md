# BreachLab - Ghost Track: Level 16 → 17 (Diff)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 16 → 17 (Diff)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost16`
- **Goal:** Retrieve the password / credentials for `ghost17`
- **Next Connection:** `ssh ghost17@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The MOTD banner for Level 16 describes the challenge:
> *"Two files. Almost identical. The password is the single line that differs. Don't read by eye — this is what diff was built for."*

The objective is to compare two near-identical files (`passwords.new` and `passwords.old`) using the Linux `diff` utility to isolate the single differing line and extract the password for `ghost17`.

---

## 2. Reconnaissance & Artifact Inspection

Logging in via SSH as `ghost16` and inspecting the files:

```bash
ghost16@breachlab:~$ ls -la
total 64
drwx------ 1 ghost16 ghost16 4096 Jun  1 03:40 .
drwxr-xr-x 1 root    root    4096 May 19 12:05 ..
...
-rw-r----- 1 ghost16 ghost16 3293 May 19 12:05 passwords.new
-rw-r----- 1 ghost16 ghost16 3300 May 19 12:05 passwords.old
```

Both files contain 100 structured entries (`entry_0001` through `entry_0100`).

---

## 3. Comparing Files with `diff`

Using `diff` to pinpoint the modification between `passwords.new` and `passwords.old`:

```bash
ghost16@breachlab:~$ diff passwords.new passwords.old
42c42
< entry_0042: D1ff_Sp0ts_1t
---
> entry_0042: 785adf942e7980620803
```

### Alternative Comparison Methods

- **Side-by-side comparison (`diff -y --suppress-common-lines`):**
  ```bash
  diff -y --suppress-common-lines passwords.new passwords.old
  ```
- **Unified Diff (`diff -u`):**
  ```bash
  diff -u passwords.old passwords.new
  ```
- **Using `comm` (requires sorted input):**
  ```bash
  comm -3 <(sort passwords.new) <(sort passwords.old)
  ```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost17` |
| **Password / Flag** | `D1ff_Sp0ts_1t` |
| **Changed Entry** | `entry_0042` |
| **Target SSH Command** | `ssh ghost17@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `diff <file1> <file2>`: Display line-by-line differences between two files.
- `diff -u <file1> <file2>`: Output differences in unified format (commonly used for patches and code reviews).
- `diff -y <file1> <file2>`: Produce a two-column side-by-side difference view.
- `comm -3 <file1> <file2>`: Suppress lines that appear in both files, showing only unique entries to each file.

---

## 6. Lessons Learned

1. **Automated Line Comparison:** Inspecting long data files manually is prone to human error; standard differential tools like `diff` and `cmp` detect subtle character or line variations instantly.
2. **File Version Tracking:** Differential comparison is a fundamental building block of version control systems (e.g. Git) and security auditing tools looking for unauthorized modifications.
