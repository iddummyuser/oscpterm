# 🔴 Enhanced RedTeam Terminal v2.3 - Complete Manual

## Table of Contents
1. [Overview](#overview)
2. [What's New in v2.3](#whats-new-in-v23)
3. [Installation](#installation)
4. [Quick Start](#quick-start)
5. [Core Features](#core-features)
   - [PTY Support & Real-time Output](#pty-support--real-time-output)
   - [Interactive Commands](#interactive-commands)
   - [Auto-Extraction](#auto-extraction)
6. [Command Reference](#command-reference)
   - [Engagement Management](#engagement-management)
   - [Terminal Recording](#terminal-recording)
   - [Highlights & Extraction](#highlights--extraction)
   - [Logging & Search](#logging--search)
   - [Tagging System](#tagging-system)
   - [Export & Reports](#export--reports)
   - [Screenshots](#screenshots)
   - [Themes & Styling](#themes--styling)
   - [Utilities](#utilities)
7. [Command Aliases](#command-aliases)
8. [Usage Examples](#usage-examples)
9. [Tips & Best Practices](#tips--best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Overview

Enhanced RedTeam Terminal v2.3 is a powerful terminal wrapper designed for penetration testers and security professionals. It provides real-time command output, automatic data extraction, comprehensive logging, and professional reporting capabilities.

### Key Features
- **Real-time Output**: No more waiting for commands to complete
- **Interactive Support**: Use SSH, FTP, SQLMap, and other interactive tools
- **Auto-Extraction**: Automatically identifies IPs, URLs, credentials, and more
- **Professional Documentation**: Generate reports in PDF, HTML, and Markdown
- **Engagement-based Organization**: Keep projects separated and organized

---

## What's New in v2.3

### 🚀 Major Improvements

1. **PTY (Pseudo-Terminal) Support**
   - Real-time output for all commands
   - No buffering issues with long-running scans
   - Progress indicators visible as they happen

2. **Interactive Command Support**
   - Full TTY emulation for interactive tools
   - Support for SSH, FTP, Telnet, MySQL, and more
   - Seamless input/output handling

3. **Automatic Data Extraction**
   - Extracts IPs, URLs, emails, credentials
   - Identifies ports, services, and domains
   - Detects hashes, API keys, and sensitive data

4. **Enhanced Nmap Aliases**
   - Progressive scanning approach
   - Optimized for different scenarios
   - Better timeout management

---

## Installation

### Requirements
- Python 3.7 or higher
- Linux or macOS (Windows via WSL)

### Install Dependencies
```bash
# Core dependencies
pip install rich reportlab pyautogui pillow prompt_toolkit asciinema imageio[ffmpeg]

# Make script executable
chmod +x redterm.py

# Run the tool
./redterm.py
```

### Quick Install Script
```bash
# One-liner installation
curl -sSL https://example.com/install.sh | bash

# Or manual installation
git clone https://github.com/redteam/terminal.git
cd terminal
pip install -r requirements.txt
./redterm.py
```

---

## Quick Start

### First Run
```bash
$ ./redterm.py
🔴 Enhanced RedTeam Terminal v2.3
Features: TTY Support • Auto-Extraction • Real-time Output • Interactive Commands
Type :help for commands | :record start to begin recording

default:~> 
```

### Basic Workflow
```bash
# 1. Create new engagement
default:~> :engage client_test
✅ Engagement set to: client_test

# 2. Start recording
client_test:~> :record start
✅ 🔴 Terminal recording started

# 3. Run reconnaissance
🔴 client_test:~> nmap-quick 192.168.1.0/24
[Real-time output appears here]

# 4. View extracted data
🔴 client_test:~> :highlights
[Shows extracted IPs, ports, etc.]

# 5. Generate report
🔴 client_test:~> :export pdf
✅ PDF report generated: client_test_report.pdf
```

---

## Core Features

### PTY Support & Real-time Output

The terminal now uses pseudo-terminals (PTY) for command execution, providing:

- **Real-time Output**: See results as they happen
- **Progress Indicators**: Watch scan progress live
- **No Buffering**: Immediate feedback from commands
- **Proper Signal Handling**: Ctrl+C works as expected

#### Example: Real-time Nmap Scan
```bash
default:~> nmap-aggressive 192.168.1.100
ℹ️ Executing: nmap -sS -sV -sC -O -A -p- -T4 192.168.1.100
ℹ️ Timeout set to: 7200s (long-running command detected)

Starting Nmap 7.92 ( https://nmap.org )
Stats: 0:00:03 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan
SYN Stealth Scan Timing: About 0.65% done
Stats: 0:00:15 elapsed; 0 hosts completed (1 up), 1 undergoing SYN Stealth Scan
SYN Stealth Scan Timing: About 2.45% done; ETC: 16:40 (0:09:55 remaining)
[... continues in real-time ...]
```

### Interactive Commands

Full support for interactive tools and sessions:

#### Supported Interactive Tools
- **Network**: SSH, Telnet, FTP, Netcat
- **Databases**: MySQL, PostgreSQL, SQLite
- **Frameworks**: Metasploit, SQLMap
- **Editors**: Vim, Nano, Emacs
- **Interpreters**: Python, Ruby, Perl

#### Example: SSH Session
```bash
default:~> ssh user@192.168.1.100
The authenticity of host '192.168.1.100' can't be established.
ECDSA key fingerprint is SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxx.
Are you sure you want to continue connecting (yes/no)? yes
user@192.168.1.100's password: [password input works]
Welcome to Ubuntu 20.04.3 LTS

user@target:~$ whoami
user
user@target:~$ exit
logout
Connection to 192.168.1.100 closed.
✅ Completed in 45.3s
```

### Auto-Extraction

Automatically extracts and categorizes valuable information from command outputs:

#### Extracted Data Types
- **IPs**: IPv4 and IPv6 addresses
- **URLs**: HTTP/HTTPS links
- **Emails**: Email addresses
- **Usernames**: Detected usernames
- **Passwords**: Potential passwords (sanitized)
- **Hashes**: MD5, SHA, NTLM hashes
- **Ports**: Open ports with services
- **Domains**: Domain names
- **API Keys**: Detected API keys
- **Private Keys**: SSH/SSL private keys

#### View Extracted Highlights
```bash
default:~> :highlights

🎯 IPs
┏━━━━━━━━━━━━━━━━━┓
┃ Value           ┃
┡━━━━━━━━━━━━━━━━━┩
│ 192.168.1.100   │
│ 192.168.1.105   │
│ 10.10.10.5      │
└─────────────────┘

🎯 Ports
┏━━━━━━━━━━━━━━━━━┓
┃ Value           ┃
┡━━━━━━━━━━━━━━━━━┩
│ 22:ssh          │
│ 80:http         │
│ 443:https       │
│ 3306:mysql      │
└─────────────────┘

🎯 URLs
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Value                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ http://192.168.1.100/admin      │
│ https://target.com/login.php    │
└─────────────────────────────────┘
```

---

## Command Reference

### Engagement Management

Engagements organize your work by project, client, or assessment.

#### Create/Switch Engagement
```bash
# Create new or switch to existing
:engage project_name
✅ Engagement set to: project_name

# Quick switch to existing
:engage switch project_name
✅ Switched to engagement: project_name

# List all engagements
:engage list
📁 Existing Engagements:
 🔴 default (45 commands, last: 2025-01-08 14:30:22)
 ⚫ project_alpha (23 commands, last: 2025-01-08 12:15:33)
```

### Terminal Recording

Record your entire terminal session for documentation or training.

#### Recording Commands
```bash
# Start recording
:record start
✅ 🔴 Terminal recording started

# Stop recording
:record stop
🟢 Recording saved: recordings/default/recording_20250108_143022.json
✅ Asciinema export: recordings/default/recording_20250108_143022.cast

# List recordings
:record list
┏━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Timestamp           ┃ Duration ┃ File                      ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ 2025-01-08 14:30:22 │ 125.3s   │ recording_20250108_143022 │
└────┴─────────────────────┴──────────┴───────────────────────────┘

# Playback recording
:record play 1
ℹ️ Playing recording from 2025-01-08 14:30:22
ℹ️ Duration: 125.3s
ℹ️ Press Ctrl+C to stop playback
```

### Highlights & Extraction

View and manage automatically extracted data.

#### Highlight Commands
```bash
# View all extracted highlights
:highlights
[Shows categorized extracted data]

# Manually extract from text
:extract "Found server at 192.168.1.50 running on port 8080"
✅ Extraction complete

# Highlights are automatically saved and persist across sessions
```

### Logging & Search

All commands and outputs are automatically logged.

#### Log Commands
```bash
# Show last 5 commands
:log

# Show last N commands
:log 20

# Show all commands
:log full

# Show raw output (unsanitized)
:log raw
```

#### Search Commands
```bash
# Search everything
:search 192.168.1.100

# Search specific field
:search command nmap      # Search in commands only
:search output "open port" # Search in outputs only
:search tags web          # Search in tags only
```

### Tagging System

Organize commands with tags for easy categorization.

```bash
# Tag last command
:tag recon,network,critical

# Search by tags
:search tags critical
```

### Export & Reports

Generate professional documentation in multiple formats.

#### Export Commands
```bash
# Markdown report (default)
:export
✅ Report exported to `default_report.md`

# JSON export
:export json
✅ Report exported to `default_report.json`

# PDF report
:export pdf
✅ PDF report generated: default_report.pdf

# HTML dashboard
:dashboard
✅ HTML Dashboard generated: default_dashboard.html
```

### Screenshots

Capture terminal screenshots with metadata.

```bash
# Manual screenshot
:screenshot
Screenshot description (optional): SQL injection found
✅ Screenshot saved: screenshots/default/screenshot_20250108_154530.png

# Enable auto-screenshot
:screenshot auto
✅ Auto-screenshot enabled

# Toggle auto-screenshot
:screenshot toggle
✅ Auto-screenshot disabled
```

### Themes & Styling

Customize the terminal appearance.

```bash
# List themes
:theme
● default
   Primary: #00ff00 | Success: #00ff00 | Error: #ff0000
○ matrix
   Primary: #00ff41 | Success: #00ff41 | Error: #ff0000
○ stealth
   Primary: #333333 | Success: #00cc00 | Error: #cc0000
○ neon
   Primary: #ff00ff | Success: #33ff66 | Error: #ff3366

# Change theme
:theme matrix
✅ Theme set to: matrix
```

### Utilities

#### Status
```bash
:status
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property             ┃ Value                      ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Current Engagement   │ default                    │
│ Current Directory    │ /home/user                 │
│ Theme               │ default                    │
│ Auto-Screenshot     │ Disabled                   │
│ Recording           │ 🔴 ACTIVE                  │
│ Extracted Highlights│ 47                         │
│ Total Commands      │ 123                        │
│ Success Rate        │ 94.3%                      │
└─────────────────────┴────────────────────────────┘
```

#### Other Utilities
```bash
# Show command aliases
:alias

# Clear engagement data
:clear
⚠️ Delete ALL logs for engagement 'default'? [y/N]: 

# Show help
:help

# Exit terminal
:exit
```

---

## Command Aliases

Pre-configured shortcuts for common penetration testing tools.

### Nmap Aliases

```bash
# Progressive scanning approach
nmap-ping <target>        # Host discovery only (-sn)
nmap-quick <target>       # Top 100 ports, fast (-sS --top-ports 100 -T4)
nmap-common <target>      # Top 1000 ports with versions (-sS --top-ports 1000 -sV -T4)
nmap-full <target>        # Top 5000 with scripts (-sS -sV -sC -O --top-ports 5000)
nmap-aggressive <target>  # All 65535 ports (-sS -sV -sC -O -A -p- -T4)
nmap-stealth <target>     # Stealthy scan (-sS -Pn -T2 --top-ports 1000)
nmap-udp <target>         # UDP scan (-sU --top-ports 100 -T4)
nmap-vulns <target>       # Vulnerability scripts (-sV --script vuln)
nmap-smb <target>         # SMB enumeration (-p445,139 --script smb-enum*)
nmap-web <target>         # Web enumeration (-p80,443,8080,8443 -sV --script http-enum)
```

### Directory Enumeration

```bash
gobuster-common <url>     # Common wordlist with 30 threads
gobuster-big <url>        # Big wordlist with 50 threads
gobuster-files <url>      # Search for files with extensions
dirbuster <url>           # Alternative directory brute-forcer
```

### Other Tool Aliases

```bash
nikto-scan <target>       # Web vulnerability scanner
nc-listen <port>          # Netcat listener
nc-connect <ip> <port>    # Netcat connection
enum4linux <target>       # SMB enumeration
smbclient-list <target>   # List SMB shares
whatweb <url>             # Web technology identifier
searchsploit <term>       # Exploit database search
msfconsole                # Metasploit console (quiet mode)
hydra-ssh <user> <passlist> <target>  # SSH brute-force
sqlmap-test <url>         # Basic SQLMap test
masscan-quick <target>    # Fast port scanner
```

---

## Usage Examples

### Complete Penetration Test Workflow

```bash
# 1. Setup engagement and recording
default:~> :engage client_pentest_2025
✅ Engagement set to: client_pentest_2025

client_pentest_2025:~> :record start
✅ 🔴 Terminal recording started

# 2. Network discovery
🔴 client_pentest_2025:~> nmap-ping 192.168.1.0/24
[... real-time output shows live hosts ...]
🔴 client_pentest_2025:~> :tag discovery,network

# 3. Port scanning (progressive approach)
🔴 client_pentest_2025:~> nmap-quick 192.168.1.100
[... finds open ports 22, 80, 443 ...]

🔴 client_pentest_2025:~> nmap-full 192.168.1.100
[... detailed service enumeration ...]
🔴 client_pentest_2025:~> :tag target-host,detailed-scan

# 4. Web enumeration
🔴 client_pentest_2025:~> gobuster-common http://192.168.1.100
[... finds /admin, /backup, /api ...]
🔴 client_pentest_2025:~> :tag web-enum,interesting

# 5. Check extracted data
🔴 client_pentest_2025:~> :highlights
[... shows all extracted IPs, URLs, services ...]

# 6. Interactive testing
🔴 client_pentest_2025:~> sqlmap-test http://192.168.1.100/page?id=1
[... interactive SQLMap session ...]

# 7. Screenshot important findings
🔴 client_pentest_2025:~> :screenshot
Screenshot description: SQL injection confirmed on login page

# 8. Generate reports
🔴 client_pentest_2025:~> :record stop
🔴 client_pentest_2025:~> :export pdf
🔴 client_pentest_2025:~> :dashboard
```

### Interactive SSH Session

```bash
# Direct SSH with full interactivity
default:~> ssh pentester@10.10.10.5
pentester@10.10.10.5's password: [interactive password input]
Welcome to Ubuntu 20.04.3 LTS

pentester@target:~$ sudo -l
[sudo] password for pentester: [interactive sudo password]
User pentester may run the following commands:
    (ALL : ALL) /usr/bin/python3

pentester@target:~$ exit
✅ Completed in 234.5s
```

### Real-time Vulnerability Scanning

```bash
# Nikto scan with live output
default:~> nikto-scan http://192.168.1.100
- Nikto v2.1.6
---------------------------------------------------------------------------
+ Target IP:          192.168.1.100
+ Target Hostname:    192.168.1.100
+ Target Port:        80
+ Start Time:         2025-01-08 16:45:23
---------------------------------------------------------------------------
+ Server: Apache/2.4.41 (Ubuntu)
+ The anti-clickjacking X-Frame-Options header is not present.
[... continues with findings as they're discovered ...]
```

### Using Highlights for Intelligence Gathering

```bash
# After running various scans
default:~> :highlights

🎯 IPs (15 found)
┏━━━━━━━━━━━━━━━━━┓
┃ Value           ┃
┡━━━━━━━━━━━━━━━━━┩
│ 192.168.1.1     │
│ 192.168.1.100   │
│ 192.168.1.105   │
│ 10.10.10.5      │
│ 172.16.0.1      │
└─────────────────┘

🎯 Services (8 found)
┏━━━━━━━━━━━━━━━━━┓
┃ Value           ┃
┡━━━━━━━━━━━━━━━━━┩
│ 22:ssh          │
│ 80:http         │
│ 443:https       │
│ 3306:mysql      │
│ 8080:http-proxy │
└─────────────────┘

🎯 URLs (12 found)
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Value                              ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ http://192.168.1.100/admin         │
│ http://192.168.1.100/backup        │
│ https://192.168.1.100/api/v1       │
│ http://192.168.1.100/phpmyadmin    │
└────────────────────────────────────┘
```

---

## Tips & Best Practices

### 1. Progressive Scanning
Start with quick scans and progressively go deeper:
```bash
nmap-ping → nmap-quick → nmap-common → nmap-full → nmap-aggressive
```

### 2. Use Tags Effectively
Create a consistent tagging taxonomy:
- **Phase**: `recon`, `enum`, `exploit`, `post-exploit`
- **Type**: `network`, `web`, `database`, `credential`
- **Priority**: `critical`, `high`, `medium`, `low`

### 3. Regular Exports
Export data regularly to avoid loss:
```bash
# Quick markdown export after each phase
:export

# Full PDF report at milestones
:export pdf
```

### 4. Leverage Auto-Extraction
Review highlights frequently:
```bash
# Check after each scan
:highlights

# Export includes all highlights
:export json
```

### 5. Interactive Tool Usage
For interactive tools, the terminal handles I/O seamlessly:
- Password prompts work normally
- Tab completion functions
- Ctrl+C interrupts cleanly
- Sessions remain stable

### 6. Recording Best Practices
- Start recording at engagement beginning
- Stop recording before generating reports
- Recordings capture everything for training/review

---

## Troubleshooting

### Common Issues

#### 1. Command Output Not Showing
- **Issue**: Command seems to hang with no output
- **Solution**: The PTY support should prevent this, but if it occurs:
  ```bash
  # Use Ctrl+C to interrupt
  # Check if command requires sudo
  # Verify network connectivity
  ```

#### 2. Interactive Commands Not Working
- **Issue**: Can't type in SSH/FTP sessions
- **Solution**: Ensure terminal is in proper mode:
  ```bash
  # The tool handles TTY automatically
  # If issues persist, check terminal emulator settings
  # Try running outside tmux/screen first
  ```

#### 3. Extraction Missing Data
- **Issue**: Some IPs/URLs not extracted
- **Solution**: Manually extract:
  ```bash
  :extract "The server IP is 192.168.1.200"
  ```

#### 4. Recording Playback Issues
- **Issue**: Recording won't play back
- **Solution**: 
  ```bash
  # Check recording exists
  :record list
  
  # Verify file permissions
  ls -la recordings/[engagement]/
  ```

#### 5. Performance Issues
- **Issue**: Terminal feels slow
- **Solution**:
  ```bash
  # Disable auto-screenshot if not needed
  :screenshot toggle
  
  # Export and clear old logs
  :export
  :clear
  ```

### Debug Mode
For troubleshooting, run with debug output:
```bash
python3 redterm.py --debug
```

### Getting Help
- Use `:help` for built-in documentation
- Check GitHub issues for known problems
- Submit bug reports with `:status` output

---

## Conclusion

Enhanced RedTeam Terminal v2.3 transforms your command-line workflow with real-time output, automatic intelligence gathering, and comprehensive documentation capabilities. The PTY support ensures all tools work as expected, while auto-extraction saves valuable time in identifying important data.

Whether you're conducting a quick security assessment or a full penetration test, this tool provides the framework to work efficiently while maintaining detailed documentation of your activities.

Happy hacking! 🚀
