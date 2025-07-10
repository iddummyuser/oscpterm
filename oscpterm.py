#!/usr/bin/env python3
import subprocess
import sqlite3
import re
import time
import json
import base64
import hashlib
from datetime import datetime
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.completion import WordCompleter, Completer, Completion
from prompt_toolkit.shortcuts import confirm
from prompt_toolkit.formatted_text import HTML
import os
import shutil
from pathlib import Path
import pty
import select
import termios
import tty
import sys
import threading
from collections import defaultdict
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from rich.console import Console
    from rich.theme import Theme
    from rich.syntax import Syntax
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import track
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("⚠️ Rich not available - install with: pip install rich")

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Preformatted, PageBreak
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠️ ReportLab not available - install with: pip install reportlab")

try:
    import pyautogui
    from PIL import Image, ImageDraw, ImageFont
    SCREENSHOT_AVAILABLE = True
except ImportError:
    SCREENSHOT_AVAILABLE = False
    print("⚠️ Screenshot tools not available - install with: pip install pyautogui pillow")

try:
    import asciinema.asciicast as asciicast
    from asciinema.asciicast.v2 import Writer
    ASCIINEMA_AVAILABLE = True
except ImportError:
    ASCIINEMA_AVAILABLE = False
    print("⚠️ Asciinema not available - install with: pip install asciinema")

try:
    from PIL import Image, ImageDraw, ImageFont
    import imageio
    GIF_AVAILABLE = True
except ImportError:
    GIF_AVAILABLE = False
    print("⚠️ GIF export not available - install with: pip install imageio[ffmpeg]")

DB_PATH = "redterm_logs.db"
ENGAGEMENT = "default"
history = InMemoryHistory()

# Terminal recording variables
RECORDING = False
RECORDING_START_TIME = None
RECORDING_DATA = []
RECORDINGS_DIR = "recordings"

# Working directory tracking
CURRENT_WORKING_DIR = os.getcwd()

# Extracted highlights storage
HIGHLIGHTS = defaultdict(set)

# Command timeouts (in seconds)
COMMAND_TIMEOUTS = {
    'default': 60,
    'nmap': 7200,  # 2 hours for nmap scans
    'gobuster': 3600,  # 1 hour for directory enumeration
    'nikto': 3600,
    'hydra': 3600,
    'enum4linux': 1800,
    'dirb': 1800,
    'dirbuster': 1800,
    'sqlmap': 7200,
    'masscan': 3600
}

# Auto-extraction patterns
EXTRACTION_PATTERNS = {
    'ip_addresses': {
        'pattern': r'\b(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\b',
        'category': 'IPs'
    },
    'ipv6_addresses': {
        'pattern': r'(?:[0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}',
        'category': 'IPv6'
    },
    'mac_addresses': {
        'pattern': r'(?:[0-9A-Fa-f]{2}[:-]){5}(?:[0-9A-Fa-f]{2})',
        'category': 'MACs'
    },
    'urls': {
        'pattern': r'https?://[^\s<>"{}|\\^`\[\]]+',
        'category': 'URLs'
    },
    'emails': {
        'pattern': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        'category': 'Emails'
    },
    'usernames': {
        'pattern': r'(?:user(?:name)?|login|uname)[\s:=]+([a-zA-Z0-9._-]+)',
        'category': 'Usernames'
    },
    'passwords': {
        'pattern': r'(?:pass(?:word)?|passwd|pwd)[\s:=]+([^\s]+)',
        'category': 'Passwords'
    },
    'hashes': {
        'pattern': r'\b[a-fA-F0-9]{32,128}\b',
        'category': 'Hashes'
    },
    'ports': {
        'pattern': r'(?:port|Port)\s+(\d{1,5})(?:/tcp|/udp)?(?:\s+open)?',
        'category': 'Ports'
    },
    'services': {
        'pattern': r'(\d{1,5})/(?:tcp|udp)\s+open\s+(\S+)',
        'category': 'Services'
    },
    'domains': {
        'pattern': r'\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\b',
        'category': 'Domains'
    },
    'api_keys': {
        'pattern': r'(?:api[_-]?key|apikey|access[_-]?token)[\s:=]+([a-zA-Z0-9-_]{20,})',
        'category': 'API_Keys'
    },
    'private_keys': {
        'pattern': r'-----BEGIN (?:RSA |DSA |EC )?PRIVATE KEY-----',
        'category': 'Private_Keys'
    }
}

# Interactive command patterns
INTERACTIVE_COMMANDS = [
    'ssh', 'ftp', 'telnet', 'mysql', 'psql', 'sqlmap',
    'msfconsole', 'gdb', 'vim', 'nano', 'less', 'more',
    'python', 'python3', 'ruby', 'perl', 'bash', 'sh',
    'nc -', 'ncat', 'socat'
]

# ─────────────── THEME & STYLING CONFIGURATION ───────────────
THEMES = {
    'default': {
        'primary': '#00ff00',
        'secondary': '#ffff00', 
        'error': '#ff0000',
        'success': '#00ff00',
        'info': '#00ffff',
        'warning': '#ff8800'
    },
    'matrix': {
        'primary': '#00ff41',
        'secondary': '#008f39',
        'error': '#ff0000',
        'success': '#00ff41',
        'info': '#00ff41',
        'warning': '#ffff00'
    },
    'stealth': {
        'primary': '#333333',
        'secondary': '#666666',
        'error': '#cc0000',
        'success': '#00cc00',
        'info': '#0099cc',
        'warning': '#cc6600'
    },
    'neon': {
        'primary': '#ff00ff',
        'secondary': '#00ffff',
        'error': '#ff3366',
        'success': '#33ff66',
        'info': '#3366ff',
        'warning': '#ffff33'
    }
}

CURRENT_THEME = 'default'
AUTO_SCREENSHOT = False
SCREENSHOT_DIR = "screenshots"

# Rich console setup
if RICH_AVAILABLE:
    console = Console(theme=Theme(THEMES[CURRENT_THEME]))
else:
    console = None

# ─────────────── CONFIGURATION ───────────────
ALIASES = {
    # Nmap aliases - progressive scanning approach
    'nmap-ping': 'nmap -sn {}',                                      # Host discovery only
    'nmap-quick': 'nmap -sS --top-ports 100 -T4 --open {}',        # Top 100 ports, fast
    'nmap-common': 'nmap -sS --top-ports 1000 -sV -T4 --open {}',  # Top 1000 ports with versions
    'nmap-full': 'nmap -sS -sV -sC -O --top-ports 5000 {}',        # Top 5000 with scripts
    'nmap-aggressive': 'nmap -sS -sV -sC -O -A -p- -T4 {}',        # All ports, aggressive
    'nmap-stealth': 'nmap -sS -Pn -T2 --top-ports 1000 {}',        # Stealthy scan
    'nmap-udp': 'nmap -sU --top-ports 100 -T4 {}',                 # Top 100 UDP ports
    'nmap-vulns': 'nmap -sV --script vuln {}',                     # Vulnerability scripts
    'nmap-smb': 'nmap -p445,139 --script smb-enum* {}',            # SMB enumeration
    'nmap-web': 'nmap -p80,443,8080,8443 -sV --script http-enum {}', # Web enumeration
    
    # Directory enumeration
    'gobuster-common': 'gobuster dir -u {} -w /usr/share/wordlists/dirb/common.txt -t 30',
    'gobuster-big': 'gobuster dir -u {} -w /usr/share/wordlists/dirb/big.txt -t 50',
    'gobuster-files': 'gobuster dir -u {} -w /usr/share/wordlists/dirb/common.txt -x php,asp,aspx,jsp,html,js -t 30',
    
    # Other tools
    'nikto-scan': 'nikto -h {}',
    'nc-listen': 'nc -lvnp {}',
    'nc-connect': 'nc {} {}',
    'enum4linux': 'enum4linux -a {}',
    'smbclient-list': 'smbclient -L {} -N',
    'dirbuster': 'dirb {} /usr/share/wordlists/dirb/common.txt',
    'whatweb': 'whatweb {}',
    'searchsploit': 'searchsploit {}',
    'msfconsole': 'msfconsole -q',
    'burp-proxy': 'java -jar /opt/burpsuite/burpsuite_community.jar',
    'hydra-ssh': 'hydra -l {} -P {} ssh://{}',
    'sqlmap-test': 'sqlmap -u {} --batch --banner',
    'masscan-quick': 'masscan -p1-65535 {} --rate=1000'
}

