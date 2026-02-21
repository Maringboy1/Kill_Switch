#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║       KILLSWITCH PRO — Enterprise Process Manager            ║
║       Kali Linux Edition  |  Premium Build                   ║
║       + Panel / Tray Integration                             ║
╚══════════════════════════════════════════════════════════════╝

How to use:
  • Double-click the .desktop launcher  → opens full window
  • Click X / close → minimizes to a floating ⚡ panel button
  • Click the floating button           → restores full window
  • Right-click floating button         → menu: Open / Quit
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import psutil
import threading
import time
import signal
import os
import csv
import datetime
import collections
import platform

# ══════════════════════════════════════════════════════════════
#  THEME
# ══════════════════════════════════════════════════════════════
BG0   = "#080c14"
BG1   = "#0c1120"
BG2   = "#101829"
BG3   = "#141f33"
BG4   = "#1a2640"
BORD  = "#1e2d45"

CYAN   = "#00d4ff"
GREEN  = "#00ff88"
GREEND = "#00bb66"
ORANGE = "#ff8c00"
RED    = "#ff2d55"
PURPLE = "#a855f7"
YELLOW = "#ffd60a"

TEXT   = "#d4e0f0"
TEXTD  = "#5a7090"
TEXTB  = "#eaf4ff"
ROWEV  = "#0c1120"
ROWOD  = "#0e1528"
ROWSEL = "#0f2040"

FMB  = ("Courier New", 10, "bold")
FM   = ("Courier New", 10)
FMS  = ("Courier New", 9)
FMT  = ("Courier New", 18, "bold")

GRAPH_LEN = 60

PROTECTED = {
    "systemd","init","kthreadd","kworker","migration","watchdog",
    "ksoftirqd","rcu_sched","sshd","NetworkManager","dbus-daemon",
    "udevd","X","Xorg","lightdm","gdm3","wpa_supplicant",
}


# ══════════════════════════════════════════════════════════════
#  SPARKLINE
# ══════════════════════════════════════════════════════════════
SPARK_W = 176
SPARK_H = 44

class Sparkline(tk.Frame):
    def __init__(self, parent, color):
        super().__init__(parent, bg=BG2, width=SPARK_W, height=SPARK_H)
        self.pack_propagate(False)
        self._color = color
        self._data  = collections.deque([0.0] * GRAPH_LEN, maxlen=GRAPH_LEN)
        self._cv    = tk.Canvas(self, width=SPARK_W, height=SPARK_H,
                                background=BG2, highlightthickness=0, bd=0)
        self._cv.place(x=0, y=0, width=SPARK_W, height=SPARK_H)

    def push(self, value):
        self._data.append(max(0.0, min(100.0, float(value))))
        self._draw()

    def _draw(self):
        cv   = self._cv
        W, H = SPARK_W, SPARK_H
        cv.delete("all")
        for i in (1, 2, 3):
            y = int(H * i / 4)
            cv.create_line(0, y, W, y, fill=BORD, width=1)
        data = list(self._data)
        if len(data) < 2:
            return
        step = W / (len(data) - 1)
        pts  = [(i * step, H - (data[i] / 100.0) * (H - 4))
                for i in range(len(data))]
        poly = [0.0, float(H)] + [c for pt in pts for c in pt] + [float(W), float(H)]
        cv.create_polygon(poly, fill=self._color, outline="", stipple="gray12")
        flat = [c for pt in pts for c in pt]
        cv.create_line(flat, fill=self._color, width=2, smooth=True)
        x, y = pts[-1]
        cv.create_oval(x-3, y-3, x+3, y+3, fill=self._color, outline=BG2, width=1)


# ══════════════════════════════════════════════════════════════
#  STAT CARD
# ══════════════════════════════════════════════════════════════
class StatCard(tk.Frame):
    def __init__(self, parent, title, color, has_graph=True):
        super().__init__(parent, bg=BG2,
                         highlightthickness=1, highlightbackground=BORD)
        self._color = color
        tk.Label(self, text=title, font=FMS, fg=TEXTD, bg=BG2).pack(
            anchor="w", padx=10, pady=(8, 0))
        self._val = tk.Label(self, text="—",
                             font=("Courier New", 15, "bold"),
                             fg=color, bg=BG2)
        self._val.pack(anchor="w", padx=10)
        if has_graph:
            self._spark = Sparkline(self, color)
            self._spark.pack(padx=6, pady=(2, 4))
        else:
            self._spark = None
            tk.Frame(self, height=6, bg=BG2).pack()
        self._sub = tk.Label(self, text="", font=FMS, fg=TEXTD, bg=BG2)
        self._sub.pack(anchor="w", padx=10, pady=(0, 8))

    def update_card(self, val_str, sub_str="", graph_val=None):
        try:
            v     = float(val_str.replace("%", "").strip())
            color = RED if v >= 85 else ORANGE if v >= 60 else self._color
        except Exception:
            color = self._color
        self._val.config(text=val_str, fg=color)
        self._sub.config(text=sub_str)
        if self._spark and graph_val is not None:
            self._spark.push(graph_val)


