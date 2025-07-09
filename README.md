# 🔴 Enhanced RedTeam Terminal v2.2 - Complete Manual

## Table of Contents
1. [Installation & Setup](#installation--setup)
2. [Engagement Management](#engagement-management)
3. [Terminal Recording](#terminal-recording)
4. [Command Execution](#command-execution)
5. [Logging & Search](#logging--search)
6. [Tagging System](#tagging-system)
7. [Export & Reports](#export--reports)
8. [Screenshots](#screenshots)
9. [Themes & Styling](#themes--styling)
10. [Utilities](#utilities)
11. [Command Aliases](#command-aliases)
12. [Advanced Usage Examples](#advanced-usage-examples)
13. [Tips & Best Practices](#tips--best-practices)
14. [File Structure](#file-structure)

---

## Installation & Setup

### Requirements
```bash
# Install Python dependencies
pip install rich reportlab pyautogui pillow prompt_toolkit asciinema imageio[ffmpeg]

# Make script executable
chmod +x redterm.py

# Run the tool
./redterm.py
```

### First Launch
```bash
$ ./redterm.py
🔴 Enhanced RedTeam Terminal v2.2
Features: Terminal Recording • HTML Dashboard • Extended Timeouts • Auto-Screenshots
Type :help for commands | :record start to begin recording

default:~> 
```

---

## Engagement Management

Engagements help organize different projects, clients, or testing scenarios. Each engagement maintains its own logs, recordings, and screenshots.

### Create/Switch Engagement
```bash
# Create new engagement
default:~> :engage project_alpha
✅ Engagement set to: project_alpha

# Quick switch to existing engagement
project_alpha:~> :engage switch default
✅ Switched to engagement: default
```

### List All Engagements
```bash
default:~> :engage list

📁 Existing Engagements:
 🔴 default (45 commands, last: 2025-01-08 14:30:22)
 ⚫ project_alpha (23 commands, last: 2025-01-08 12:15:33)
 ⚫ client_beta (67 commands, last: 2025-01-07 18:45:12)
```

---

## Terminal Recording

Record entire terminal sessions with precise timing for playback, documentation, and training purposes.

### Start Recording
```bash
default:~> :record start
✅ 🔴 Terminal recording started
ℹ️ Use :record stop to end recording

# Prompt now shows recording indicator
🔴 default:~> 
```

### Stop Recording
```bash
🔴 default:~> :record stop
🟢 Recording saved: recordings/default/recording_20250108_143022.json
ℹ️ Duration: 125.3 seconds
✅ Asciinema export: recordings/default/recording_20250108_143022.cast
```

### List Recordings
```bash
default:~> :record list

┏━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ID ┃ Timestamp           ┃ Duration ┃ File                      ┃
┡━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 1  │ 2025-01-08 14:30:22 │ 125.3s   │ recording_20250108_143022 │
│ 2  │ 2025-01-08 15:45:10 │ 87.2s    │ recording_20250108_154510 │
└────┴─────────────────────┴──────────┴───────────────────────────┘
```

### Playback Recording
```bash
default:~> :record play 1
ℹ️ Playing recording from 2025-01-08 14:30:22
ℹ️ Duration: 125.3s
ℹ️ Press Ctrl+C to stop playback

default:~> nmap -sS -O -sV --top-ports 1000 192.168.1.100
[... playback continues in real-time ...]
```

---

## Command Execution

Execute system commands with automatic logging, timing, and output capture.

### Basic Commands
```bash
# Regular shell commands
default:~> ls -la
total 24
drwxr-xr-x  6 user user 4096 Jan  8 14:30 .
drwxr-xr-x 12 user user 4096 Jan  8 10:15 ..
-rw-r--r--  1 user user 8192 Jan  8 14:30 redterm_logs.db

# Change directory (persistent)
default:~> cd /tmp
✅ Changed directory to: /tmp
default:tmp> pwd
/tmp
```

### Using Command Aliases
```bash
# Quick nmap scan
default:~> nmap-quick 192.168.1.100
ℹ️ Executing: nmap -sS -O -sV --top-ports 1000 192.168.1.100
[... nmap output ...]
✅ Completed in 45.2s

# Full nmap scan (with extended timeout)
default:~> nmap-full 192.168.1.100
ℹ️ Executing: nmap -sS -sV -sC -O -A -p- 192.168.1.100
ℹ️ Timeout set to: 3600s (long-running command detected)
[... nmap output ...]
✅ Completed in 1523.7s

# Directory enumeration
default:~> gobuster-common http://target.com
ℹ️ Executing: gobuster dir -u http://target.com -w /usr/share/wordlists/dirb/common.txt
ℹ️ Timeout set to: 1800s (long-running command detected)
[... gobuster output ...]
```

### Command Timeouts
- **Default**: 60 seconds
- **nmap**: 3600 seconds (1 hour)
- **gobuster**: 1800 seconds (30 minutes)
- **nikto**: 1800 seconds
- **hydra**: 3600 seconds
- **enum4linux**: 1800 seconds

---

## Logging & Search

All commands and outputs are automatically logged with sanitization for sensitive data.

### View Logs
```bash
# Show last 5 commands
default:~> :log

┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━┳━━━━━━━┓
┃ Time                ┃ Status ┃ Command                       ┃ Duration ┃ Dir ┃ Tags  ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━╇━━━━━━━┩
│ 2025-01-08 14:30:22 │ ✅     │ nmap-quick 192.168.1.100      │ 45.2s    │ ~   │ recon │
│ 2025-01-08 14:31:15 │ ✅     │ gobuster-common http://ta...  │ 123.5s   │ ~   │ enum  │
│ 2025-01-08 14:33:45 │ ❌     │ hydra -l admin -P pass.txt   │ 60.0s    │ tmp │       │
└─────────────────────┴────────┴───────────────────────────────┴──────────┴─────┴───────┘

# Show last 10 commands
default:~> :log 10

# Show all commands
default:~> :log full

# Show raw output (unsanitized)
default:~> :log raw
```

### Search Commands
```bash
# Search all fields
default:~> :search nmap
🔍 Search Results for 'nmap' in all:

[🕒 2025-01-08 14:30:22] 🏷️[recon]
➤ nmap-quick 192.168.1.100
Starting Nmap 7.92...

# Search in specific field
default:~> :search command hydra
🔍 Search Results for 'hydra' in command:

[🕒 2025-01-08 14:33:45]
➤ hydra -l admin -P passwords.txt ssh://192.168.1.100
Hydra v9.2 starting...

# Search by tags
default:~> :search tags recon
🔍 Search Results for 'recon' in tags:

[🕒 2025-01-08 14:30:22] 🏷️[recon]
➤ nmap-quick 192.168.1.100
```

### Search Types
- **all**: Search in commands, outputs, and tags
- **command**: Search only in executed commands
- **output**: Search only in command outputs
- **tags**: Search only in tags

---

## Tagging System

Tag commands for easy categorization and retrieval.

### Tag Last Command
```bash
# Execute a command
default:~> nikto-scan http://target.com
[... nikto output ...]
✅ Completed in 234.5s

# Tag it
default:~> :tag webapp,vulnerability,critical
🏷️ Tagged last command with: webapp,vulnerability,critical
```

### Common Tag Examples
- **recon**: Initial reconnaissance
- **enum**: Enumeration activities
- **webapp**: Web application testing
- **network**: Network-level testing
- **exploit**: Exploitation attempts
- **privesc**: Privilege escalation
- **critical**: Critical findings
- **todo**: Follow-up required

---

## Export & Reports

Generate professional reports in multiple formats.

### Markdown Export
```bash
default:~> :export
✅ Report exported to `default_report.md`

# Contents preview:
# Red Team Report: `default`
Generated: 2025-01-08T15:45:30
## 📊 Executive Summary
- Total Commands: 45
- Average Execution Time: 87.3s
```

### JSON Export
```bash
default:~> :export json
✅ Report exported to `default_report.json`

# JSON structure:
{
  "engagement": "default",
  "generated": "2025-01-08T15:45:30",
  "commands": [
    {
      "id": 1,
      "command": "nmap-quick 192.168.1.100",
      "output": "...",
      "execution_time": 45.2,
      "status": "success",
      "tags": "recon"
    }
  ]
}
```

### PDF Report
```bash
default:~> :export pdf
✅ PDF report generated: default_report.pdf

# Professional PDF includes:
# - Title page with engagement details
# - Executive summary with statistics
# - Command timeline with outputs
# - Sanitized sensitive information
# - Professional formatting
```

### HTML Dashboard
```bash
default:~> :dashboard
✅ HTML Dashboard generated: default_dashboard.html

# Interactive dashboard features:
# - Real-time statistics cards
# - Command success/failure pie chart
# - Top commands bar chart
# - Tag usage radar chart
# - Recent commands timeline
# - Dark theme with matrix-style colors
```

---

## Screenshots

Capture terminal screenshots with metadata overlay.

### Manual Screenshot
```bash
default:~> :screenshot
Screenshot description (optional): Found SQL injection vulnerability
✅ Screenshot saved: screenshots/default/screenshot_20250108_154530.png

# Screenshot includes:
# - Terminal content
# - Timestamp overlay
# - Engagement name
# - Custom description
```

### Auto-Screenshot Mode
```bash
# Enable auto-screenshot
default:~> :screenshot auto
✅ Auto-screenshot enabled

# Now screenshots are taken after each command
default:~> sqlmap -u "http://target.com/page?id=1"
[... sqlmap output ...]
✅ Completed in 156.7s
✅ Screenshot saved: screenshots/default/screenshot_20250108_154730.png

# Toggle off
default:~> :screenshot toggle
✅ Auto-screenshot disabled
```

---

## Themes & Styling

Customize terminal appearance with built-in themes.

### List Available Themes
```bash
default:~> :theme
Available Themes:
● default
   Primary: #00ff00 | Success: #00ff00 | Error: #ff0000
○ matrix
   Primary: #00ff41 | Success: #00ff41 | Error: #ff0000
○ stealth
   Primary: #333333 | Success: #00cc00 | Error: #cc0000
○ neon
   Primary: #ff00ff | Success: #33ff66 | Error: #ff3366
```

### Change Theme
```bash
default:~> :theme matrix
✅ Theme set to: matrix

# Terminal now uses Matrix-style green colors

default:~> :theme stealth
✅ Theme set to: stealth

# Subdued colors for discreet operation
```

### Theme Descriptions
- **default**: Classic green terminal
- **matrix**: Matrix movie inspired
- **stealth**: Low visibility, dark colors
- **neon**: Bright, cyberpunk aesthetic

---

## Utilities

### Show Status
```bash
default:~> :status

┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property             ┃ Value                      ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Current Engagement   │ default                    │
│ Current Directory    │ /home/user                 │
│ Theme               │ default                    │
│ Auto-Screenshot     │ Disabled                   │
│ Recording           │ 🔴 ACTIVE                  │
│ Last Command        │ nmap-quick 192.168.1.100   │
│ Last Execution      │ 2025-01-08 14:30:22 (45.2s)│
│ Total Commands      │ 45                         │
│ Average Time        │ 87.3s                      │
│ Success Rate        │ 91.1%                      │
└─────────────────────┴────────────────────────────┘
```

### Clear Engagement Data
```bash
default:~> :clear
⚠️ Delete ALL logs for engagement 'default'? [y/N]: y
✅ Logs for `default` cleared.

# This removes:
# - All command logs
# - All screenshots
# - All recordings
# - All associated data
```

### Show Help
```bash
default:~> :help

🔧 Enhanced RedTeam Terminal Commands:

📁 ENGAGEMENT MANAGEMENT:
  :engage <name>              → Create/switch to engagement
  :engage switch <name>       → Switch to existing engagement  
  :engage list                → List all engagements with stats

📼 TERMINAL RECORDING:
  :record start               → Start terminal recording
  :record stop                → Stop and save recording
  :record list                → List all recordings
  :record play <id>           → Playback a recording
  :record export <id> gif     → Export recording to GIF (coming soon)

[... complete help text ...]
```

### Exit Terminal
```bash
default:~> :exit
👋 Goodbye! Stay safe out there.

# If recording is active:
🔴 default:~> :exit
⚠️ Recording in progress!
Stop recording and exit? [y/N]: y
🟢 Recording saved: recordings/default/recording_20250108_160000.json
👋 Goodbye! Stay safe out there.
```

---

## Command Aliases

Pre-configured shortcuts for common penetration testing tools.

### List All Aliases
```bash
default:~> :alias

🔧 Available Aliases:
  nmap-quick           → nmap -sS -O -sV --top-ports 1000 {}
  nmap-full            → nmap -sS -sV -sC -O -A -p- {}
  nmap-udp             → nmap -sU --top-ports 1000 {}
  gobuster-common      → gobuster dir -u {} -w /usr/share/wordlists/dirb/common.txt
  gobuster-big         → gobuster dir -u {} -w /usr/share/wordlists/dirb/big.txt
  nikto-scan           → nikto -h {}
  nc-listen            → nc -lvnp {}
  nc-connect           → nc {} {}
  enum4linux           → enum4linux -a {}
  smbclient-list       → smbclient -L {} -N
  dirbuster            → dirb {} /usr/share/wordlists/dirb/common.txt
  whatweb              → whatweb {}
  searchsploit         → searchsploit {}
  msfconsole           → msfconsole -q
  burp-proxy           → java -jar /opt/burpsuite/burpsuite_community.jar
  hydra-ssh            → hydra -l {} -P {} ssh://{}
```

### Using Aliases

#### Single Parameter
```bash
default:~> nmap-quick 192.168.1.100
ℹ️ Executing: nmap -sS -O -sV --top-ports 1000 192.168.1.100

default:~> enum4linux 192.168.1.100
ℹ️ Executing: enum4linux -a 192.168.1.100
```

#### Multiple Parameters
```bash
default:~> hydra-ssh admin passwords.txt 192.168.1.100
ℹ️ Executing: hydra -l admin -P passwords.txt ssh://192.168.1.100

default:~> nc-connect 192.168.1.100 4444
ℹ️ Executing: nc 192.168.1.100 4444
```

#### No Parameters
```bash
default:~> msfconsole
ℹ️ Executing: msfconsole -q

default:~> burp-proxy
ℹ️ Executing: java -jar /opt/burpsuite/burpsuite_community.jar
```

---

## Advanced Usage Examples

### Complete Penetration Test Workflow
```bash
# 1. Start new engagement with recording
default:~> :engage client_pentest
✅ Engagement set to: client_pentest
client_pentest:~> :record start
✅ 🔴 Terminal recording started

# 2. Initial reconnaissance
🔴 client_pentest:~> nmap-quick 10.10.10.0/24
[... output ...]
🔴 client_pentest:~> :tag network-scan,initial-recon

# 3. Detailed scan of discovered host
🔴 client_pentest:~> nmap-full 10.10.10.5
[... output ...]
🔴 client_pentest:~> :tag detailed-scan,target-host

# 4. Web enumeration
🔴 client_pentest:~> gobuster-common http://10.10.10.5
[... output ...]
🔴 client_pentest:~> :tag web-enum,port-80

# 5. Take screenshot of interesting finding
🔴 client_pentest:~> :screenshot
Screenshot description: Admin panel discovered at /admin
✅ Screenshot saved

# 6. Vulnerability scanning
🔴 client_pentest:~> nikto-scan http://10.10.10.5
[... output ...]
🔴 client_pentest:~> :tag vuln-scan,critical

# 7. Stop recording and generate reports
🔴 client_pentest:~> :record stop
🟢 Recording saved
client_pentest:~> :export pdf
✅ PDF report generated
client_pentest:~> :dashboard
✅ HTML Dashboard generated
```

### Searching and Filtering Results
```bash
# Find all critical findings
default:~> :search tags critical

# Find all commands that failed
default:~> :search output "error"

# Find specific tool usage
default:~> :search command sqlmap

# View detailed logs for investigation
default:~> :log 20

# Search for specific IP addresses
default:~> :search 192.168.1.100
```

### Multi-Engagement Workflow
```bash
# Working on multiple projects
default:~> :engage list
📁 Existing Engagements:
 🔴 client_a (145 commands)
 ⚫ client_b (89 commands)
 ⚫ research (234 commands)

# Quick switch between engagements
client_a:~> :engage switch research
✅ Switched to engagement: research

# Check status of current engagement
research:~> :status
```

### Theme Usage for Different Scenarios
```bash
# Stealth mode for sensitive environments
default:~> :theme stealth
✅ Theme set to: stealth

# High visibility for demonstrations
default:~> :theme neon
✅ Theme set to: neon

# Classic hacker aesthetic
default:~> :theme matrix
✅ Theme set to: matrix
```

---

## Tips & Best Practices

### 1. Organization
- **Always use engagements** to separate different projects
- **Name engagements descriptively**: `client_name_YYYY-MM-DD`
- **Tag consistently** using a predefined taxonomy

### 2. Documentation
- **Enable recording** for complex test scenarios
- **Take screenshots** of all critical findings
- **Add descriptions** to manual screenshots
- **Export reports** at regular intervals

### 3. Security
- **Logs are automatically sanitized** to remove passwords/tokens
- **Use `:log raw`** carefully as it shows unsanitized data
- **Clear engagements** after project completion

### 4. Efficiency
- **Use aliases** instead of typing full commands
- **Leverage search** to find previous work
- **Set appropriate themes** for your environment
- **Enable auto-screenshot** for visual-heavy testing

### 5. Reporting
- **Generate HTML dashboards** for executive summaries
- **Use PDF exports** for formal reports
- **JSON exports** for integration with other tools
- **Markdown exports** for wiki/documentation

### 6. Troubleshooting
- **Check `:status`** for current configuration
- **Use `:log full`** to review all commands
- **Recordings** can help recreate issues
- **Search function** to find specific errors

---

## File Structure

```
redterm/
├── redterm.py                    # Main script
├── redterm_logs.db               # SQLite database
│
├── recordings/                   # Terminal recordings
│   ├── default/                  # Default engagement
│   │   ├── recording_20250108_143022.json
│   │   └── recording_20250108_143022.cast
│   └── client_pentest/          # Custom engagement
│       └── recording_20250108_154510.json
│
├── screenshots/                  # Screenshot captures
│   ├── default/
│   │   └── screenshot_20250108_143022.png
│   └── client_pentest/
│       └── screenshot_20250108_154510.png
│
└── reports/                     # Generated reports
    ├── default_report.md
    ├── default_report.json
    ├── default_report.pdf
    ├── default_dashboard.html
    ├── client_pentest_report.md
    └── client_pentest_dashboard.html
```

### Database Schema
```sql
-- Command logs table
command_logs (
    id INTEGER PRIMARY KEY,
    engagement TEXT,
    command TEXT,
    output TEXT,
    sanitized_output TEXT,
    execution_time REAL,
    timestamp TEXT,
    tags TEXT,
    status TEXT,
    working_directory TEXT
)

-- Screenshots table
screenshots (
    id INTEGER PRIMARY KEY,
    engagement TEXT,
    command_id INTEGER,
    filepath TEXT,
    timestamp TEXT
)

-- Recordings table
recordings (
    id INTEGER PRIMARY KEY,
    engagement TEXT,
    filepath TEXT,
    duration REAL,
    timestamp TEXT
)
```

---

## Troubleshooting

### Common Issues

#### Recording Not Working
```bash
# Check if dependencies are installed
pip install asciinema

# Verify recording status
:status
```

#### Screenshots Failing
```bash
# Install required packages
pip install pyautogui pillow

# Test with manual screenshot
:screenshot
```

#### PDF Export Errors
```bash
# Install reportlab
pip install reportlab

# Try markdown export as alternative
:export markdown
```

#### Command Timeouts
```bash
# Long-running commands have extended timeouts
# nmap-full: 1 hour
# gobuster: 30 minutes
# Adjust in code if needed
```

---

## Conclusion

The Enhanced RedTeam Terminal v2.2 provides a comprehensive solution for penetration testers to:
- Organize multiple engagements
- Record terminal sessions
- Automatically log all commands
- Generate professional reports
- Maintain visual documentation
- Search through historical data

This tool significantly improves workflow efficiency and documentation quality for security assessments.

For updates and contributions, visit the project repository.
