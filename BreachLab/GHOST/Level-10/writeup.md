# BreachLab - Ghost Track: Level 10 → 11 (Binary Strings)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 10 → 11 (Binary Strings)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost10`
- **Goal:** Retrieve the password / credentials for `ghost11`
- **Next Connection:** `ssh ghost11@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The challenge presents a large password dump (`data.txt`) containing hundreds of candidate strings. Every entry in the file appears exactly twice, except for one unique string representing the valid credentials for `ghost11`. The objective is to filter out duplicate lines programmatically using Linux text-processing pipelines (`sort` and `uniq`) rather than manual inspection.

---

## 2. Reconnaissance & Artifact Inspection

Logging in via SSH as `ghost10` and inspecting directory contents:

```bash
ghost10@breachlab:~$ ls -la
total 64
drwx------ 1 ghost10 ghost10  4096 Jun  4 20:32 .
drwxr-xr-x 1 root    root     4096 May 19 12:05 ..
...
-rw-r----- 1 ghost10 ghost10 12015 May 19 12:05 data.txt
```

### Inspecting `data.txt`

The file contains approximately 12 KB of unstructured text strings, each on its own line:

```bash
ghost10@breachlab:~$ wc -l data.txt
# Contains hundreds of paired password entries
```

---

## 3. Data Processing & Unique Line Filtering

The `uniq` utility detects adjacent duplicate lines. Because `uniq` only compares neighboring lines, standard practice requires sorting the file first with `sort`.

### Pipeline Execution

Using `sort` piped into `uniq -u` (*unique only*, printing solely lines with an occurrence count of 1):

```bash
ghost10@breachlab:~$ sort data.txt | uniq -u
Str1ngs_R3v34l
```

### Alternative Approaches

Using `uniq -c` with `grep`:
```bash
ghost10@breachlab:~$ sort data.txt | uniq -c | grep "^[[:space:]]*1[[:space:]]"
      1 Str1ngs_R3v34l
```

Using `awk`:
```bash
ghost10@breachlab:~$ awk '{count[$0]++} END {for (line in count) if (count[line] == 1) print line}' data.txt
Str1ngs_R3v34l
```

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost11` |
| **Password / Flag** | `Str1ngs_R3v34l` |
| **Source File** | `data.txt` |
| **Target SSH Command** | `ssh ghost11@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `sort <file>`: Sort lines of text alphabetically or numerically.
- `uniq -u`: Output only unique lines (lines that appear exactly once in the input).
- `uniq -d`: Output only duplicate lines.
- `uniq -c`: Prefix lines by the number of occurrences.
- `sort <file> | uniq -u`: Canonical shell pipeline for isolating non-repeating data entries.

---

## 6. Lessons Learned

1. **Prerequisite for `uniq`:** `uniq` does not detect non-consecutive duplicates across an entire file; sorting beforehand with `sort` is required to group identical lines.
2. **Set Differential Analysis:** Filtering by frequency count (`uniq -u` or `uniq -c`) is an essential technique for finding anomalies, singletons, and corrupted records in security data sets.
