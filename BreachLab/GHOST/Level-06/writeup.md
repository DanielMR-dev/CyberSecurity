# BreachLab - Ghost Track: Level 6 → 7 (Ghost in the Machine)

## General Information

- **Platform:** [BreachLab](https://breachlab.org)
- **Track:** Ghost Track
- **Level:** Level 6 → 7 (Ghost in the Machine)
- **Host:** `204.168.229.209`
- **Port:** `2222`
- **Current User:** `ghost6`
- **Goal:** Retrieve the password / credentials for `ghost7`
- **Next Connection:** `ssh ghost7@204.168.229.209 -p 2222`

---

## 1. Scenario & Objectives

After prior security incidents, analyst **Kael** stopped storing credentials in plain text on disk and instead exported runtime secrets into process environment variables. The objective is to inspect the shell environment, identify Base64-encoded strings, and decode the sensitive parameter to extract the authentication password for `ghost7`.

---

## 2. Reconnaissance & Environment Inspection

Logging in via SSH as `ghost6` and dumping all active environment variables with `env`:

```bash
ghost6@breachlab:~$ env
SHELL=/bin/bash
METRICS_ENABLED=false
REGION=eu-central-1
LOG_LEVEL=minimal
HISTSIZE=1000
API_DIGEST=M252X0wzNGtzXzN2M3J5dGgxbmc=
TRACE_SALT=bW9uaXRvcmluZ19rZXlfZGVsdGE3
PWD=/home/ghost6
LOGNAME=ghost6
MAX_RETRIES=3
NODE_ID=ghost-analyst-07
RUNTIME_TOKEN=c3lzdGVtX3Rva2VuX2dhbW1hX3Yz
MOTD_SHOWN=pam
HOME=/home/ghost6
LANG=C.UTF-8
...
CACHE_SEED=bm90X2FfcmVhbF9jcmVkZW50aWFs
BUILD_ID=a3f7b2c1
SESSION_HASH=d4e5f6a7b8
```

---

## 3. Base64 Analysis & Flag Extraction

### Identifying Suspicious Variables

Several variables exhibited standard Base64 encoding padding and character sets:
- `API_DIGEST=M252X0wzNGtzXzN2M3J5dGgxbmc=`
- `TRACE_SALT=bW9uaXRvcmluZ19rZXlfZGVsdGE3`
- `RUNTIME_TOKEN=c3lzdGVtX3Rva2VuX2dhbW1hX3Yz`
- `CACHE_SEED=bm90X2FfcmVhbF9jcmVkZW50aWFs`

### Decoding `API_DIGEST`

Decoding the `API_DIGEST` string using the `base64` utility:

```bash
ghost6@breachlab:~$ echo -n "M252X0wzNGtzXzN2M3J5dGgxbmc=" | base64 -d
3nv_L34ks_3v3ryth1ng
```

### Decoding Contextual Variables (Decoys & Metadata)

- `echo -n "bW9uaXRvcmluZ19rZXlfZGVsdGE3" | base64 -d` → `monitoring_key_delta7`
- `echo -n "c3lzdGVtX3Rva2VuX2dhbW1hX3Yz" | base64 -d` → `system_token_gamma_v3`
- `echo -n "bm90X2FfcmVhbF9jcmVkZW50aWFs" | base64 -d` → `not_a_real_credential`

The valid password for `ghost7` is recovered from `API_DIGEST`.

---

## 4. Flag / Credentials Retrieved

| Parameter | Value |
| :--- | :--- |
| **Next User** | `ghost7` |
| **Password / Flag** | `3nv_L34ks_3v3ryth1ng` |
| **Source Variable** | `API_DIGEST` |
| **Target SSH Command** | `ssh ghost7@204.168.229.209 -p 2222` |

---

## 5. Key Commands & Concepts Reference

- `env` / `printenv`: Display all exported environment variables in the active shell.
- `echo -n "<string>" | base64 -d`: Decode Base64-encoded strings without appending trailing newlines.
- `/proc/$$/environ`: Alternative kernel view of process environment variables (separated by null bytes: `strings /proc/$$/environ`).

---

## 6. Lessons Learned

1. **Environment Variables Are Not Secrets:** While 12-Factor App methodology recommends configuring applications via environment variables, unencrypted secrets in `env` remain visible to any process running under that user context or readable via `/proc/<pid>/environ`.
2. **Encoding vs. Encryption:** Base64 is an encoding scheme for data representation, providing zero cryptographic confidentiality.