# ══════════════════════════════════════════════════════════════
#  KILL LOG
# ══════════════════════════════════════════════════════════════
class KillLog(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG2,
                         highlightthickness=1, highlightbackground=BORD)
        hdr = tk.Frame(self, bg=BG2)
        hdr.pack(fill="x", padx=10, pady=(6, 2))
        tk.Label(hdr, text="▸ KILL LOG", font=FMB, fg=RED, bg=BG2).pack(side="left")
        tk.Button(hdr, text="Clear", font=FMS, fg=TEXTD,
                  bg=BG3, relief="flat", cursor="hand2",
                  command=self._clear, padx=6, pady=1).pack(side="right")
        self._txt = tk.Text(self, font=("Courier New", 8),
                            bg=BG1, fg=TEXTD, relief="flat",
                            state="disabled", wrap="none", height=6)
        self._txt.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self._txt.tag_config("ts",   foreground=TEXTD)
        self._txt.tag_config("ok",   foreground=GREEN)
        self._txt.tag_config("fail", foreground=RED)
        self._txt.tag_config("term", foreground=ORANGE)
        self._txt.tag_config("kill", foreground=RED)
        self._txt.tag_config("pid",  foreground=CYAN)

    def add(self, pid, name, sig_label, success=True):
        ts   = datetime.datetime.now().strftime("%H:%M:%S")
        icon = "✓" if success else "✗"
        tag  = "kill" if "KILL" in sig_label.upper() else "term"
        self._txt.config(state="normal")
        self._txt.insert("end", f"[{ts}] ", "ts")
        self._txt.insert("end", icon + " ", "ok" if success else "fail")
        self._txt.insert("end", f"[{pid}]", "pid")
        self._txt.insert("end", f" {name:<20} → {sig_label}\n", tag)
        self._txt.see("end")
        self._txt.config(state="disabled")

    def _clear(self):
        self._txt.config(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.config(state="disabled")


# ══════════════════════════════════════════════════════════════
#  DETAIL PANEL
# ══════════════════════════════════════════════════════════════
class DetailPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BG2,
                         highlightthickness=1, highlightbackground=BORD)
        tk.Label(self, text="▸ PROCESS DETAILS", font=FMB,
                 fg=CYAN, bg=BG2).pack(anchor="w", padx=10, pady=(10, 4))
        self._txt = tk.Text(self, font=("Courier New", 8),
                            bg=BG1, fg=TEXT, relief="flat",
                            state="disabled", wrap="word")
        self._txt.pack(fill="both", expand=True, padx=6, pady=(0, 6))
        self._txt.tag_config("k",    foreground=CYAN)
        self._txt.tag_config("v",    foreground=TEXT)
        self._txt.tag_config("h",    foreground=GREEN,  font=FMB)
        self._txt.tag_config("warn", foreground=ORANGE)
        self._txt.tag_config("dim",  foreground=TEXTD)

    def show(self, pid):
        self._txt.config(state="normal")
        self._txt.delete("1.0", "end")
        try:
            p = psutil.Process(pid)
            nfo = p.as_dict(attrs=["pid","name","exe","cmdline","username",
                                   "status","create_time","cpu_percent",
                                   "memory_percent","memory_info",
                                   "num_threads","nice","ppid"])

            def row(k, v):
                self._txt.insert("end", f"  {k:<14} ", "k")
                self._txt.insert("end", f"{v}\n", "v")

            self._txt.insert("end", "── GENERAL ──────────────\n", "h")
            row("PID",     nfo.get("pid","?"))
            row("Name",    nfo.get("name","?"))
            row("Status",  nfo.get("status","?"))
            row("User",    nfo.get("username","?"))
            row("Parent",  nfo.get("ppid","?"))
            row("Nice",    nfo.get("nice","?"))
            ct = nfo.get("create_time")
            if ct:
                row("Started", datetime.datetime.fromtimestamp(ct)
                    .strftime("%Y-%m-%d %H:%M:%S"))

            self._txt.insert("end", "\n── PERFORMANCE ──────────\n", "h")
            row("CPU %",   f'{nfo.get("cpu_percent",0):.2f}%')
            row("MEM %",   f'{nfo.get("memory_percent",0):.2f}%')
            mi = nfo.get("memory_info")
            if mi:
                row("RSS",  f'{mi.rss/1048576:.1f} MB')
                row("VMS",  f'{mi.vms/1048576:.1f} MB')
            row("Threads", nfo.get("num_threads","?"))

            self._txt.insert("end", "\n── EXECUTABLE ───────────\n", "h")
            self._txt.insert("end", f"  {nfo.get('exe') or 'N/A'}\n", "dim")

            cmd = nfo.get("cmdline") or []
            if cmd:
                self._txt.insert("end", "\n── COMMAND ──────────────\n", "h")
                self._txt.insert("end", f"  {' '.join(cmd[:5])}\n", "dim")

            try:
                fls = p.open_files()[:5]
                if fls:
                    self._txt.insert("end", "\n── OPEN FILES (top 5) ───\n", "h")
                    for f in fls:
                        self._txt.insert("end", f"  {f.path}\n", "dim")
            except Exception:
                pass

            try:
                conns = p.net_connections()[:4]
                if conns:
                    self._txt.insert("end", "\n── CONNECTIONS ──────────\n", "h")
                    for c in conns:
                        la = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "?"
                        ra = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else "?"
                        self._txt.insert("end", f"  {la} → {ra} [{c.status}]\n", "dim")
            except Exception:
                pass

            if nfo.get("name") in PROTECTED:
                self._txt.insert("end", "\n⚠  PROTECTED SYSTEM PROCESS\n", "warn")

        except psutil.NoSuchProcess:
            self._txt.insert("end", "  Process no longer exists.\n", "warn")
        except psutil.AccessDenied:
            self._txt.insert("end", "  Access denied — run as sudo.\n", "warn")
        except Exception as e:
            self._txt.insert("end", f"  Error: {e}\n", "warn")

        self._txt.config(state="disabled")

    def clear(self):
        self._txt.config(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.config(state="disabled")


# ══════════════════════════════════════════════════════════════
#  FLOATING PANEL BUTTON  (appears when main window is hidden)
# ══════════════════════════════════════════════════════════════
class FloatingPanel(tk.Toplevel):
    """
    A small always-on-top button that acts as a system-tray substitute.
    Appears in the bottom-right corner when the main window is minimized.
    Left-click → restore main window.
    Right-click → context menu (Open / Quit).
    Drag → reposition anywhere on screen.
    """

    def __init__(self, master, on_open, on_quit):
        super().__init__(master)
        self._on_open = on_open
        self._on_quit = on_quit

        # Window chrome
        self.overrideredirect(True)   # borderless
        self.attributes("-topmost", True)
        self.configure(bg=BG3)
        self.resizable(False, False)

        # Position: bottom-right corner
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"+{sw - 120}+{sh - 60}")

        # Content
        self._build()
        self._drag_x = self._drag_y = 0

    def _build(self):
        frame = tk.Frame(self, bg=BG3,
                         highlightthickness=1, highlightbackground=CYAN,
                         cursor="hand2")
        frame.pack(fill="both", expand=True)

        # Pulse dot
        self._dot = tk.Label(frame, text="●", font=("Courier New", 9),
                             fg=GREEN, bg=BG3)
        self._dot.pack(side="left", padx=(8, 2))
        self._pulse()

        tk.Label(frame, text="⚡ KillSwitch", font=("Courier New", 9, "bold"),
                 fg=CYAN, bg=BG3).pack(side="left")
        tk.Label(frame, text="PRO", font=("Courier New", 7, "bold"),
                 fg=RED, bg=BG3).pack(side="left", padx=(1, 8))

        # Events
        for w in (frame, self._dot):
            w.bind("<Button-1>",        self._click)
            w.bind("<Button-3>",        self._ctx_menu)
            w.bind("<ButtonPress-1>",   self._drag_start)
            w.bind("<B1-Motion>",       self._drag_move)

        # Context menu
        self._menu = tk.Menu(self, tearoff=0, bg=BG3, fg=TEXT,
                             activebackground=BG4, activeforeground=CYAN,
                             font=FM, bd=0, relief="flat")
        self._menu.add_command(label="  ⚡  Open KillSwitch PRO",
                               command=self._on_open)
        self._menu.add_separator()
        self._menu.add_command(label="  ✕  Quit",
                               command=self._on_quit,
                               foreground=RED)

    def _pulse(self):
        current = self._dot.cget("fg")
        self._dot.config(fg=GREEN if current == TEXTD else TEXTD)
        self.after(900, self._pulse)

    def _click(self, _e=None):
        self._on_open()

    def _ctx_menu(self, e):
        self._menu.tk_popup(e.x_root, e.y_root)

    def _drag_start(self, e):
        self._drag_x = e.x
        self._drag_y = e.y

    def _drag_move(self, e):
        x = self.winfo_x() + (e.x - self._drag_x)
        y = self.winfo_y() + (e.y - self._drag_y)
        self.geometry(f"+{x}+{y}")