DANGEROUS_COMMANDS = [
    'rm -rf /',
    'dd if=',
    'mkfs',
    'format',
    'fdisk',
    'parted',
    'wipefs',
    '> /dev/sd',
    'shutdown',
    'reboot',
    'halt'
]

SENSITIVE_PATTERNS = [
    r'password[:\s=]*[\'"]?([^\s\'"]+)',
    r'token[:\s=]*[\'"]?([^\s\'"]+)',
    r'api[_-]?key[:\s=]*[\'"]?([^\s\'"]+)',
    r'secret[:\s=]*[\'"]?([^\s\'"]+)',
    r'auth[:\s=]*[\'"]?([^\s\'"]+)',
    r'\b[A-Za-z0-9+/]{20,}={0,2}\b',  # base64 patterns
    r'[a-fA-F0-9]{32,}',  # hex hashes
    r'ssh-rsa\s+[A-Za-z0-9+/]+',  # SSH keys
    r'-----BEGIN [A-Z ]+-----.*?-----END [A-Z ]+-----'  # PEM certificates/keys
]

# ─────────────── CUSTOM COMPLETER ───────────────
class RedTermCompleter(Completer):
    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        
        # Command completion
        if text.startswith(':'):
            commands = [':engage', ':log', ':clear', ':status', ':exit', ':help', ':alias', 
                       ':search', ':tag', ':export', ':screenshot', ':theme', ':dashboard', 
                       ':record', ':highlights', ':extract']
            for cmd in commands:
                if cmd.startswith(text):
                    yield Completion(cmd[len(text):])
        
        # Record subcommands
        elif text.startswith(':record '):
            subcommands = ['start', 'stop', 'list', 'play', 'export']
            for sub in subcommands:
                if sub.startswith(text.split()[-1]):
                    yield Completion(sub[len(text.split()[-1]):])
        
        # Alias completion
        elif any(text.startswith(alias) for alias in ALIASES.keys()):
            for alias in ALIASES.keys():
                if alias.startswith(text.split()[0]):
                    yield Completion(alias)
        
        # Engagement completion
        elif text.startswith(':engage '):
            engagements = self.get_engagements()
            for eng in engagements:
                if eng.startswith(text.split()[-1]):
                    yield Completion(eng[len(text.split()[-1]):])
    
    def get_engagements(self):
        try:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("SELECT DISTINCT engagement FROM command_logs")
            engagements = [row[0] for row in c.fetchall()]
            conn.close()
            return engagements
        except:
            return []

session = PromptSession(history=history, completer=RedTermCompleter())
last_output = ""

# ─────────────── STYLING & OUTPUT FUNCTIONS ───────────────
def print_styled(text, style='primary', panel=False):
    """Print styled text using Rich if available"""
    if RICH_AVAILABLE and console:
        if panel:
            console.print(Panel(text, style=style))
        else:
            console.print(text, style=style)
    else:
        # Fallback to plain text
        print(text)

def print_success(text):
    print_styled(f"✅ {text}", 'success')

def print_error(text):
    print_styled(f"❌ {text}", 'error')

def print_info(text):
    print_styled(f"ℹ️ {text}", 'info')

def print_warning(text):
    print_styled(f"⚠️ {text}", 'warning')

