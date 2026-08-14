# BreachLab - Ghost Track: Level 3 → 4 (Access Denied)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 3 → 4 (Access Denied)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost3`
- **Goal:** Retrieve the password / credentials for `ghost4`
- **Next Connection:** `ssh ghost4@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

Analyst **Kael** organized his intelligence storage under `/var/intel/` with specific Linux group permissions. The objective is to understand Linux group-based access control, locate the restricted storage tier accessible by your assigned group (`analysts`), and extract the authentication credentials for `ghost4`.

---

## 2. Reconnaissance & Storage Mapping

Logging into the `ghost3` session and inspecting files in the home directory:

```bash
ghost3@breachlab:~$ ls -la
total 64
drwx------ 1 ghost3 ghost3 4096 Jun  1 20:54 .
drwxr-xr-x 1 root   root   4096 May 19 12:05 ..
...
-rw-r----- 1 ghost3 ghost3  308 Apr 17 09:44 map.txt
```

### Inspecting `map.txt`

```bash
ghost3@breachlab:~$ cat map.txt
KAEL'S STORAGE LAYOUT
=====================
Recovered from workstation. Partially redacted.

  /var/intel/public/   — world readable
  /var/intel/ops/      — restricted
  /var/intel/archive/  — root only

Access follows the group scheme. The kernel will
tell you what you are, if you ask it.

— KAEL
```

---

## 3. Filesystem Permissions & Group Access Analysis

### Inspecting `/var/intel`

Navigating to `/var/intel` and checking the access control list / permissions:

```bash
ghost3@breachlab:~$ cd /var/intel
ghost3@breachlab:/var/intel$ ls -la
total 28
drwxr-xr-x 1 root root     4096 May 19 12:05 .
drwxr-xr-x 1 root root     4096 May 19 12:05 ..
drwx------ 2 root root     4096 May 19 12:05 archive
drwxr-x--- 1 root analysts 4096 May 19 12:05 ops
drwxr-xr-x 1 root root     4096 May 19 12:05 public
```

### Permissions Breakdown

| Directory | Owner / Group | Permissions | Access for `ghost3` |
| :--- | :--- | :--- | :--- |
| `archive/` | `root:root` | `drwx------` (700) | ❌ Denied (Root only) |
| `ops/` | `root:analysts` | `drwxr-x---` (750) | ✅ Allowed (`ghost3` in group `analysts`) |
| `public/` | `root:root` | `drwxr-xr-x` (755) | ✅ Allowed (World-readable) |

---

## 4. Extracting Credentials

Navigating into the restricted `/var/intel/ops/` directory:

```bash
ghost3@breachlab:/var/intel$ cd ops
ghost3@breachlab:/var/intel/ops$ ls
access_codes.dat  operative_list.txt

ghost3@breachlab:/var/intel/ops$ cat operative_list.txt
INDEX OF ACTIVE OPERATIONS
Classification: Analyst Only

See access_codes.dat for current credentials.

ghost3@breachlab:/var/intel/ops$ cat access_codes.dat
P3rm1ss10ns_M4tt3r
```

---

## 5. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost4` |
| **Password / Flag** | `P3rm1ss10ns_M4tt3r` |
| **Target SSH Command** | `ssh ghost4@204.168.229.209 -p 2222` |

---

## 6. Key Commands & Concepts Reference

- `id`: Display current user identity, UID, GID, and secondary group memberships.
- `ls -la`: Inspect ownership, group assignments, and standard POSIX permission bits (`rwxrwxrwx`).
- `chmod` / `chown`: Manage read, write, and execute permissions across user, group, and others.

---

## 7. Lessons Learned

1. **POSIX Group Permissions:** In multi-user Linux environments, group permissions (`r-x`) allow granular delegation of read/execute rights to specific operational roles without granting root access.
2. **Access Enumeration:** Checking user group memberships (`id` or `groups`) helps immediately identify what restricted filesystem areas are reachable.