# ══════════════════════════════════════════════════════════════
#  MAIN APPLICATION
# ══════════════════════════════════════════════════════════════
class KillSwitchPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("KillSwitch PRO — Enterprise Process Manager")
        self.geometry("1380x840")
        self.minsize(1100, 660)
        self.configure(bg=BG0)

        self.selected_pids = set()
        self.search_var    = tk.StringVar()
        self.auto_refresh  = tk.BooleanVar(value=True)
        self.refresh_secs  = tk.IntVar(value=3)
        self.show_useronly = tk.BooleanVar(value=False)
        self._running      = True
        self._processes    = []
        self._sort_col     = "cpu"
        self._sort_rev     = True
        self._floating     = None   # FloatingPanel instance

        self._build_ui()
        self._bind_keys()
        self._start_bg_thread()
        self.protocol("WM_DELETE_WINDOW", self._minimize_to_panel)

    # ─────────────────────────────────────────────────────
    #  PANEL / TRAY  INTEGRATION
    # ─────────────────────────────────────────────────────
    def _minimize_to_panel(self):
        """Hide main window, show floating panel button."""
        self.withdraw()
        if self._floating is None or not self._floating.winfo_exists():
            self._floating = FloatingPanel(
                self,
                on_open=self._restore_from_panel,
                on_quit=self._quit_app,
            )
        else:
            self._floating.deiconify()

    def _restore_from_panel(self):
        """Show main window, hide floating panel."""
        if self._floating and self._floating.winfo_exists():
            self._floating.withdraw()
        self.deiconify()
        self.lift()
        self.focus_force()

    def _quit_app(self):
        self._running = False
        if self._floating and self._floating.winfo_exists():
            self._floating.destroy()
        self.destroy()

    # ─────────────────────────────────────────────────────
    #  UI BUILD
    # ─────────────────────────────────────────────────────
    def _build_ui(self):
        self._build_titlebar()
        self._build_stats_row()
        self._build_main()
        self._build_statusbar()

    def _build_titlebar(self):
        bar = tk.Frame(self, bg=BG3,
                       highlightthickness=1, highlightbackground=BORD)
        bar.pack(fill="x")

        left = tk.Frame(bar, bg=BG3)
        left.pack(side="left", padx=16, pady=10)
        tk.Label(left, text="⚡", font=("Courier New", 18),
                 fg=CYAN, bg=BG3).pack(side="left")
        tk.Label(left, text=" KILLSWITCH", font=FMT,
                 fg=CYAN, bg=BG3).pack(side="left")
        tk.Label(left, text=" PRO", font=("Courier New", 12, "bold"),
                 fg=RED, bg=BG3).pack(side="left", pady=(6, 0))
        tk.Label(left,
                 text="   Enterprise Process Manager  |  Kali Linux",
                 font=FMS, fg=TEXTD, bg=BG3).pack(side="left", padx=10)

        right = tk.Frame(bar, bg=BG3)
        right.pack(side="right", padx=16)
        u = platform.uname()
        tk.Label(right, text=f"{u.system} {u.release}",
                 font=FMS, fg=TEXTD, bg=BG3).pack()
        tk.Label(right, text=u.node,
                 font=FMB, fg=GREEN, bg=BG3).pack()

        # Minimize-to-panel button in titlebar
        tk.Button(bar, text="⬇ Panel", font=FMS, fg=CYAN,
                  bg=BG4, relief="flat", cursor="hand2",
                  command=self._minimize_to_panel,
                  padx=8, pady=4,
                  activebackground=BORD,
                  activeforeground=CYAN).pack(side="right", padx=8, pady=8)

    def _build_stats_row(self):
        row = tk.Frame(self, bg=BG0, pady=8)
        row.pack(fill="x", padx=14)

        self._c_cpu   = StatCard(row, "CPU USAGE",  CYAN,   has_graph=True)
        self._c_mem   = StatCard(row, "MEMORY",     GREEN,  has_graph=True)
        self._c_swap  = StatCard(row, "SWAP",       ORANGE, has_graph=False)
        self._c_disk  = StatCard(row, "DISK I/O",   PURPLE, has_graph=False)
        self._c_net   = StatCard(row, "NETWORK",    YELLOW, has_graph=False)
        self._c_procs = StatCard(row, "PROCESSES",  CYAN,   has_graph=False)

        for c in (self._c_cpu, self._c_mem, self._c_swap,
                  self._c_disk, self._c_net, self._c_procs):
            c.pack(side="left", padx=5, fill="y")

    def _build_main(self):
        outer = tk.Frame(self, bg=BG0)
        outer.pack(fill="both", expand=True, padx=14, pady=(0, 6))

        left = tk.Frame(outer, bg=BG0)
        left.pack(side="left", fill="both", expand=True)

        self._build_toolbar(left)
        self._build_table(left)

        self._kill_log = KillLog(left)
        self._kill_log.pack(fill="x", pady=(6, 0))

        self._detail = DetailPanel(outer)
        self._detail.pack(side="right", fill="y", padx=(8, 0))
        self._detail.config(width=270)
        self._detail.pack_propagate(False)

    def _build_toolbar(self, parent):
        bar = tk.Frame(parent, bg=BG3,
                       highlightthickness=1, highlightbackground=BORD,
                       pady=7)
        bar.pack(fill="x", pady=(0, 6))

        # Row 1
        r1 = tk.Frame(bar, bg=BG3)
        r1.pack(fill="x", padx=10, pady=(0, 4))

        tk.Label(r1, text="🔍", font=("", 12), bg=BG3, fg=CYAN).pack(side="left")
        self._search_entry = tk.Entry(r1, textvariable=self.search_var,
                                      font=FM, bg=BG4, fg=TEXT,
                                      insertbackground=CYAN,
                                      relief="flat", width=28)
        self._search_entry.pack(side="left", padx=(4, 10))
        self.search_var.trace_add("write", lambda *_: self._populate())

        tk.Button(r1, text="✕ Clear", font=FMS, fg=TEXTD,
                  bg=BG4, relief="flat", cursor="hand2",
                  command=lambda: self.search_var.set(""),
                  padx=5).pack(side="left")

        ttk.Separator(r1, orient="vertical").pack(side="left", fill="y",
                                                  padx=10, pady=2)
        tk.Checkbutton(r1, text="My Processes Only",
                       variable=self.show_useronly,
                       command=self._populate,
                       bg=BG3, fg=TEXT, selectcolor=BG4,
                       activebackground=BG3, font=FMS).pack(side="left")

        ttk.Separator(r1, orient="vertical").pack(side="left", fill="y",
                                                  padx=10, pady=2)
        tk.Checkbutton(r1, text="Auto-Refresh",
                       variable=self.auto_refresh,
                       bg=BG3, fg=TEXT, selectcolor=BG4,
                       activebackground=BG3, font=FMS).pack(side="left")
        tk.Label(r1, text="every", font=FMS, fg=TEXTD, bg=BG3).pack(side="left", padx=(6,2))
        tk.Spinbox(r1, from_=1, to=30, width=3,
                   textvariable=self.refresh_secs,
                   font=FMS, bg=BG4, fg=TEXT,
                   buttonbackground=BG3,
                   relief="flat").pack(side="left")
        tk.Label(r1, text="s", font=FMS, fg=TEXTD, bg=BG3).pack(side="left", padx=(2,10))

        tk.Button(r1, text="⟳ Refresh Now", font=FMS, fg=CYAN,
                  bg=BG4, relief="flat", cursor="hand2",
                  command=self._refresh_now,
                  padx=8).pack(side="left")
        tk.Button(r1, text="💾 Export CSV", font=FMS, fg=YELLOW,
                  bg=BG4, relief="flat", cursor="hand2",
                  command=self._export_csv,
                  padx=8).pack(side="left", padx=(6,0))

        # Row 2 – kill buttons
        r2 = tk.Frame(bar, bg=BG3)
        r2.pack(fill="x", padx=10)

        tk.Label(r2, text="SIGNAL:", font=FMB, fg=TEXTD, bg=BG3).pack(side="left")

        def kill_btn(text, color, cmd):
            return tk.Button(r2, text=text, font=FMB, fg=color,
                             bg=BG4, relief="flat", cursor="hand2",
                             command=cmd, padx=10, pady=3,
                             activebackground=BORD, activeforeground=color)

        kill_btn("  ✕  SIGTERM  (Graceful)", ORANGE,
                 self._kill_sigterm).pack(side="left", padx=(8, 4))
        kill_btn("  ☠  SIGKILL  (Force)", RED,
                 self._kill_sigkill).pack(side="left", padx=4)
        kill_btn("  ⏸  SIGSTOP", PURPLE,
                 lambda: self._send_signal(signal.SIGSTOP, "SIGSTOP")).pack(side="left", padx=4)
        kill_btn("  ▶  SIGCONT", GREEN,
                 lambda: self._send_signal(signal.SIGCONT, "SIGCONT")).pack(side="left", padx=4)
        kill_btn("  ✕  Deselect", TEXTD,
                 self._clear_sel).pack(side="right", padx=4)

        self._sel_lbl = tk.Label(r2, text="  No process selected",
                                 font=FMS, fg=TEXTD, bg=BG3)
        self._sel_lbl.pack(side="right")

    def _build_table(self, parent):
        frame = tk.Frame(parent, bg=BG0)
        frame.pack(fill="both", expand=True)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("KP.Treeview",
                        background=ROWEV, foreground=TEXT,
                        rowheight=22, fieldbackground=ROWEV,
                        borderwidth=0, font=FM)
        style.configure("KP.Treeview.Heading",
                        background=BG3, foreground=CYAN,
                        relief="flat", font=FMB, padding=(4, 4))
        style.map("KP.Treeview",
                  background=[("selected", ROWSEL)],
                  foreground=[("selected", TEXTB)])
        style.map("KP.Treeview.Heading",
                  background=[("active", BG4)])

        cols = ("pid","name","user","cpu","mem_mb","mem_pct",
                "status","threads","ppid","nice")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings",
                                 style="KP.Treeview",
                                 selectmode="extended")

        hdrs = {"pid":("PID",60), "name":("PROCESS NAME",200),
                "user":("USER",90), "cpu":("CPU %",80),
                "mem_mb":("MEM MB",80), "mem_pct":("MEM %",70),
                "status":("STATUS",80), "threads":("THREADS",65),
                "ppid":("PPID",65), "nice":("NICE",50)}
        for col, (hdr, w) in hdrs.items():
            self.tree.heading(col, text=hdr,
                              command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=w, minwidth=40, stretch=(col=="name"))

        # Tags
        self.tree.tag_configure("even",  background=ROWEV)
        self.tree.tag_configure("odd",   background=ROWOD)
        self.tree.tag_configure("crit",  foreground=RED)
        self.tree.tag_configure("high",  foreground=ORANGE)
        self.tree.tag_configure("med",   foreground=YELLOW)
        self.tree.tag_configure("low",   foreground=TEXT)
        self.tree.tag_configure("prot",  foreground=PURPLE)

        sb = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._on_select)
        self.tree.bind("<Double-1>",         self._show_detail)
        self.tree.bind("<Button-3>",         self._ctx_menu)

        # Context menu
        self._ctx = tk.Menu(self, tearoff=0, bg=BG3, fg=TEXT,
                            activebackground=BG4, activeforeground=CYAN,
                            font=FM, bd=0)
        self._ctx.add_command(label="  ✕  SIGTERM — Graceful Kill",
                              command=self._kill_sigterm,
                              foreground=ORANGE)
        self._ctx.add_command(label="  ☠  SIGKILL — Force Kill",
                              command=self._kill_sigkill,
                              foreground=RED)
        self._ctx.add_separator()
        self._ctx.add_command(label="  ⏸  SIGSTOP — Pause",
                              command=lambda: self._send_signal(
                                  signal.SIGSTOP, "SIGSTOP"))
        self._ctx.add_command(label="  ▶  SIGCONT — Resume",
                              command=lambda: self._send_signal(
                                  signal.SIGCONT, "SIGCONT"))
        self._ctx.add_separator()
        self._ctx.add_command(label="  🔍  Show Details",
                              command=self._show_detail)

    def _build_statusbar(self):
        bar = tk.Frame(self, bg=BG3, pady=4,
                       highlightthickness=1, highlightbackground=BORD)
        bar.pack(fill="x")

        self._status_var = tk.StringVar(value="  Ready.")
        tk.Label(bar, textvariable=self._status_var,
                 font=FMS, fg=TEXTD, bg=BG3,
                 anchor="w").pack(side="left", padx=14)

        self._clock = tk.Label(bar, text="", font=FMS, fg=TEXTD, bg=BG3)
        self._clock.pack(side="right", padx=14)
        self._tick()

        tk.Label(bar,
                 text="Del=SIGTERM  Ctrl+K=SIGKILL  "
                      "Ctrl+R / F5=Refresh  Ctrl+F=Search  Ctrl+W=Panel",
                 font=FMS, fg=TEXTD, bg=BG3).pack(side="right", padx=20)

    def _tick(self):
        self._clock.config(
            text=datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S"))
        self.after(1000, self._tick)

    # ─────────────────────────────────────────────────────
    #  KEYBOARD SHORTCUTS
    # ─────────────────────────────────────────────────────
    def _bind_keys(self):
        self.bind("<Delete>",    lambda e: self._kill_sigterm())
        self.bind("<Control-k>", lambda e: self._kill_sigkill())
        self.bind("<Control-r>", lambda e: self._refresh_now())
        self.bind("<F5>",        lambda e: self._refresh_now())
        self.bind("<Control-f>", lambda e: self._search_entry.focus_set())
        self.bind("<Escape>",    lambda e: self._clear_sel())
        self.bind("<Control-w>", lambda e: self._minimize_to_panel())

    # ─────────────────────────────────────────────────────
    #  DATA COLLECTION
    # ─────────────────────────────────────────────────────
    def _collect_procs(self):
        out   = []
        attrs = ["pid","name","username","cpu_percent","memory_info",
                 "memory_percent","status","num_threads","ppid","nice"]
        for p in psutil.process_iter(attrs):
            try:
                i = p.info
                out.append({
                    "pid":    i["pid"],
                    "name":   i["name"] or "?",
                    "user":   (i["username"] or "?").split("\\")[-1],
                    "cpu":    i["cpu_percent"] or 0.0,
                    "mem_mb": round(
                        (i["memory_info"].rss
                         if i["memory_info"] else 0) / 1048576, 1),
                    "mem_pct":round(i["memory_percent"] or 0.0, 2),
                    "status": i["status"] or "?",
                    "threads":i["num_threads"] or 0,
                    "ppid":   i["ppid"] or 0,
                    "nice":   i["nice"] if i["nice"] is not None else 0,
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied,
                    psutil.ZombieProcess):
                continue
        return out

    def _collect_sys(self):
        return (psutil.cpu_percent(interval=None),
                psutil.virtual_memory(),
                psutil.swap_memory(),
                psutil.disk_io_counters(),
                psutil.net_io_counters())

    # ─────────────────────────────────────────────────────
    #  BACKGROUND THREAD
    # ─────────────────────────────────────────────────────
    def _start_bg_thread(self):
        psutil.cpu_percent(interval=None)
        for p in psutil.process_iter(["cpu_percent"]):
            try: p.cpu_percent(interval=None)
            except Exception: pass

        def loop():
            time.sleep(0.6)
            while self._running:
                if self.auto_refresh.get():
                    procs = self._collect_procs()
                    sys   = self._collect_sys()
                    self.after(0, lambda p=procs, s=sys: self._apply(p, s))
                time.sleep(max(1, self.refresh_secs.get()))

        threading.Thread(target=loop, daemon=True).start()

    def _refresh_now(self):
        def _do():
            p = self._collect_procs()
            s = self._collect_sys()
            self.after(0, lambda: self._apply(p, s))
        threading.Thread(target=_do, daemon=True).start()
        self._status_var.set("  Refreshing…")

    def _apply(self, procs, sys_stat):
        self._processes = procs
        self._populate()
        self._update_sys(sys_stat)

    # ─────────────────────────────────────────────────────
    #  TABLE POPULATE
    # ─────────────────────────────────────────────────────
    def _populate(self):
        query    = self.search_var.get().lower().strip()
        useronly = self.show_useronly.get()
        me       = os.environ.get("USER", "root")
        procs    = self._processes[:]

        if query:
            procs = [p for p in procs if
                     query in p["name"].lower() or
                     query in str(p["pid"]) or
                     query in p["user"].lower() or
                     query in p["status"].lower()]
        if useronly:
            procs = [p for p in procs if p["user"] == me]

        num_cols = {"pid","cpu","mem_mb","mem_pct","threads","ppid","nice"}
        col, rev = self._sort_col, self._sort_rev
        if col in num_cols:
            procs = sorted(procs, key=lambda x: float(x.get(col, 0)), reverse=rev)
        else:
            procs = sorted(procs, key=lambda x: str(x.get(col, "")), reverse=rev)

        sel_pids = self.selected_pids.copy()
        ypos     = self.tree.yview()

        self.tree.delete(*self.tree.get_children())
        for i, p in enumerate(procs):
            cpu  = p["cpu"]
            name = p["name"]
            ctag = ("crit" if cpu >= 50 else
                    "high" if cpu >= 15 else
                    "med"  if cpu >= 3  else "low")
            rtag = "even" if i % 2 == 0 else "odd"
            ptag = "prot" if name in PROTECTED else ""
            tags = tuple(t for t in (ctag, rtag, ptag) if t)
            self.tree.insert("", "end", iid=str(p["pid"]),
                             values=(
                                 p["pid"], p["name"], p["user"],
                                 f'{cpu:.1f}%', p["mem_mb"],
                                 f'{p["mem_pct"]:.1f}%',
                                 p["status"], p["threads"],
                                 p["ppid"], p["nice"]
                             ),
                             tags=tags)
            if p["pid"] in sel_pids:
                self.tree.selection_add(str(p["pid"]))

        self.tree.yview_moveto(ypos[0])
        self._status_var.set(
            f"  {len(procs)} / {len(self._processes)} processes"
            f"  |  sorted by {self._sort_col.upper()}"
            f"  {'↓' if self._sort_rev else '↑'}")

    # ─────────────────────────────────────────────────────
    #  SYSTEM STATS UPDATE
    # ─────────────────────────────────────────────────────
    def _update_sys(self, stat):
        cpu, mem, swap, disk, net = stat

        self._c_cpu.update_card(
            f"{cpu:.1f}%",
            f"{psutil.cpu_count(logical=False)} phys / "
            f"{psutil.cpu_count()} logical cores",
            graph_val=cpu)

        ug = mem.used  / (1024**3)
        tg = mem.total / (1024**3)
        self._c_mem.update_card(
            f"{mem.percent:.1f}%",
            f"{ug:.1f} GB / {tg:.1f} GB",
            graph_val=mem.percent)

        us = swap.used  / (1024**3)
        ts_v = swap.total / (1024**3)
        self._c_swap.update_card(
            f"{swap.percent:.1f}%",
            f"{us:.1f} GB / {ts_v:.1f} GB")

        if disk:
            rd = disk.read_bytes  / (1024**2)
            wr = disk.write_bytes / (1024**2)
            self._c_disk.update_card(f"R {rd:.0f} MB", f"W {wr:.0f} MB total")

        sm = net.bytes_sent / (1024**2)
        rm = net.bytes_recv / (1024**2)
        self._c_net.update_card(f"↑ {sm:.0f} MB", f"↓ {rm:.0f} MB recv")

        tt = sum(p["threads"] for p in self._processes)
        self._c_procs.update_card(str(len(self._processes)), f"Threads: {tt}")

    # ─────────────────────────────────────────────────────
    #  SORTING
    # ─────────────────────────────────────────────────────
    def _sort_by(self, col):
        self._sort_rev = (not self._sort_rev
                          if self._sort_col == col else True)
        self._sort_col = col
        self._populate()

    # ─────────────────────────────────────────────────────
    #  SELECTION
    # ─────────────────────────────────────────────────────
    def _on_select(self, _event=None):
        sel = self.tree.selection()
        self.selected_pids = {int(s) for s in sel}
        if len(sel) == 1:
            vals = self.tree.item(sel[0])["values"]
            self._sel_lbl.config(text=f"  [{vals[0]}] {vals[1]}")
            self._detail.show(int(sel[0]))
        elif len(sel) > 1:
            self._sel_lbl.config(text=f"  {len(sel)} selected")
            self._detail.clear()
        else:
            self._sel_lbl.config(text="  No process selected")
            self._detail.clear()

    def _clear_sel(self):
        self.tree.selection_set([])
        self.selected_pids = set()
        self._on_select()

    def _show_detail(self, _e=None):
        sel = self.tree.selection()
        if sel:
            self._detail.show(int(sel[0]))

    def _ctx_menu(self, event):
        iid = self.tree.identify_row(event.y)
        if iid:
            if iid not in self.tree.selection():
                self.tree.selection_set(iid)
            self._on_select()
            self._ctx.tk_popup(event.x_root, event.y_root)

    # ─────────────────────────────────────────────────────
    #  KILL / SIGNAL LOGIC
    # ─────────────────────────────────────────────────────
    def _kill_sigterm(self):
        self._do_kill(signal.SIGTERM, "SIGTERM", graceful=True)

    def _kill_sigkill(self):
        self._do_kill(signal.SIGKILL, "SIGKILL", graceful=False)

    def _send_signal(self, sig, label):
        if not self.selected_pids:
            messagebox.showwarning("No Selection", "Select a process first.")
            return
        for pid in list(self.selected_pids):
            try:
                name = psutil.Process(pid).name()
                os.kill(pid, sig)
                self._kill_log.add(pid, name, label, success=True)
                self._status_var.set(f"  ✓  Sent {label} to [{pid}] {name}")
            except Exception as e:
                self._status_var.set(f"  ✗  Failed: {e}")
        self.after(500, self._refresh_now)

    def _do_kill(self, sig, sig_name, graceful=True):
        if not self.selected_pids:
            messagebox.showwarning("No Selection",
                                   "Please select a process first.")
            return

        targets, prot_names = [], []
        for pid in self.selected_pids:
            try:
                p    = psutil.Process(pid)
                name = p.name()
                targets.append((pid, name))
                if name in PROTECTED:
                    prot_names.append(name)
            except psutil.NoSuchProcess:
                pass
            except psutil.AccessDenied:
                messagebox.showerror("Access Denied",
                    f"Cannot access PID {pid}.\n"
                    "Run with sudo for system processes.")
                return

        if not targets:
            messagebox.showerror("Error", "No valid processes selected.")
            return

        if prot_names:
            if not messagebox.askyesno(
                "⚠  Protected System Process",
                f"WARNING: Protected system process selected:\n\n"
                f"  {', '.join(prot_names)}\n\n"
                "Killing this may CRASH your system.\n"
                "Are you absolutely sure?", icon="warning"):
                return

        label     = f"{sig_name} ({'Graceful' if graceful else 'Force'})"
        names_str = "\n".join(f"  [{p}] {n}" for p, n in targets[:8])
        if len(targets) > 8:
            names_str += f"\n  … and {len(targets)-8} more"

        msg = (f"Send {label} to:\n\n{names_str}\n\n"
               "The process will be asked to quit gracefully.\n"
               "Unsaved work may be preserved."
               if graceful else
               f"⚠️  FORCE KILL via {label}:\n\n{names_str}\n\n"
               "Process will be terminated IMMEDIATELY.\n"
               "Unsaved data WILL be lost.")

        if not messagebox.askyesno("Confirm", msg, icon="warning"):
            return

        killed, failed = [], []
        for pid, name in targets:
            try:
                os.kill(pid, sig)
                killed.append((pid, name))
                self._kill_log.add(pid, name, label, success=True)
            except ProcessLookupError:
                failed.append((pid, name, "no longer exists"))
            except PermissionError:
                failed.append((pid, name, "permission denied — use sudo"))
                self._kill_log.add(pid, name, label, success=False)
            except Exception as e:
                failed.append((pid, name, str(e)))
                self._kill_log.add(pid, name, label, success=False)

        if killed:
            self._status_var.set(
                f"  ✓  {sig_name} sent to {len(killed)} process(es)"
                + (f"  |  {len(failed)} failed" if failed else ""))
        if failed:
            details = "\n".join(f"  [{p}] {n}: {r}" for p, n, r in failed)
            messagebox.showerror("Some Operations Failed",
                                 f"Failed:\n{details}")

        self.selected_pids = set()
        self._sel_lbl.config(text="  No process selected")
        self.after(600, self._refresh_now)

    # ─────────────────────────────────────────────────────
    #  EXPORT CSV
    # ─────────────────────────────────────────────────────
    def _export_csv(self):
        ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv"), ("All", "*.*")],
            initialfile=f"processes_{ts}.csv")
        if not path:
            return
        try:
            with open(path, "w", newline="") as f:
                w = csv.writer(f)
                w.writerow(["PID","Name","User","CPU%","MEM_MB",
                            "MEM%","Status","Threads","PPID","Nice"])
                for p in self._processes:
                    w.writerow([p["pid"],p["name"],p["user"],
                                p["cpu"],p["mem_mb"],p["mem_pct"],
                                p["status"],p["threads"],
                                p["ppid"],p["nice"]])
            self._status_var.set(
                f"  ✓  Exported {len(self._processes)} "
                f"processes → {path}")
        except Exception as e:
            messagebox.showerror("Export Failed", str(e))

    # ─────────────────────────────────────────────────────
    #  CLOSE
    # ─────────────────────────────────────────────────────
    def _on_close(self):
        self._running = False
        self.destroy()



# ══════════════════════════════════════════════════════════════
#  SELF-INSTALLER
# ══════════════════════════════════════════════════════════════
import sys
import shutil
import subprocess

INSTALL_DIR  = os.path.expanduser("~/.local/share/killswitch-pro")
DESKTOP_DIR  = os.path.expanduser("~/.local/share/applications")
BIN_DIR      = os.path.expanduser("~/.local/bin")
DESKTOP_PATH = os.path.join(DESKTOP_DIR, "killswitch-pro.desktop")
BIN_PATH     = os.path.join(BIN_DIR, "killswitch-pro")
APP_PATH     = os.path.join(INSTALL_DIR, "killswitch_pro.py")


def _self_install():
    this_file = os.path.abspath(__file__)

    print("\n  ⚡ KillSwitch PRO — Self Installer")
    print("  ════════════════════════════════════")

    # 1. Check psutil
    print("  [1/4] Checking dependencies...")
    try:
        import psutil  # noqa
        print("        ✓ psutil OK")
    except ImportError:
        print("        Installing psutil...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "psutil",
             "--break-system-packages", "-q"],
            stderr=subprocess.DEVNULL)
        print("        ✓ psutil installed")

    # 2. Copy app file
    print(f"  [2/4] Installing to {INSTALL_DIR}...")
    os.makedirs(INSTALL_DIR, exist_ok=True)
    shutil.copy2(this_file, APP_PATH)
    os.chmod(APP_PATH, 0o755)
    print("        ✓ App file copied")

    # 3. Create .desktop entry
    print("  [3/4] Creating application menu entry...")
    os.makedirs(DESKTOP_DIR, exist_ok=True)
    desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name=KillSwitch PRO