def create_status_table():
    """Create a styled status table"""
    if not RICH_AVAILABLE:
        return None
    
    table = Table(title="RedTeam Terminal Status")
    table.add_column("Property", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")
    
    return table

# ─────────────── AUTO-EXTRACTION FUNCTIONS ───────────────
def extract_highlights(text):
    """Extract interesting data from command output"""
    for name, config in EXTRACTION_PATTERNS.items():
        pattern = config['pattern']
        category = config['category']
        
        # Special handling for sensitive data
        if name in ['passwords', 'api_keys', 'private_keys']:
            # Skip extraction if it's a known false positive
            if any(fp in text.lower() for fp in ['password:', 'enter password', 'new password']):
                continue
        
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        
        if matches:
            if isinstance(matches[0], tuple):
                # For patterns with groups
                for match in matches:
                    if name == 'services':
                        # Special handling for services (port, service_name)
                        port, service = match
                        HIGHLIGHTS[category].add(f"{port}:{service}")
                    else:
                        HIGHLIGHTS[category].add(match[0])
            else:
                # For simple patterns
                for match in matches:
                    # Filter out common false positives
                    if category == 'IPs' and match in ['127.0.0.1', '0.0.0.0']:
                        continue
                    if category == 'Domains' and len(match) < 4:
                        continue
                    HIGHLIGHTS[category].add(match)

def show_highlights():
    """Display extracted highlights"""
    if not HIGHLIGHTS:
        print_info("No highlights extracted yet")
        return
    
    if RICH_AVAILABLE:
        for category, items in sorted(HIGHLIGHTS.items()):
            if items:
                table = Table(title=f"🎯 {category}")
                table.add_column("Value", style="cyan")
                for item in sorted(items):
                    table.add_row(item)
                console.print(table)
    else:
        print("\n🎯 Extracted Highlights:")
        for category, items in sorted(HIGHLIGHTS.items()):
            if items:
                print(f"\n{category}:")
                for item in sorted(items):
                    print(f"  • {item}")

def save_highlights():
    """Save highlights to database"""
    if not HIGHLIGHTS:
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create highlights table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS highlights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            engagement TEXT,
            category TEXT,
            value TEXT,
            timestamp TEXT,
            UNIQUE(engagement, category, value)
        )
    ''')
    
    # Insert highlights
    timestamp = datetime.utcnow().isoformat()
    for category, items in HIGHLIGHTS.items():
        for item in items:
            try:
                c.execute(
                    "INSERT OR IGNORE INTO highlights (engagement, category, value, timestamp) VALUES (?, ?, ?, ?)",
                    (ENGAGEMENT, category, item, timestamp)
                )
            except:
                pass
    
    conn.commit()
    conn.close()

def load_highlights():
    """Load highlights from database"""
    global HIGHLIGHTS
    HIGHLIGHTS.clear()
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        c.execute(
            "SELECT category, value FROM highlights WHERE engagement=?",
            (ENGAGEMENT,)
        )
        for category, value in c.fetchall():
            HIGHLIGHTS[category].add(value)
    except:
        pass
    
    conn.close()

# ─────────────── PTY COMMAND EXECUTION ───────────────
def is_interactive_command(cmd):
    """Check if command requires interactive TTY"""
    cmd_lower = cmd.lower()
    return any(ic in cmd_lower for ic in INTERACTIVE_COMMANDS)

def run_command_pty(command):
    """Run command with PTY support for real-time output"""
    global last_output
    
    output_buffer = []
    start_time = time.time()
    
    # Save terminal settings
    old_tty = termios.tcgetattr(sys.stdin)
    
    try:
        # Create PTY
        master_fd, slave_fd = pty.openpty()
        
        # Fork process
        pid = os.fork()
        
        if pid == 0:  # Child process
            os.close(master_fd)
            os.setsid()
            os.dup2(slave_fd, 0)
            os.dup2(slave_fd, 1)
            os.dup2(slave_fd, 2)
            os.close(slave_fd)
            
            # Set working directory
            os.chdir(CURRENT_WORKING_DIR)
            
            # Execute command
            os.execvp('/bin/sh', ['/bin/sh', '-c', command])
        
        else:  # Parent process
            os.close(slave_fd)
            
            # Set stdin to raw mode for interactive commands
            if is_interactive_command(command):
                tty.setraw(sys.stdin.fileno())
            
            # Monitor output
            while True:
                try:
                    # Check if process is still running
                    pid_status, status = os.waitpid(pid, os.WNOHANG)
                    if pid_status != 0:
                        break
                    
                    # Check for available data
                    r, w, e = select.select([master_fd, sys.stdin], [], [], 0.1)
                    
                    if master_fd in r:
                        # Read from command output
                        data = os.read(master_fd, 1024)
                        if not data:
                            break
                        
                        # Decode and display
                        decoded = data.decode('utf-8', errors='replace')
                        sys.stdout.write(decoded)
                        sys.stdout.flush()
                        output_buffer.append(decoded)
                        
                        # Record if recording
                        if RECORDING:
                            record_event('output', decoded)
                        
                        # Extract highlights in real-time
                        extract_highlights(decoded)
                    
                    if sys.stdin in r and is_interactive_command(command):
                        # Forward user input to command
                        data = os.read(sys.stdin.fileno(), 1024)
                        os.write(master_fd, data)
                        
                        # Record input if recording
                        if RECORDING:
                            try:
                                decoded_input = data.decode('utf-8', errors='replace')
                                record_event('input', decoded_input)
                            except:
                                pass
                
                except (OSError, IOError):
                    break
            
            # Get final exit status
            if pid_status == 0:
                _, status = os.waitpid(pid, 0)
            
            os.close(master_fd)
            
            # Check exit status
            execution_time = time.time() - start_time
            last_output = ''.join(output_buffer)
            
            if os.WIFEXITED(status):
                exit_code = os.WEXITSTATUS(status)
                return exit_code == 0, execution_time
            else:
                return False, execution_time
    
    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_tty)

# ─────────────── SCREENSHOT FUNCTIONS ───────────────
def ensure_screenshot_dir():
    """Ensure screenshot directory exists"""
    Path(SCREENSHOT_DIR).mkdir(exist_ok=True)
    engagement_dir = Path(SCREENSHOT_DIR) / ENGAGEMENT
    engagement_dir.mkdir(exist_ok=True)
    return engagement_dir

def take_screenshot(command_id=None, description=""):
    """Take a screenshot of the current terminal"""
    if not SCREENSHOT_AVAILABLE:
        print_warning("Screenshot functionality not available")
        return None
    
    try:
        screenshot_dir = ensure_screenshot_dir()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = screenshot_dir / filename
        
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        
        # Add metadata overlay
        img = Image.open(filepath)
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fallback to default
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        # Add metadata text
        metadata = f"Engagement: {ENGAGEMENT} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        if description:
            metadata += f" | {description}"
        
        # Add semi-transparent background for text
        text_bbox = draw.textbbox((0, 0), metadata, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        overlay = Image.new('RGBA', (text_width + 20, text_height + 10), (0, 0, 0, 128))
        img.paste(overlay, (10, 10), overlay)
        
        # Draw text
        draw.text((20, 15), metadata, fill=(255, 255, 255, 255), font=font)
        img.save(filepath)
        
        # Log to database
        if command_id:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("INSERT INTO screenshots (engagement, command_id, filepath, timestamp) VALUES (?, ?, ?, ?)",
                      (ENGAGEMENT, command_id, str(filepath), datetime.utcnow().isoformat()))
            conn.commit()
            conn.close()
        
        print_success(f"Screenshot saved: {filepath}")
        return str(filepath)
        
    except Exception as e:
        print_error(f"Screenshot failed: {e}")
        return None

def auto_screenshot_if_enabled(command_id):
    """Take automatic screenshot if enabled"""
    if AUTO_SCREENSHOT and command_id:
        take_screenshot(command_id, "Auto-capture after command")

# ─────────────── TERMINAL RECORDING FUNCTIONS ───────────────
def ensure_recordings_dir():
    """Ensure recordings directory exists"""
    Path(RECORDINGS_DIR).mkdir(exist_ok=True)
    engagement_dir = Path(RECORDINGS_DIR) / ENGAGEMENT
    engagement_dir.mkdir(exist_ok=True)
    return engagement_dir

def start_recording():
    """Start terminal recording"""
    global RECORDING, RECORDING_START_TIME, RECORDING_DATA
    
    if RECORDING:
        print_warning("Recording already in progress")
        return
    
    RECORDING = True
    RECORDING_START_TIME = time.time()
    RECORDING_DATA = []
    
    # Add initial recording entry
    RECORDING_DATA.append({
        'time': 0,
        'type': 'info',
        'data': f'Recording started for engagement: {ENGAGEMENT}'
    })
    
    print_success("🔴 Terminal recording started")
    print_info("Use :record stop to end recording")

def stop_recording():
    """Stop terminal recording and save"""
    global RECORDING, RECORDING_START_TIME, RECORDING_DATA
    
    if not RECORDING:
        print_warning("No recording in progress")
        return
    
    RECORDING = False
    duration = time.time() - RECORDING_START_TIME
    
    # Save recording
    recording_dir = ensure_recordings_dir()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save as custom JSON format
    json_file = recording_dir / f"recording_{timestamp}.json"
    recording_metadata = {
        'engagement': ENGAGEMENT,
        'start_time': RECORDING_START_TIME,
        'duration': duration,
        'events': RECORDING_DATA,
        'timestamp': datetime.utcnow().isoformat()
    }
    
    with open(json_file, 'w') as f:
        json.dump(recording_metadata, f, indent=2)
    
    # Save to database
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("INSERT INTO recordings (engagement, filepath, duration, timestamp) VALUES (?, ?, ?, ?)",
              (ENGAGEMENT, str(json_file), duration, datetime.utcnow().isoformat()))
    recording_id = c.lastrowid
    conn.commit()
    conn.close()
    
    print_success(f"🟢 Recording saved: {json_file}")
    print_info(f"Duration: {duration:.1f} seconds")
    
    # Export to asciinema if available
    if ASCIINEMA_AVAILABLE:
        try:
            asciinema_file = recording_dir / f"recording_{timestamp}.cast"
            export_to_asciinema(recording_metadata, asciinema_file)
            print_success(f"Asciinema export: {asciinema_file}")
        except Exception as e:
            print_warning(f"Asciinema export failed: {e}")
    
    return recording_id

def record_event(event_type, data):
    """Record an event during terminal recording"""
    global RECORDING_DATA, RECORDING_START_TIME
    
    if RECORDING and RECORDING_START_TIME:
        elapsed = time.time() - RECORDING_START_TIME
        RECORDING_DATA.append({
            'time': elapsed,
            'type': event_type,
            'data': data
        })

def export_to_asciinema(recording_metadata, output_file):
    """Export recording to asciinema format"""
    with open(output_file, 'w') as f:
        # Write header
        header = {
            "version": 2,
            "width": 80,
            "height": 24,
            "timestamp": int(recording_metadata['start_time']),
            "env": {"SHELL": "/bin/bash", "TERM": "xterm-256color"}
        }
        f.write(json.dumps(header) + '\n')
        
        # Write events
        for event in recording_metadata['events']:
            if event['type'] in ['input', 'output']:
                f.write(json.dumps([
                    event['time'],
                    'o' if event['type'] == 'output' else 'i',
                    event['data']
                ]) + '\n')

def list_recordings():
    """List all available recordings"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id, filepath, duration, timestamp FROM recordings WHERE engagement=? ORDER BY id DESC",
              (ENGAGEMENT,))
    recordings = c.fetchall()
    conn.close()
    
    if not recordings:
        print_info("No recordings found for this engagement")
        return
    
    if RICH_AVAILABLE:
        table = Table(title=f"Recordings for {ENGAGEMENT}")
        table.add_column("ID", style="cyan")
        table.add_column("Timestamp", style="yellow")
        table.add_column("Duration", style="green")
        table.add_column("File", style="magenta")
        
        for rec_id, filepath, duration, timestamp in recordings:
            table.add_row(
                str(rec_id),
                timestamp[:19],
                f"{duration:.1f}s",
                os.path.basename(filepath)
            )
        console.print(table)
    else:
        print(f"\n📼 Recordings for {ENGAGEMENT}:")
        for rec_id, filepath, duration, timestamp in recordings:
            print(f"  [{rec_id}] {timestamp[:19]} - {duration:.1f}s - {os.path.basename(filepath)}")

def playback_recording(recording_id):
    """Playback a terminal recording"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT filepath FROM recordings WHERE id=? AND engagement=?", (recording_id, ENGAGEMENT))
    result = c.fetchone()
    conn.close()
    
    if not result:
        print_error(f"Recording {recording_id} not found")
        return
    
    filepath = result[0]
    try:
        with open(filepath, 'r') as f:
            recording_data = json.load(f)
        
        print_info(f"Playing recording from {recording_data['timestamp'][:19]}")
        print_info(f"Duration: {recording_data['duration']:.1f}s")
        print_info("Press Ctrl+C to stop playback\n")
        
        start_time = time.time()
        
        for event in recording_data['events']:
            # Wait for the right time
            while (time.time() - start_time) < event['time']:
                time.sleep(0.01)
            
            if event['type'] == 'input':
                print(f"{ENGAGEMENT}> {event['data']}", end='')
            elif event['type'] == 'output':
                print(event['data'], end='')
            elif event['type'] == 'info':
                print_info(event['data'])
                
    except KeyboardInterrupt:
        print_info("\nPlayback stopped")
    except Exception as e:
        print_error(f"Playback failed: {e}")

def export_recording_to_gif(recording_id, output_file=None):
    """Export recording to animated GIF (requires additional setup)"""
    if not GIF_AVAILABLE:
        print_error("GIF export not available. Install with: pip install imageio[ffmpeg]")
        return
    
    # This is a placeholder - full implementation would require
    # terminal rendering to images and then combining into GIF
    print_info("GIF export feature coming soon...")

# ─────────────── HTML DASHBOARD GENERATION ───────────────
def create_html_dashboard():
    """Generate an HTML dashboard with charts and statistics"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Gather statistics
    c.execute("SELECT COUNT(*), AVG(execution_time), SUM(CASE WHEN status='success' THEN 1 ELSE 0 END), SUM(CASE WHEN status='error' THEN 1 ELSE 0 END) FROM command_logs WHERE engagement=?", (ENGAGEMENT,))
    total, avg_time, success_count, error_count = c.fetchone()
    success_rate = (success_count / total * 100) if total > 0 else 0
    
    # Command timeline
    c.execute("SELECT timestamp, command, execution_time, status FROM command_logs WHERE engagement=? ORDER BY id DESC LIMIT 20", (ENGAGEMENT,))
    recent_commands = c.fetchall()
    
    # Top commands
    c.execute("SELECT command, COUNT(*) as count FROM command_logs WHERE engagement=? GROUP BY command ORDER BY count DESC LIMIT 10", (ENGAGEMENT,))
    top_commands = c.fetchall()
    
    # Tag statistics
    c.execute("SELECT tags FROM command_logs WHERE engagement=? AND tags IS NOT NULL AND tags != ''", (ENGAGEMENT,))
    all_tags = []
    for (tags,) in c.fetchall():
        all_tags.extend(tags.split(','))
    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    # Get highlights summary
    highlights_summary = {}
    try:
        c.execute("SELECT category, COUNT(*) FROM highlights WHERE engagement=? GROUP BY category", (ENGAGEMENT,))
        highlights_summary = dict(c.fetchall())
    except:
        pass
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RedTeam Terminal Dashboard - {ENGAGEMENT}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #0a0a0a;
            color: #00ff00;
            padding: 20px;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        h1 {{
            color: #00ff00;
            text-align: center;
            margin-bottom: 30px;
            text-shadow: 0 0 10px #00ff00;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
        }}
        .stat-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #00ff00;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #888;
            font-size: 0.9em;
            text-transform: uppercase;
        }}
        .chart-container {{
            background: #1a1a1a;
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
        }}
        .command-list {{
            background: #1a1a1a;
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .command-item {{
            background: #0a0a0a;
            border-left: 3px solid #00ff00;
            padding: 10px 15px;
            margin-bottom: 10px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}
        .success {{ border-left-color: #00ff00; }}
        .error {{ border-left-color: #ff0000; }}
        .timestamp {{
            color: #888;
            font-size: 0.8em;
        }}
        .charts-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }}
        .highlights-section {{
            background: #1a1a1a;
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }}
        .highlight-item {{
            display: inline-block;
            background: #0a0a0a;
            border: 1px solid #00ff00;
            padding: 5px 10px;
            margin: 5px;
            border-radius: 5px;
            font-family: monospace;
        }}
        @media (max-width: 768px) {{
            .charts-row {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔴 RedTeam Terminal Dashboard - {ENGAGEMENT}</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Commands</div>
                <div class="stat-value">{total}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Success Rate</div>
                <div class="stat-value">{success_rate:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Execution Time</div>
                <div class="stat-value">{avg_time:.1f}s</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Failed Commands</div>
                <div class="stat-value" style="color: #ff0000;">{error_count}</div>
            </div>
        </div>
        
        <div class="highlights-section">
            <h3>🎯 Extracted Highlights</h3>
            {' '.join([f'<div class="highlight-item">{cat}: {count}</div>' for cat, count in highlights_summary.items()])}
        </div>
        
        <div class="charts-row">
            <div class="chart-container">
                <h3>Command Status Distribution</h3>
                <canvas id="statusChart"></canvas>
            </div>
            <div class="chart-container">
                <h3>Top Commands</h3>
                <canvas id="topCommandsChart"></canvas>
            </div>
        </div>
        
        <div class="command-list">
            <h3>Recent Commands</h3>
            {"".join([f'<div class="command-item {row[3]}"><div class="timestamp">{row[0][:19]} ({row[2]:.1f}s)</div>{row[1]}</div>' for row in recent_commands])}
        </div>
        
        <div class="chart-container">
            <h3>Command Tags</h3>
            <canvas id="tagsChart"></canvas>
        </div>
    </div>
    
    <script>
        // Status Chart
        const statusCtx = document.getElementById('statusChart').getContext('2d');
        new Chart(statusCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Success', 'Error'],
                datasets: [{{
                    data: [{success_count}, {error_count}],
                    backgroundColor: ['#00ff00', '#ff0000'],
                    borderColor: ['#00ff00', '#ff0000'],
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#00ff00'
                        }}
                    }}
                }}
            }}
        }});
        
        // Top Commands Chart
        const topCommandsCtx = document.getElementById('topCommandsChart').getContext('2d');
        new Chart(topCommandsCtx, {{
            type: 'bar',
            data: {{
                labels: {[cmd[0][:30] + "..." if len(cmd[0]) > 30 else cmd[0] for cmd in top_commands[:5]]},
                datasets: [{{
                    label: 'Executions',
                    data: {[cmd[1] for cmd in top_commands[:5]]},
                    backgroundColor: '#00ff00',
                    borderColor: '#00ff00',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    y: {{
                        beginAtZero: true,
                        grid: {{
                            color: '#333'
                        }},
                        ticks: {{
                            color: '#00ff00'
                        }}
                    }},
                    x: {{
                        grid: {{
                            color: '#333'
                        }},
                        ticks: {{
                            color: '#00ff00'
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        display: false
                    }}
                }}
            }}
        }});
        
        // Tags Chart
        const tagsCtx = document.getElementById('tagsChart').getContext('2d');
        new Chart(tagsCtx, {{
            type: 'radar',
            data: {{
                labels: {list(tag_counts.keys())},
                datasets: [{{
                    label: 'Tag Usage',
                    data: {list(tag_counts.values())},
                    backgroundColor: 'rgba(0, 255, 0, 0.2)',
                    borderColor: '#00ff00',
                    borderWidth: 2,
                    pointBackgroundColor: '#00ff00'
                }}]
            }},
            options: {{
                responsive: true,
                scales: {{
                    r: {{
                        beginAtZero: true,
                        grid: {{
                            color: '#333'
                        }},
                        pointLabels: {{
                            color: '#00ff00'
                        }},
                        ticks: {{
                            color: '#00ff00'
                        }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        labels: {{
                            color: '#00ff00'
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    
    filename = f"{ENGAGEMENT}_dashboard.html"
    with open(filename, 'w') as f:
        f.write(html_content)
    
    conn.close()
    print_success(f"HTML Dashboard generated: {filename}")
    return filename

# ─────────────── PDF EXPORT FUNCTIONS ───────────────
def create_pdf_report():
    """Generate a professional PDF report"""
    if not PDF_AVAILABLE:
        print_error("PDF generation not available. Install with: pip install reportlab")
        return
    
    try:
        filename = f"{ENGAGEMENT}_report.pdf"
        doc = SimpleDocTemplate(filename, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=HexColor('#2c3e50'),
            alignment=1,  # Center
            spaceAfter=30
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#34495e'),
            leftIndent=0,
            spaceAfter=12
        )
        
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Code'],
            fontSize=10,
            leftIndent=20,
            backgroundColor=HexColor('#f8f9fa'),
            borderColor=HexColor('#e9ecef'),
            borderWidth=1,
            borderPadding=5
        )
        
        story = []
        
        # Title page
        story.append(Paragraph(f"Red Team Assessment Report", title_style))
        story.append(Paragraph(f"Engagement: {ENGAGEMENT}", styles['Heading2']))
        story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        
        c.execute("SELECT COUNT(*), AVG(execution_time), SUM(CASE WHEN status='success' THEN 1 ELSE 0 END), SUM(CASE WHEN status='error' THEN 1 ELSE 0 END) FROM command_logs WHERE engagement=?", (ENGAGEMENT,))
        total, avg_time, success_count, error_count = c.fetchone()
        success_rate = (success_count / total * 100) if total > 0 else 0
        
        story.append(Paragraph("Executive Summary", heading_style))
        summary_text = f"""
        <para>
        Total Commands Executed: {total}<br/>
        Average Execution Time: {avg_time:.2f} seconds<br/>
        Success Rate: {success_rate:.1f}% ({success_count}/{total})<br/>
        Failed Commands: {error_count}<br/>
        </para>
        """
        story.append(Paragraph(summary_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Extracted Highlights
        if HIGHLIGHTS:
            story.append(Paragraph("Extracted Highlights", heading_style))
            for category, items in sorted(HIGHLIGHTS.items()):
                if items:
                    highlight_text = f"<b>{category}:</b> {', '.join(sorted(items)[:10])}"
                    if len(items) > 10:
                        highlight_text += f" ... and {len(items) - 10} more"
                    story.append(Paragraph(highlight_text, styles['Normal']))
            story.append(Spacer(1, 20))
        
        # Command Timeline
        story.append(Paragraph("Command Timeline", heading_style))
        c.execute("SELECT timestamp, command, sanitized_output, execution_time, tags, status FROM command_logs WHERE engagement=? ORDER BY id", (ENGAGEMENT,))
        
        for row in c.fetchall():
            timestamp, cmd, output, exec_time, tags, status = row
            status_icon = "✓" if status == 'success' else "✗"
            
            # Command header
            cmd_header = f"{status_icon} {timestamp[:19]} ({exec_time:.2f}s)"
            if tags:
                cmd_header += f" [Tags: {tags}]"
            story.append(Paragraph(cmd_header, styles['Heading3']))
            
            # Command
            story.append(Paragraph(f"Command:", styles['Normal']))
            story.append(Preformatted(f"$ {cmd}", code_style))
            
            # Output (truncated for PDF)
            if output.strip():
                story.append(Paragraph(f"Output:", styles['Normal']))
                truncated_output = output[:1000] + "..." if len(output) > 1000 else output
                story.append(Preformatted(truncated_output, code_style))
            
            story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        print_success(f"PDF report generated: {filename}")
        conn.close()
        
    except Exception as e:
        print_error(f"PDF generation failed: {e}")

# ─────────────── DATABASE SETUP ───────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS command_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            engagement TEXT,
            command TEXT,
            output TEXT,
            sanitized_output TEXT,
            execution_time REAL,
            timestamp TEXT,
            tags TEXT,
            status TEXT DEFAULT 'success',
            working_directory TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS engagement_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            engagement TEXT,
            note_type TEXT,
            content TEXT,
            timestamp TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS screenshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            engagement TEXT,
            command_id INTEGER,
            filepath TEXT,
            timestamp TEXT,
            FOREIGN KEY (command_id) REFERENCES command_logs (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS recordings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            engagement TEXT,
            filepath TEXT,
            duration REAL,
            timestamp TEXT
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS highlights (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            engagement TEXT,
            category TEXT,
            value TEXT,
            timestamp TEXT,
            UNIQUE(engagement, category, value)
        )
    ''')
    
    # Add working_directory column if it doesn't exist
    c.execute("PRAGMA table_info(command_logs)")
    columns = [col[1] for col in c.fetchall()]
    if 'working_directory' not in columns:
        c.execute("ALTER TABLE command_logs ADD COLUMN working_directory TEXT")
    
    conn.commit()
    conn.close()

