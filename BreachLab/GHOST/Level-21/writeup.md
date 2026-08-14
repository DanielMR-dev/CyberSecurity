# BreachLab - Ghost Track: Level 21 → 22 (Git Archaeology & Tag History)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 21 → 22 (Git Archaeology)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost21`
- **Goal:** Retrieve the password / credentials for `ghost22`
- **Next Connection:** `ssh ghost22@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

The MOTD banner introduces repository forensics:
> *"A git repo was pulled off an internal server. Main is clean now. But tags and abandoned branches remember every secret that was ever committed."*

While the default working tree (`main` branch) has had hardcoded secrets sanitized, Git retains commit objects, dangling trees, reflogs, and tags permanently unless explicitly scrubbed from git database history. The objective is to inspect git repository metadata, discover historical tags or commits in `~/repo`, and extract the leaked `SECRET_KEY` for `ghost22`.

---

## 2. Reconnaissance & Repository Inspection

Logging in via SSH as `ghost21` and locating the target Git repositories:

```bash
ghost21@breachlab:~$ ls -la
total 60
drwx------ 1 ghost21 ghost21 4096 Jun  4 15:26 .
drwxr-xr-x 1 root    root    4096 May 19 12:05 ..
...
drwxrwxr-x 3 ghost21 ghost21 4096 May 29 22:05 newRepo
drwxr-xr-x 1 ghost21 ghost21 4096 May 19 12:12 repo
```

Navigating into `repo/`:

```bash
ghost21@breachlab:~$ cd repo/
```

---

## 3. Git Forensics & Historical Tag Inspection

### Listing Git Tags

Checking for release or development snapshot tags using `git tag`:

```bash
ghost21@breachlab:~/repo$ git tag
v0.9-internal
```

### Inspecting Tag Content and Diff

Using `git show` to examine tag metadata and associated commit diffs:

```bash
ghost21@breachlab:~/repo$ git show v0.9-internal
tag v0.9-internal
Tagger: KAEL <kael@ghost>
Date:   Tue May 19 12:05:24 2026 +0000

snapshot — debug build, do not publish

commit 86143103b696d7a992d58d514cc05be092c3a341 (tag: v0.9-internal)
Author: KAEL <kael@ghost>
Date:   Tue May 19 12:05:24 2026 +0000

    temp: hardcode prod secret for debug trace

diff --git a/config.txt b/config.txt
index 90a29a8..0016c2d 100644
--- a/config.txt
+++ b/config.txt
@@ -1,5 +1,6 @@
 # Ghost Operations Config
-SECRET_KEY=${GHOST_SECRET}
+SECRET_KEY=G1t_H1st0ry
 DATABASE=internal
 REGION=eu-1
 TELEMETRY=on
+DEBUG=true
```

The tagged commit `86143103b696d7a992d58d514cc05be092c3a341` temporarily hardcoded the secret `G1t_H1st0ry` in `config.txt`.

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost22` |
| **Password / Flag** | `G1t_H1st0ry` |
| **Repository Path** | `~/repo` |
| **Leaked Object** | Tag `v0.9-internal` (Commit `8614310`) |
| **Target SSH Command** | `ssh ghost22@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `git tag`: List all annotated and lightweight tags in a repository.
- `git show <tag/commit>`: Inspect the commit message and file diffs associated with a specific git ref.
- `git log --all -p`: Search full commit history across all branches and tags with diff output.
- `git reflog`: View chronological reference updates to discover orphaned or rebased commits.

---

## 6. Lessons Learned

1. **Immutability of Git History:** Simply deleting a secret in subsequent commits does not purge it from repository objects. Historical references, branches, and tags retain previous plaintext versions indefinitely.
2. **Secret Sanitization:** To thoroughly eliminate committed secrets, tools like `git-filter-repo` or BFG Repo-Cleaner must be used to rewrite commit history and purge dangling objects (`git gc --prune=now`).
