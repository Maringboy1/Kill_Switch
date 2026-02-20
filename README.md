# Kill_Switch
This is the GUI version for your Kali Linux to see the current running process. 
# ⚡ KillSwitch PRO — Enterprise Process Manager

> A premium, enterprise-grade GUI process manager built for **Kali Linux**.  
> Monitor, analyze, and safely kill any running process — with full control and zero guesswork.

---

## 📸 Overview

KillSwitch PRO gives you a real-time, color-coded view of every process running on your system — sorted by CPU usage by default. It combines the power of a terminal process monitor with the ease of a polished graphical interface.

Built with Python, `tkinter`, and `psutil` — no heavy dependencies, no bloat.

---

## ✨ Features

### 🖥️ Real-Time Monitoring
- Live process table sorted by **CPU usage** (highest first)
- Auto-refresh every N seconds (adjustable from 1–30s)
- **Live sparkline graphs** for CPU and RAM usage
- System stats bar: CPU %, Memory, Swap, Disk I/O, Network, Process count

### 🎯 Process Control
| Signal | Button | What it does |
|--------|--------|-------------|
| `SIGTERM` | ✕ Graceful Kill | Asks the process to quit — it can save data and clean up |
| `SIGKILL` | ☠ Force Kill | Terminates instantly — no cleanup, no mercy |
| `SIGSTOP` | ⏸ Pause | Freezes the process in place |
| `SIGCONT` | ▶ Resume | Resumes a paused process |

### 🔒 Safety System
- **Protected process list** — `systemd`, `sshd`, `Xorg`, `NetworkManager`, etc. trigger an extra warning before killing
- **Double confirmation** on every kill action — no accidental kills
- **Kill Audit Log** — every action is timestamped and logged at the bottom of the screen

### 🔍 Search & Filter
- Real-time search by process name, PID, user, or status
- **"User procs only"** toggle — filter to just your own processes
- Click any column header to sort by that column

### 📋 Process Details Panel
Click any process to see a live sidebar with:
- Executable path and full command line
- CPU %, Memory (RSS/VMS), thread count
- Parent PID, nice value, start time
- Open files (top 5)
- Active network connections

### 🖱️ Right-Click Context Menu
Right-click any row for instant access to all kill/pause/resume/details actions.

### 📤 Export
- Export the full process list to **CSV** with one click (timestamped filename)

### ⌨️ Keyboard Shortcuts
| Shortcut | Action |
|----------|--------|
| `Del` | SIGTERM (graceful kill) |
| `Ctrl + K` | SIGKILL (force kill) |
| `Ctrl + R` / `F5` | Refresh now |
| `Ctrl + F` | Focus search bar |
| `Esc` | Clear selection |

### 🎨 UI Highlights
- Deep navy + neon cyberpunk terminal aesthetic
- Color-coded CPU threat levels:
  - 🔴 **Red** = >50% CPU (critical)
  - 🟠 **Orange** = >15% CPU (high)
  - 🟡 **Yellow** = >3% CPU (medium)
  - ⚪ **White** = normal
  - 🟢 **Green** = protected system process
- Multi-select support (Ctrl/Shift + click)
- Live clock in the status bar

---

## 🚀 Installation

### Requirements
- Kali Linux (or any Debian-based Linux)
- Python 3.8+
- `psutil` library
- `tkinter` (usually pre-installed)

### Install Dependencies

```bash
pip install psutil --break-system-packages
```

If `tkinter` is missing:

```bash
sudo apt install python3-tk
```

### Run KillSwitch PRO

```bash
python3 killswitch_pro.py
```

For killing **system-level or root processes**:

```bash
sudo python3 killswitch_pro.py
```

---

## 🛡️ Is It Safe?

Yes. Here's why:

- **Running the app does nothing harmful.** It only reads process information until you explicitly click a button.
- **Every kill action has a confirmation dialog.** Nothing happens without your approval.
- **Protected system processes** (`systemd`, `sshd`, `Xorg`, etc.) trigger an extra warning before any signal is sent.
- **SIGTERM is always recommended first.** It gives the process a chance to save data and close cleanly — just like pressing the X button on an app.
- **SIGKILL** should only be used when a process is frozen and won't respond to SIGTERM.

### ⚠️ Processes to Never Kill
These are already protected with warnings in the app, but good to know:

| Process | Risk if killed |
|---------|---------------|
| `systemd` / `init` | Crashes the entire system |
| `Xorg` / `lightdm` / `gdm3` | Logs you out / kills the desktop |
| `sshd` | Drops all SSH connections |
| `NetworkManager` | Drops your network connection |
| `kthreadd` / kernel workers | Kernel crash |

---

## 📁 Project Structure

```
killswitch_pro.py     ← Single-file application (all code in one place)
README.md             ← This file
```

No configuration files. No installation. Just run it.

---

## 🔧 How It Works

KillSwitch PRO uses two main libraries:

- **`psutil`** — Cross-platform library for retrieving system and process information. Reads CPU, memory, status, file handles, network connections, and more.
- **`tkinter`** — Python's built-in GUI toolkit. Renders the window, table, graphs, and all widgets.

The app runs a **background thread** that collects process data every N seconds and pushes updates to the UI thread safely via `tkinter`'s `.after()` mechanism — no race conditions, no frozen UI.

---

## 🧩 Tech Stack

| Component | Technology |
|-----------|-----------|
| Language | Python 3 |
| GUI Framework | tkinter |
| Process Data | psutil |
| Threading | Python threading module |
| Graphs | Custom tkinter Canvas sparklines |
| Export | Python csv module |

---

## 📋 Column Reference

| Column | Description |
|--------|-------------|
| PID | Process ID |
| Process Name | Name of the executable |
| User | Owner of the process |
| CPU % | CPU usage percentage |
| MEM MB | Physical memory used (RSS) in megabytes |
| MEM % | Memory as percentage of total RAM |
| Status | running / sleeping / zombie / stopped |
| Thrd | Number of threads |
| PPID | Parent process ID |
| Nice | Process scheduling priority (-20 to 19) |

---

## 🐛 Troubleshooting

**`ModuleNotFoundError: No module named 'psutil'`**
```bash
pip install psutil --break-system-packages
```

**`ModuleNotFoundError: No module named 'tkinter'`**
```bash
sudo apt install python3-tk
```

**`Permission denied` when killing a process**
```bash
sudo python3 killswitch_pro.py
```

**Process list is empty or incomplete**  
Run with `sudo` to see all system processes including root-owned ones.

---

## 📜 License

MIT License — free to use, modify, and distribute.

---

## 👤 Author

Built for Kali Linux power users who want full visibility and control over their system processes — without touching the terminal every time.

---

> **⚡ KillSwitch PRO** — Because you deserve to know exactly what's running on your machine.