def sanitize_output(output, command):
    """Remove sensitive information from command output"""
    sanitized = output
    for pattern in SENSITIVE_PATTERNS:
        sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE | re.DOTALL)
    return sanitized

def log_command(cmd, output, execution_time, status='success', tags=None):
    sanitized = sanitize_output(output, cmd)
    tag_str = ','.join(tags) if tags else ''
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO command_logs 
                 (engagement, command, output, sanitized_output, execution_time, timestamp, tags, status, working_directory) 
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (ENGAGEMENT, cmd, output, sanitized, execution_time, datetime.utcnow().isoformat(), tag_str, status, CURRENT_WORKING_DIR))
    command_id = c.lastrowid
    conn.commit()
    conn.close()
    return command_id

# ─────────────── VALIDATION & SECURITY ───────────────
def validate_command(cmd):
    """Validate command for safety"""
    cmd_lower = cmd.lower()
    
    # Check for dangerous commands
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in cmd_lower:
            return False, f"⚠️ Potentially dangerous command detected: {dangerous}"
    
    # Check for suspicious patterns
    if re.search(r'rm\s+.*-rf', cmd_lower):
        return False, "⚠️ Recursive delete detected - please be specific with paths"
    
    if re.search(r'>\s*/dev/sd[a-z]', cmd_lower):
        return False, "⚠️ Direct disk write detected"
    
    return True, ""

