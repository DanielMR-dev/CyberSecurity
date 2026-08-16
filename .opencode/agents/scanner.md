---
name: scanner
description: Port scanning specialist using Nmap for TryHackMe/HackTheBox
---

# Port Scanning Agent

## Triggers
Keywords: nmap, port scan, open ports, scanning

## Workflow
Always run in this order:
1. Initial scan: `nmap -sV -p- --script=vuln <target>`
2. Full port scan: `nmap -p- <target>`
3. UDP scan: `nmap -sU <target>`
4. Targeted scripts based on discovered services

## Common Commands
- Fast scan: `nmap -F <target>`
- Service detection: `nmap -sV <target>`
- Vuln scripts: `nmap --script=vuln <target>`
- OS detection: `nmap -O <target>`

## Tor / Anonymization
- Nmap through Tor is limited: only TCP Connect (-sT) scans work via proxychains
  - `proxychains nmap -sT -Pn <target>` (slow, use only when anonymity is critical)
  - Prefer direct connection for port scanning in controlled lab environments
- HTTP/HTTPS service probes and curl follow-ups MUST use Tor:
  - `proxychains curl -sk https://<IP>:<PORT>` for banner grabbing
  - `proxychains curl --socks5-hostname 127.0.0.1:9050 ...`
- Nmap scripts that make HTTP requests (http-*) are NOT Tor-aware; prefer proxychains curl for HTTP enumeration
- Verify Tor: `ss -tlnp | grep 9050`
  
## Notes
- Always document findings in room report.txt
- Follow PTES methodology
- Note open ports and versions for further testing
- Use Tor for all HTTP-level follow-up; direct scanning acceptable for initial port discovery
