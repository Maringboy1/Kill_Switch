# ⚡ KillSwitch PRO

> **Enterprise Process Manager for Linux**  
> Built for Kali Linux · Works on any Linux distro

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![Platform](https://img.shields.io/badge/Platform-Linux-orange?style=flat-square&logo=linux)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Version](https://img.shields.io/badge/Version-1.0.0-cyan?style=flat-square)

---

## 📸 Overview

**KillSwitch PRO** is a sleek, dark-themed desktop process manager that gives you full control over every running process on your Linux system. Monitor CPU and memory in real time, send signals, force-kill rogue processes, and export reports — all from a polished GUI.

---

## ✨ Features

- **Real-time process table** — sortable by CPU, memory, PID, user, status, and more
- **Live system stats** — CPU, RAM, Swap, Disk I/O, and Network with sparkline graphs
- **Signal control** — SIGTERM, SIGKILL, SIGSTOP, SIGCONT and any custom signal
- **Protected process detection** — warns before killing critical system processes
- **Process detail panel** — executable path, open files, network connections, and more
- **Kill log** — timestamped record of every action taken
- **Search & filter** — filter by name, PID, user, or status in real time
- **CSV export** — dump the full process list to a spreadsheet
- **Panel / Tray mode** — close the window and it shrinks to a floating ⚡ button instead of quitting
- **Keyboard shortcuts** — power-user friendly

---

## 🚀 Quick Install

```bash
git clone https://github.com/YOUR_USERNAME/killswitch-pro.git
cd killswitch-pro
python3 killswitch_pro.py
```

On **first run**, a popup will ask if you want to add KillSwitch PRO to your application menu. Click **Yes** and it installs itself automatically — no separate installer needed.

Or install silently from the terminal:

```bash
python3 killswitch_pro.py --install
```

The self-installer will:
- Check and install `psutil` if missing
- Copy the app to `~/.local/share/killswitch-pro/`
- Add **KillSwitch PRO** to your application menu with an icon
- Create a `killswitch-pro` terminal command

After that, just search **KillSwitch PRO** in your app menu and click the icon — no terminal needed ever again.

---

## 🖥️ Run Without Installing

```bash
python3 killswitch_pro.py
```

Or after installing:

```bash
killswitch-pro
```

---

## 📋 Requirements

| Requirement | Version |
|-------------|---------|
| Python | 3.8+ |
| tkinter | (usually bundled with Python) |
| psutil | 5.0+ |

Install psutil manually if needed:

```bash
pip3 install psutil --break-system-packages
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Del` | SIGTERM — graceful kill |
| `Ctrl + K` | SIGKILL — force kill |
| `Ctrl + R` / `F5` | Refresh now |
| `Ctrl + F` | Focus search bar |
| `Ctrl + W` | Minimize to panel |
| `Escape` | Deselect all |

---

## 🧲 Panel Mode

KillSwitch PRO stays in your panel — it doesn't just close.

- Press **X** or `Ctrl+W` → window hides, a small **⚡ KillSwitch PRO** floating button appears (bottom-right)
- **Left-click** the button → restores the full window
- **Right-click** the button → Open / Quit menu
- **Drag** the button to reposition it anywhere on screen

To keep it in your taskbar or dock permanently, right-click the app icon in your application menu and select **"Add to Panel"** or **"Pin to Taskbar"** (depends on your desktop environment).

---

## 🛡️ Protected Processes

KillSwitch PRO recognizes critical system processes and will warn you before sending a signal to them:

`systemd`, `init`, `kthreadd`, `sshd`, `NetworkManager`, `Xorg`, `gdm3`, and more.

> ⚠️ Killing protected processes **can crash your system**. Always read the warning dialog.

---

## 📂 File Structure

```
killswitch-pro/
├── killswitch_pro.py   # Main application (self-installer built in)
└── README.md
```

---

## 👨‍💻 Developer

**Komo Moko**  
Built with Python · tkinter · psutil

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

```
MIT License

Copyright (c) 2025 Komo Moko

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

> *KillSwitch PRO — because Task Manager was never enough.*