GenericName=Process Manager
Comment=Enterprise Process Manager — monitor, signal, and kill Linux processes
Icon=utilities-system-monitor
Exec=python3 {APP_PATH}
Terminal=false
Categories=System;Monitor;
Keywords=process;kill;monitor;system;manager;kali;
StartupNotify=true
StartupWMClass=KillSwitchPro
"""
    with open(DESKTOP_PATH, "w") as f:
        f.write(desktop_content)
    os.chmod(DESKTOP_PATH, 0o755)

    # Make trusted (GNOME/Nautilus)
    try:
        subprocess.run(["gio", "set", DESKTOP_PATH, "metadata::trusted", "true"],
                       stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # Refresh app menu
    try:
        subprocess.run(["update-desktop-database", DESKTOP_DIR],
                       stderr=subprocess.DEVNULL)
    except Exception:
        pass
    print("        ✓ App menu entry created")

    # 4. CLI shortcut
    print("  [4/4] Creating terminal shortcut...")
    os.makedirs(BIN_DIR, exist_ok=True)
    with open(BIN_PATH, "w") as f:
        f.write(f"#!/usr/bin/env bash\nexec python3 {APP_PATH} \"$@\"\n")
    os.chmod(BIN_PATH, 0o755)
    print("        ✓ Terminal command: killswitch-pro")

    print("""
  ══════════════════════════════════════════════
  ✓  KillSwitch PRO installed successfully!

  HOW TO LAUNCH:
    • Search "KillSwitch PRO" in your app menu
      and click the icon — then right-click to
      Pin / Add to Favourites / Add to Panel
    • Or type:  killswitch-pro  in any terminal

  PANEL FEATURE:
    • Closing the window shrinks it to a
      floating ⚡ button (bottom-right corner)
    • Click to restore · Right-click to quit
  ══════════════════════════════════════════════
""")


def _check_first_run():
    if "--install" in sys.argv:
        _self_install()
        sys.exit(0)


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    _check_first_run()
    app = KillSwitchPro()
    # Show install prompt AFTER main window is ready — no ghost windows
    if not os.path.isfile(DESKTOP_PATH):
        def _prompt_install():
            answer = messagebox.askyesno(
                "⚡ KillSwitch PRO — First Run",
                "Welcome to KillSwitch PRO!\n\n"
                "Would you like to add it to your\n"
                "application menu so you can launch\n"
                "it with a single click next time?\n\n"
                "(You can also run:  python killswitch_pro.py --install)",
                icon="question"
            )
            if answer:
                _self_install()
        app.after(500, _prompt_install)
    app.mainloop()
