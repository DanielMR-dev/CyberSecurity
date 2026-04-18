## Recon Findings

- Target IP: 10.65.163.160
- Hostname: JON-PC
- OS: Windows 7 Professional 7601 Service Pack 1
- Workgroup: WORKGROUP
- Open ports:
  - 135/tcp msrpc
  - 139/tcp netbios-ssn
  - 445/tcp microsoft-ds
  - 3389/tcp rdp
  - 49152/tcp msrpc
  - 49153/tcp msrpc
  - 49154/tcp msrpc
  - 49161/tcp msrpc

## Initial Assessment

- SMB exposed on 445
- Target appears to be a Windows 7 SP1 host
- Strong candidate for MS17-010 (EternalBlue)

## Gain Access

- Vulnerability confirmed: MS17-010 (EternalBlue)
- Exploit used: exploit/windows/smb/ms17_010_eternalblue
- Result: Successful Meterpreter session

## Session Details

- Session type: Meterpreter x64/windows
- Target host: JON-PC
- OS: Windows 7 SP1 x64
- Current user: NT AUTHORITY\SYSTEM

## Escalation

- No manual privilege escalation required
- Initial shell already had SYSTEM privileges