def expand_alias(command):
    """Expand command aliases"""
    parts = command.split()
    if parts[0] in ALIASES:
        alias_cmd = ALIASES[parts[0]]
        if '{}' in alias_cmd:
            if len(parts) > 1:
                return alias_cmd.format(*parts[1:])
            else:
                return f"❌ Alias '{parts[0]}' requires arguments: {alias_cmd}"
        else:
            return alias_cmd + ' ' + ' '.join(parts[1:]) if len(parts) > 1 else alias_cmd
    return command

def get_command_timeout(command):
    """Get appropriate timeout for a command"""
    cmd_lower = command.lower()
    for cmd_type, timeout in COMMAND_TIMEOUTS.items():
        if cmd_type in cmd_lower:
            return timeout
    return COMMAND_TIMEOUTS['default']

# ─────────────── ENHANCED LOGGING FUNCTIONS ───────────────
def show_logs(limit=5, show_sanitized=True):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    output_field = 'sanitized_output' if show_sanitized else 'output'
    c.execute(f"""SELECT timestamp, command, {output_field}, execution_time, tags, status, working_directory 
                  FROM command_logs WHERE engagement=? ORDER BY id DESC LIMIT ?""",
              (ENGAGEMENT, limit))
    rows = c.fetchall()
    
    if RICH_AVAILABLE:
        table = Table(title=f"Last {limit} Commands for {ENGAGEMENT}")
        table.add_column("Time", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Command", style="yellow")
        table.add_column("Duration", style="green")
        table.add_column("Dir", style="blue")
        table.add_column("Tags", style="magenta")
        
        for t, cmd, out, exec_time, tags, status, cwd in rows:
            status_icon = "✅" if status == 'success' else "❌" if status == 'error' else "⏰"
            dir_short = os.path.basename(cwd) if cwd else "~"
            table.add_row(
                t[:19],
                status_icon,
                cmd[:50] + "..." if len(cmd) > 50 else cmd,
                f"{exec_time:.2f}s",
                dir_short,
                tags if tags else ""
            )
        console.print(table)
        
        # Show output details
        for i, (t, cmd, out, exec_time, tags, status, cwd) in enumerate(rows):
            if i < 3:  # Show details for last 3 commands
                console.print(Panel(
                    f"[bold]{cmd}[/bold]\n{out[:300]}{'...' if len(out) > 300 else ''}",
                    title=f"Output - {t[:19]}",
                    style="dim"
                ))
    else:
        print(f"\n📄 Last {limit} Commands for `{ENGAGEMENT}`:")
        for t, cmd, out, exec_time, tags, status, cwd in rows:
            status_icon = "✅" if status == 'success' else "❌"
            tag_display = f" 🏷️[{tags}]" if tags else ""
            dir_display = f" 📁[{os.path.basename(cwd)}]" if cwd else ""
            print(f"\n[🕒 {t}] {status_icon} {exec_time:.2f}s{dir_display}{tag_display}")
            print(f"➤ {cmd}")
            print(f"{out.strip()[:500]}{'...' if len(out) > 500 else ''}")
    conn.close()

def search_logs(query, search_type='all'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if search_type == 'command':
        c.execute("SELECT timestamp, command, sanitized_output, tags FROM command_logs WHERE engagement=? AND command LIKE ? ORDER BY id DESC",
                  (ENGAGEMENT, f"%{query}%"))
    elif search_type == 'output':
        c.execute("SELECT timestamp, command, sanitized_output, tags FROM command_logs WHERE engagement=? AND sanitized_output LIKE ? ORDER BY id DESC",
                  (ENGAGEMENT, f"%{query}%"))
    elif search_type == 'tags':
        c.execute("SELECT timestamp, command, sanitized_output, tags FROM command_logs WHERE engagement=? AND tags LIKE ? ORDER BY id DESC",
                  (ENGAGEMENT, f"%{query}%"))
    else:
        c.execute("SELECT timestamp, command, sanitized_output, tags FROM command_logs WHERE engagement=? AND (command LIKE ? OR sanitized_output LIKE ? OR tags LIKE ?) ORDER BY id DESC",
                  (ENGAGEMENT, f"%{query}%", f"%{query}%", f"%{query}%"))
    
    rows = c.fetchall()
    print(f"\n🔍 Search Results for '{query}' in {search_type}:")
    for t, cmd, out, tags in rows:
        tag_display = f" 🏷️[{tags}]" if tags else ""
        print(f"\n[🕒 {t}]{tag_display}")
        print(f"➤ {cmd}")
        print(f"{out.strip()[:300]}{'...' if len(out) > 300 else ''}")
    conn.close()

def tag_last_command(tags):
    """Tag the most recent command"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM command_logs WHERE engagement=? ORDER BY id DESC LIMIT 1", (ENGAGEMENT,))
    row = c.fetchone()
    if row:
        tag_str = ','.join(tags)
        c.execute("UPDATE command_logs SET tags=? WHERE id=?", (tag_str, row[0]))
        conn.commit()
        print(f"🏷️ Tagged last command with: {tag_str}")
    else:
        print("❌ No commands to tag")
    conn.close()

def export_logs(format_type='markdown'):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    if format_type == 'markdown':
        filename = f"{ENGAGEMENT}_report.md"
        with open(filename, "w") as f:
            f.write(f"# Red Team Report: `{ENGAGEMENT}`\n\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n\n")
            f.write("## 📊 Executive Summary\n\n")
            
            # Command statistics
            c.execute("SELECT COUNT(*), AVG(execution_time) FROM command_logs WHERE engagement=?", (ENGAGEMENT,))
            count, avg_time = c.fetchone()
            f.write(f"- Total Commands: {count}\n")
            f.write(f"- Average Execution Time: {avg_time:.2f}s\n\n")
            
            # Tag summary
            c.execute("SELECT tags FROM command_logs WHERE engagement=? AND tags IS NOT NULL AND tags != ''", (ENGAGEMENT,))
            all_tags = []
            for (tags,) in c.fetchall():
                all_tags.extend(tags.split(','))
            tag_counts = {}
            for tag in all_tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
            
            if tag_counts:
                f.write("### 🏷️ Tag Summary\n")
                for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True):
                    f.write(f"- {tag}: {count}\n")
                f.write("\n")
            
            # Extracted highlights
            if HIGHLIGHTS:
                f.write("## 🎯 Extracted Highlights\n\n")
                for category, items in sorted(HIGHLIGHTS.items()):
                    if items:
                        f.write(f"### {category}\n")
                        for item in sorted(items):
                            f.write(f"- `{item}`\n")
                        f.write("\n")
            
            f.write("## 🔧 Command Logs\n\n")
            c.execute("SELECT timestamp, command, sanitized_output, execution_time, tags, status, working_directory FROM command_logs WHERE engagement=? ORDER BY id", (ENGAGEMENT,))
            for row in c.fetchall():
                timestamp, cmd, output, exec_time, tags, status, cwd = row
                status_icon = "✅" if status == 'success' else "❌"
                tag_display = f" 🏷️[{tags}]" if tags else ""
                cwd_display = f" 📁[{cwd}]" if cwd else ""
                f.write(f"### {status_icon} {timestamp} ({exec_time:.2f}s){cwd_display}{tag_display}\n")
                f.write(f"```bash\n$ {cmd}\n{output}\n```\n\n")
                
    elif format_type == 'json':
        filename = f"{ENGAGEMENT}_report.json"
        c.execute("SELECT * FROM command_logs WHERE engagement=? ORDER BY id", (ENGAGEMENT,))
        columns = [description[0] for description in c.description]
        data = []
        for row in c.fetchall():
            data.append(dict(zip(columns, row)))
        
        # Add highlights
        highlights_data = {}
        for category, items in HIGHLIGHTS.items():
            highlights_data[category] = list(items)
        
        with open(filename, "w") as f:
            json.dump({
                'engagement': ENGAGEMENT,
                'generated': datetime.utcnow().isoformat(),
                'highlights': highlights_data,
                'commands': data
            }, f, indent=2)
    
    conn.close()
    print(f"\n✅ Report exported to `{filename}`")

# ─────────────── COMMAND RUNNER ───────────────
def run_command(command):
    global last_output, CURRENT_WORKING_DIR
    
    # Record input if recording
    if RECORDING:
        record_event('input', command + '\n')
    
    # Handle cd command specially
    if command.startswith('cd '):
        try:
            new_dir = command[3:].strip()
            if new_dir == '~':
                new_dir = os.path.expanduser('~')
            elif not os.path.isabs(new_dir):
                new_dir = os.path.join(CURRENT_WORKING_DIR, new_dir)
            
            new_dir = os.path.abspath(new_dir)
            
            if os.path.isdir(new_dir):
                CURRENT_WORKING_DIR = new_dir
                os.chdir(CURRENT_WORKING_DIR)
                output_msg = f"Changed directory to: {CURRENT_WORKING_DIR}"
                print_success(output_msg)
                if RECORDING:
                    record_event('output', f"✅ {output_msg}\n")
                log_command(command, f"Changed to {CURRENT_WORKING_DIR}", 0.0, 'success')
            else:
                error_msg = f"Directory not found: {new_dir}"
                print_error(error_msg)
                if RECORDING:
                    record_event('output', f"❌ {error_msg}\n")
                log_command(command, error_msg, 0.0, 'error')
        except Exception as e:
            error_msg = f"Failed to change directory: {str(e)}"
            print_error(error_msg)
            if RECORDING:
                record_event('output', f"❌ {error_msg}\n")
            log_command(command, str(e), 0.0, 'error')
        return
    
    # Expand aliases
    expanded_cmd = expand_alias(command)
    if expanded_cmd.startswith("❌"):
        print_error(expanded_cmd[2:])
        if RECORDING:
            record_event('output', expanded_cmd + '\n')
        return
    
    # Validate command
    is_valid, error_msg = validate_command(expanded_cmd)
    if not is_valid:
        print_warning(error_msg[4:])  # Remove emoji prefix
        if RECORDING:
            record_event('output', error_msg + '\n')
        if not confirm("Continue anyway?"):
            return
    
    # Get appropriate timeout
    timeout = get_command_timeout(expanded_cmd)
    
    start_time = time.time()
    command_id = None
    
    # Print execution info
    info_msg = f"Executing: {expanded_cmd}"
    print_info(info_msg)
    if RECORDING:
        record_event('output', f"ℹ️ {info_msg}\n")
    
    if timeout != COMMAND_TIMEOUTS['default']:
        timeout_msg = f"Timeout set to: {timeout}s (long-running command detected)"
        print_info(timeout_msg)
        if RECORDING:
            record_event('output', f"ℹ️ {timeout_msg}\n")
    
    # Use PTY for better output handling
    try:
        success, execution_time = run_command_pty(expanded_cmd)
        
        # Extract highlights from output
        extract_highlights(last_output)
        
        # Save highlights
        save_highlights()
        
        # Log command
        status = 'success' if success else 'error'
        command_id = log_command(expanded_cmd, last_output, execution_time, status)
        
        if success:
            success_msg = f"Completed in {execution_time:.2f}s"
            print_success(success_msg)
            if RECORDING:
                record_event('output', f"✅ {success_msg}\n")
        else:
            error_msg = f"Failed in {execution_time:.2f}s"
            print_error(error_msg)
            if RECORDING:
                record_event('output', f"❌ {error_msg}\n")
        
        # Auto-screenshot if enabled
        auto_screenshot_if_enabled(command_id)
        
    except Exception as e:
        execution_time = time.time() - start_time
        last_output = str(e)
        print_error(last_output)
        if RECORDING:
            record_event('output', f"❌ {last_output}\n")
        command_id = log_command(expanded_cmd, last_output, execution_time, 'error')
    
    return command_id

# ─────────────── ENGAGEMENT MANAGEMENT ───────────────
def list_engagements():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""SELECT engagement, COUNT(*) as cmd_count, MAX(timestamp) as last_activity 
                 FROM command_logs GROUP BY engagement ORDER BY last_activity DESC""")
    engagements = c.fetchall()
    print("\n📁 Existing Engagements:")
    for eng, count, last_activity in engagements:
        indicator = "🔴" if eng == ENGAGEMENT else "⚫"
        print(f" {indicator} {eng} ({count} commands, last: {last_activity[:19]})")
    conn.close()

def show_status():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT command, timestamp, execution_time FROM command_logs WHERE engagement=? ORDER BY id DESC LIMIT 1", (ENGAGEMENT,))
    row = c.fetchone()
    
    # Count highlights
    highlight_count = sum(len(items) for items in HIGHLIGHTS.values())
    
    if RICH_AVAILABLE:
        table = create_status_table()
        table.add_row("Current Engagement", ENGAGEMENT)
        table.add_row("Current Directory", CURRENT_WORKING_DIR)
        table.add_row("Theme", CURRENT_THEME)
        table.add_row("Auto-Screenshot", "Enabled" if AUTO_SCREENSHOT else "Disabled")
        table.add_row("Recording", "🔴 ACTIVE" if RECORDING else "⚫ Inactive")
        table.add_row("Extracted Highlights", str(highlight_count))
        
        if row:
            table.add_row("Last Command", row[0][:50] + "..." if len(row[0]) > 50 else row[0])
            table.add_row("Last Execution", f"{row[1][:19]} ({row[2]:.2f}s)")
            
            # Show stats
            c.execute("SELECT COUNT(*), AVG(execution_time), SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) FROM command_logs WHERE engagement=?", (ENGAGEMENT,))
            total, avg_time, success_count = c.fetchone()
            success_rate = (success_count / total * 100) if total > 0 else 0
            table.add_row("Total Commands", str(total))
            table.add_row("Average Time", f"{avg_time:.2f}s")
            table.add_row("Success Rate", f"{success_rate:.1f}%")
        else:
            table.add_row("Status", "No commands run yet")
        
        console.print(table)
    else:
        print(f"\n📌 Current Engagement: `{ENGAGEMENT}`")
        print(f"📁 Current Directory: {CURRENT_WORKING_DIR}")
        print(f"🎨 Theme: {CURRENT_THEME}")
        print(f"📷 Auto-Screenshot: {'Enabled' if AUTO_SCREENSHOT else 'Disabled'}")
        print(f"📼 Recording: {'🔴 ACTIVE' if RECORDING else '⚫ Inactive'}")
        print(f"🎯 Extracted Highlights: {highlight_count}")
        
        if row:
            print(f"🕒 Last Command @ {row[1][:19]}: `{row[0]}` ({row[2]:.2f}s)")
            
            # Show some stats
            c.execute("SELECT COUNT(*), AVG(execution_time), SUM(CASE WHEN status='success' THEN 1 ELSE 0 END) FROM command_logs WHERE engagement=?", (ENGAGEMENT,))
            total, avg_time, success_count = c.fetchone()
            success_rate = (success_count / total * 100) if total > 0 else 0
            print(f"📊 Stats: {total} commands, {avg_time:.2f}s avg, {success_rate:.1f}% success rate")
        else:
            print("🕒 No commands run yet.")
    conn.close()

def set_theme(theme_name):
    """Set the color theme"""
    global CURRENT_THEME, console
    if theme_name in THEMES:
        CURRENT_THEME = theme_name
        if RICH_AVAILABLE:
            console = Console(theme=Theme(THEMES[CURRENT_THEME]))
        print_success(f"Theme set to: {theme_name}")
    else:
        print_error(f"Unknown theme: {theme_name}")
        print_info(f"Available themes: {', '.join(THEMES.keys())}")

def toggle_auto_screenshot():
    """Toggle automatic screenshot capture"""
    global AUTO_SCREENSHOT
    AUTO_SCREENSHOT = not AUTO_SCREENSHOT
    status = "enabled" if AUTO_SCREENSHOT else "disabled"
    print_success(f"Auto-screenshot {status}")

def show_themes():
    """Display available themes with preview"""
    if RICH_AVAILABLE:
        print_info("Available Themes:")
        for theme_name, colors in THEMES.items():
            indicator = "●" if theme_name == CURRENT_THEME else "○"
            console.print(f"{indicator} [bold]{theme_name}[/bold]", style=colors['primary'])
            console.print(f"   Primary: {colors['primary']} | Success: {colors['success']} | Error: {colors['error']}")
    else:
        print("\n🎨 Available Themes:")
        for theme_name in THEMES.keys():
            indicator = "●" if theme_name == CURRENT_THEME else "○"
            print(f"  {indicator} {theme_name}")

def manual_screenshot():
    """Take a manual screenshot"""
    description = input("Screenshot description (optional): ").strip()
    filepath = take_screenshot(description=description or "Manual screenshot")
    if filepath:
        print_success(f"Screenshot saved: {filepath}")

def show_aliases():
    print("\n🔧 Available Aliases:")
    for alias, command in ALIASES.items():
        print(f"  {alias:<20} → {command}")

# ─────────────── MAIN LOOP ───────────────
def main():
    global ENGAGEMENT, AUTO_SCREENSHOT, CURRENT_THEME, CURRENT_WORKING_DIR
    
    # Create necessary directories
    ensure_screenshot_dir()
    ensure_recordings_dir()
    
    # Startup banner
    if RICH_AVAILABLE:
        startup_text = """
[bold red]🔴 Enhanced RedTeam Terminal v2.3[/bold red]
[cyan]Features:[/cyan] TTY Support • Auto-Extraction • Real-time Output • Interactive Commands
[dim]Type :help for commands | :record start to begin recording[/dim]
        """
        console.print(Panel(startup_text, style="bold"))
    else:
        print("🔴 Enhanced RedTeam Terminal v2.3 | OSCP-Compatible")
        print("Features: TTY Support • Auto-Extraction • Real-time Output")
        print("Type :help for available commands\n")
    
    init_db()
    load_highlights()
    
    while True:
        try:
            # Show current directory in prompt with recording indicator
            prompt_dir = os.path.basename(CURRENT_WORKING_DIR) if CURRENT_WORKING_DIR != os.path.expanduser('~') else '~'
            recording_indicator = "🔴 " if RECORDING else ""
            user_input = session.prompt(f'{recording_indicator}{ENGAGEMENT}:{prompt_dir}> ')
            if user_input.strip() == "":
                continue
                
            # Handle internal commands
            if user_input.startswith(":engage"):
                tokens = user_input.split()
                if len(tokens) >= 2:
                    if tokens[1] == "list":
                        list_engagements()
                    elif tokens[1] == "switch" and len(tokens) == 3:
                        ENGAGEMENT = tokens[2].strip()
                        load_highlights()  # Load highlights for new engagement
                        print_success(f"Switched to engagement: {ENGAGEMENT}")
                    else:
                        ENGAGEMENT = tokens[1].strip()
                        load_highlights()  # Load highlights for new engagement
                        print_success(f"Engagement set to: {ENGAGEMENT}")
                else:
                    print_error("Usage: :engage <n> | :engage switch <n> | :engage list")
                    
            elif user_input == ":highlights":
                show_highlights()
            
            elif user_input.startswith(":extract"):
                parts = user_input.split(None, 1)
                if len(parts) == 2:
                    extract_highlights(parts[1])
                    print_success("Extraction complete")
                else:
                    print_error("Usage: :extract <text>")
                    
            elif user_input.startswith(":record"):
                parts = user_input.split()
                if len(parts) == 1:
                    print_info(f"Recording status: {'🔴 ACTIVE' if RECORDING else '⚫ Inactive'}")
                    print_info("Usage: :record start | :record stop | :record list | :record play <id>")
                elif parts[1] == "start":
                    start_recording()
                elif parts[1] == "stop":
                    stop_recording()
                elif parts[1] == "list":
                    list_recordings()
                elif parts[1] == "play" and len(parts) == 3:
                    if parts[2].isdigit():
                        playback_recording(int(parts[2]))
                    else:
                        print_error("Recording ID must be a number")
                elif parts[1] == "export" and len(parts) >= 3:
                    if parts[2].isdigit():
                        if len(parts) == 4 and parts[3] == "gif":
                            export_recording_to_gif(int(parts[2]))
                        else:
                            print_info("Export format: gif (more formats coming soon)")
                    else:
                        print_error("Recording ID must be a number")
                else:
                    print_error("Unknown record command. Use: start, stop, list, play <id>, export <id> <format>")
                    
            elif user_input == ":log":
                show_logs()
            elif user_input.startswith(":log "):
                parts = user_input.split()
                if len(parts) == 2 and parts[1].isdigit():
                    show_logs(int(parts[1]))
                elif parts[1] == "full":
                    show_logs(1000)
                elif parts[1] == "raw":
                    show_logs(5, show_sanitized=False)
                else:
                    print_error("Usage: :log [number] | :log full | :log raw")
                    
            elif user_input.startswith(":search "):
                parts = user_input.split(None, 2)
                if len(parts) == 2:
                    search_logs(parts[1])
                elif len(parts) == 3:
                    search_logs(parts[2], parts[1])
                else:
                    print_error("Usage: :search <query> | :search <type> <query>")
                    print_info("Types: command, output, tags, all")
                    
            elif user_input.startswith(":tag "):
                tags = user_input[5:].split(',')
                tags = [tag.strip() for tag in tags]
                tag_last_command(tags)
                
            elif user_input.startswith(":export"):
                parts = user_input.split()
                if len(parts) == 1:
                    export_logs('markdown')
                elif parts[1] == 'pdf':
                    create_pdf_report()
                elif parts[1] in ['markdown', 'json']:
                    export_logs(parts[1])
                else:
                    print_error("Supported formats: markdown, json, pdf")
                    
            elif user_input == ":dashboard":
                create_html_dashboard()
                    
            elif user_input.startswith(":theme"):
                parts = user_input.split()
                if len(parts) == 1:
                    show_themes()
                elif len(parts) == 2:
                    set_theme(parts[1])
                else:
                    print_error("Usage: :theme | :theme <theme_name>")
                    
            elif user_input == ":screenshot":
                manual_screenshot()
            elif user_input == ":screenshot auto":
                toggle_auto_screenshot()
            elif user_input.startswith(":screenshot "):
                if user_input.endswith("toggle"):
                    toggle_auto_screenshot()
                else:
                    print_error("Usage: :screenshot | :screenshot auto | :screenshot toggle")
                    
            elif user_input == ":alias":
                show_aliases()
            elif user_input == ":status":
                show_status()
            elif user_input == ":clear":
                if confirm(f"⚠️ Delete ALL logs for engagement '{ENGAGEMENT}'?"):
                    conn = sqlite3.connect(DB_PATH)
                    c = conn.cursor()
                    c.execute("DELETE FROM command_logs WHERE engagement=?", (ENGAGEMENT,))
                    c.execute("DELETE FROM screenshots WHERE engagement=?", (ENGAGEMENT,))
                    c.execute("DELETE FROM recordings WHERE engagement=?", (ENGAGEMENT,))
                    c.execute("DELETE FROM highlights WHERE engagement=?", (ENGAGEMENT,))
                    conn.commit()
                    conn.close()
                    HIGHLIGHTS.clear()
                    print_success(f"Logs for `{ENGAGEMENT}` cleared.")
                    
            elif user_input == ":exit":
                if RECORDING:
                    print_warning("Recording in progress!")
                    if confirm("Stop recording and exit?"):
                        stop_recording()
                    else:
                        continue
                
                # Save highlights before exit
                save_highlights()
                        
                if RICH_AVAILABLE:
                    console.print("👋 [bold green]Goodbye! Stay safe out there.[/bold green]")
                else:
                    print("👋 Goodbye! Stay safe out there.")
                break
                
            elif user_input == ":help":
                help_text = """
🔧 Enhanced RedTeam Terminal Commands:

📁 ENGAGEMENT MANAGEMENT:
  :engage <n>         → Create/switch to engagement
  :engage switch <n>  → Switch to existing engagement  
  :engage list           → List all engagements with stats

📼 TERMINAL RECORDING:
  :record start          → Start terminal recording
  :record stop           → Stop and save recording
  :record list           → List all recordings
  :record play <id>      → Playback a recording
  :record export <id> gif → Export recording to GIF (coming soon)

🎯 AUTO-EXTRACTION:
  :highlights            → Show extracted IPs, URLs, credentials, etc.
  :extract <text>        → Manually extract highlights from text

📊 LOGGING & SEARCH:
  :log                   → Show last 5 commands (sanitized)
  :log <number>          → Show last N commands
  :log full              → Show all commands for engagement
  :log raw               → Show unsanitized output
  :search <query>        → Search all fields
  :search <type> <query> → Search specific field (command/output/tags/all)

🏷️ TAGGING & EXPORT:
  :tag <tag1,tag2>       → Tag last command
  :export                → Export markdown report
  :export json           → Export JSON report
  :export pdf            → Export professional PDF report
  :dashboard             → Generate HTML dashboard with charts

🎨 THEMES & STYLING:
  :theme                 → Show available themes
  :theme <n>          → Set theme (default/matrix/stealth/neon)

📷 SCREENSHOTS:
  :screenshot            → Take manual screenshot
  :screenshot auto       → Toggle auto-screenshot mode
  :screenshot toggle     → Toggle auto-screenshot mode

🔧 UTILITIES:
  :alias                 → Show available command aliases
  :status                → Show engagement stats & settings
  :clear                 → Clear engagement logs & recordings
  :help                  → Show this help
  :exit                  → Exit terminal

🚀 NEW FEATURES IN v2.3:
  • TTY support for real-time output (nmap, gobuster, etc.)
  • Interactive command support (ssh, ftp, sqlmap)
  • Auto-extraction of IPs, URLs, passwords, hashes
  • Better handling of long-running commands
  • Enhanced nmap aliases for progressive scanning

📦 DEPENDENCIES:
  pip install rich reportlab pyautogui pillow prompt_toolkit asciinema imageio[ffmpeg]
"""
                if RICH_AVAILABLE:
                    console.print(Panel(help_text, title="Help", style="cyan"))
                else:
                    print(help_text)
            else:
                # Execute as shell command
                run_command(user_input)
                
        except KeyboardInterrupt:
            print_info("Use :exit to quit gracefully")
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()
