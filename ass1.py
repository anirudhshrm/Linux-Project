#!/usr/bin/env python3
import os
import sys
import time
import psutil
import platform
import calendar
import subprocess
import threading
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, font
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class LinuxSystemAssistant(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Linux System Assistant")
        self.geometry("1000x700")
        self.minsize(800, 600)
        
        # Set color scheme
        self.bg_color = "#f0f0f0"
        self.frame_bg = "#ffffff"
        self.highlight_color = "#4a86e8"
        self.text_color = "#333333"
        self.success_color = "#28a745"
        self.warning_color = "#ffc107"
        self.danger_color = "#dc3545"
        
        # Configure styles
        self.configure_styles()
        
        # Initialize variables
        self.cpu_usage_history = [0] * 60  # Store 60 data points for history
        self.memory_usage_history = [0] * 60
        self.update_interval = 1000  # Update interval in milliseconds
        
        # Create UI elements
        self.create_ui()
        
        # Start periodic updates
        self.update_system_info()
    
    def configure_styles(self):
        """Configure ttk styles for the application."""
        self.style = ttk.Style()
        
        # Configure the notebook style
        self.style.configure("TNotebook", background=self.bg_color)
        self.style.configure("TNotebook.Tab", padding=[10, 5], font=('Helvetica', 10))
        self.style.map("TNotebook.Tab", background=[("selected", self.highlight_color)], 
                      foreground=[("selected", "#ffffff")])
        
        # Configure the frame style
        self.style.configure("Card.TFrame", background=self.frame_bg, relief="raised")
        
        # Configure the label style
        self.style.configure("TLabel", background=self.frame_bg, foreground=self.text_color)
        self.style.configure("Title.TLabel", font=('Helvetica', 16, 'bold'), background=self.frame_bg)
        self.style.configure("Header.TLabel", font=('Helvetica', 14, 'bold'), background=self.frame_bg)
        self.style.configure("Info.TLabel", font=('Helvetica', 10), background=self.frame_bg)
        
        # Configure the button style
        self.style.configure("TButton", font=('Helvetica', 10), padding=5)
        self.style.configure("Primary.TButton", background=self.highlight_color)
        
        # Configure the progressbar style
        self.style.configure("TProgressbar", thickness=20, background=self.highlight_color)
    
    def create_ui(self):
        """Create the main UI elements."""
        # Create main container
        self.main_container = ttk.Frame(self, padding=10)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(self.main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create tabs
        self.dashboard_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.system_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.disk_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.calendar_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        self.maintenance_frame = ttk.Frame(self.notebook, style="Card.TFrame")
        
        # Add tabs to notebook
        self.notebook.add(self.dashboard_frame, text="Dashboard")
        self.notebook.add(self.system_frame, text="System Info")
        self.notebook.add(self.disk_frame, text="Disk Info")
        self.notebook.add(self.calendar_frame, text="Calendar")
        self.notebook.add(self.maintenance_frame, text="Maintenance")
        
        # Initialize all tabs
        self.init_dashboard_tab()
        self.init_system_tab()
        self.init_disk_tab()
        self.init_calendar_tab()
        self.init_maintenance_tab()
    
    def init_dashboard_tab(self):
        """Initialize the dashboard tab."""
        # Create a canvas with scrollbar
        self.dashboard_canvas = tk.Canvas(self.dashboard_frame, bg=self.frame_bg)
        scrollbar = ttk.Scrollbar(self.dashboard_frame, orient="vertical", command=self.dashboard_canvas.yview)
        self.dashboard_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dashboard_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas
        self.dashboard_content = ttk.Frame(self.dashboard_canvas, style="Card.TFrame")
        self.dashboard_canvas.create_window((0, 0), window=self.dashboard_content, anchor="nw")
        
        # Configure the canvas to resize with the window
        self.dashboard_content.bind("<Configure>", lambda e: self.dashboard_canvas.configure(
            scrollregion=self.dashboard_canvas.bbox("all"),
            width=e.width
        ))
        
        # Title
        title_label = ttk.Label(self.dashboard_content, text="System Dashboard", style="Title.TLabel")
        title_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="w")
        
        # Top row: CPU and Memory
        self.cpu_frame = ttk.LabelFrame(self.dashboard_content, text="CPU Usage", padding=10)
        self.cpu_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.memory_frame = ttk.LabelFrame(self.dashboard_content, text="Memory Usage", padding=10)
        self.memory_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        
        # CPU Usage components
        self.cpu_progress = ttk.Progressbar(self.cpu_frame, orient="horizontal", mode="determinate", 
                                           style="TProgressbar", length=300)
        self.cpu_progress.pack(pady=(10, 5), fill="x")
        
        self.cpu_percent_label = ttk.Label(self.cpu_frame, text="0%", style="Info.TLabel")
        self.cpu_percent_label.pack(pady=5)
        
        # CPU Chart
        self.cpu_figure = plt.Figure(figsize=(5, 2), dpi=100)
        self.cpu_plot = self.cpu_figure.add_subplot(111)
        self.cpu_plot.set_ylim(0, 100)
        self.cpu_plot.set_title('CPU Usage History')
        self.cpu_plot.set_ylabel('Usage %')
        self.cpu_plot.grid(True)
        
        self.cpu_line, = self.cpu_plot.plot(range(60), self.cpu_usage_history, 'b-')
        
        self.cpu_canvas = FigureCanvasTkAgg(self.cpu_figure, self.cpu_frame)
        self.cpu_canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)
        
        # Memory Usage components
        self.memory_progress = ttk.Progressbar(self.memory_frame, orient="horizontal", mode="determinate", 
                                              style="TProgressbar", length=300)
        self.memory_progress.pack(pady=(10, 5), fill="x")
        
        self.memory_info_label = ttk.Label(self.memory_frame, text="0 / 0 GB (0%)", style="Info.TLabel")
        self.memory_info_label.pack(pady=5)
        
        # Memory Chart
        self.memory_figure = plt.Figure(figsize=(5, 2), dpi=100)
        self.memory_plot = self.memory_figure.add_subplot(111)
        self.memory_plot.set_ylim(0, 100)
        self.memory_plot.set_title('Memory Usage History')
        self.memory_plot.set_ylabel('Usage %')
        self.memory_plot.grid(True)
        
        self.memory_line, = self.memory_plot.plot(range(60), self.memory_usage_history, 'r-')
        
        self.memory_canvas = FigureCanvasTkAgg(self.memory_figure, self.memory_frame)
        self.memory_canvas.get_tk_widget().pack(pady=10, fill="both", expand=True)
        
        # Bottom row: System Overview and Disk Overview
        self.system_overview_frame = ttk.LabelFrame(self.dashboard_content, text="System Overview", padding=10)
        self.system_overview_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")
        
        self.disk_overview_frame = ttk.LabelFrame(self.dashboard_content, text="Disk Overview", padding=10)
        self.disk_overview_frame.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        
        # System Overview components
        self.system_info_text = tk.Text(self.system_overview_frame, height=10, width=40, wrap=tk.WORD, 
                                       bg=self.frame_bg, fg=self.text_color)
        self.system_info_text.pack(pady=10, fill="both", expand=True)
        
        # Disk Overview components
        self.disk_info_text = tk.Text(self.disk_overview_frame, height=10, width=40, wrap=tk.WORD, 
                                     bg=self.frame_bg, fg=self.text_color)
        self.disk_info_text.pack(pady=10, fill="both", expand=True)
        
        # Configure grid weights
        self.dashboard_content.grid_columnconfigure(0, weight=1)
        self.dashboard_content.grid_columnconfigure(1, weight=1)
        self.dashboard_content.grid_rowconfigure(1, weight=1)
        self.dashboard_content.grid_rowconfigure(2, weight=1)
    
    def init_system_tab(self):
        """Initialize the system information tab."""
        # Create a canvas with scrollbar
        self.system_canvas = tk.Canvas(self.system_frame, bg=self.frame_bg)
        scrollbar = ttk.Scrollbar(self.system_frame, orient="vertical", command=self.system_canvas.yview)
        self.system_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.system_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas
        self.system_content = ttk.Frame(self.system_canvas, style="Card.TFrame")
        self.system_canvas.create_window((0, 0), window=self.system_content, anchor="nw")
        
        # Configure the canvas to resize with the window
        self.system_content.bind("<Configure>", lambda e: self.system_canvas.configure(
            scrollregion=self.system_canvas.bbox("all"),
            width=e.width
        ))
        
        # Title
        title_label = ttk.Label(self.system_content, text="System Information", style="Title.TLabel")
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # System Information Frame
        system_info_frame = ttk.LabelFrame(self.system_content, text="System Details", padding=10)
        system_info_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Labels for system information
        labels = ["OS", "Hostname", "Kernel", "Architecture", "Processor", "Uptime", "Boot Time"]
        self.system_info_labels = {}
        self.system_info_values = {}
        
        for i, label in enumerate(labels):
            self.system_info_labels[label] = ttk.Label(system_info_frame, text=f"{label}:", 
                                                      font=('Helvetica', 10, 'bold'))
            self.system_info_labels[label].grid(row=i, column=0, padx=20, pady=10, sticky="w")
            
            self.system_info_values[label] = ttk.Label(system_info_frame, text="Loading...")
            self.system_info_values[label].grid(row=i, column=1, padx=20, pady=10, sticky="w")
        
        # CPU Information Title
        cpu_title_label = ttk.Label(self.system_content, text="CPU Information", style="Title.TLabel")
        cpu_title_label.grid(row=2, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # CPU Information Frame
        cpu_info_frame = ttk.LabelFrame(self.system_content, text="CPU Details", padding=10)
        cpu_info_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        # Labels for CPU information
        cpu_labels = ["Physical Cores", "Logical Cores", "Max Frequency", "Current Frequency", "CPU Usage"]
        self.cpu_info_labels = {}
        self.cpu_info_values = {}
        
        for i, label in enumerate(cpu_labels):
            self.cpu_info_labels[label] = ttk.Label(cpu_info_frame, text=f"{label}:", 
                                                   font=('Helvetica', 10, 'bold'))
            self.cpu_info_labels[label].grid(row=i, column=0, padx=20, pady=10, sticky="w")
            
            self.cpu_info_values[label] = ttk.Label(cpu_info_frame, text="Loading...")
            self.cpu_info_values[label].grid(row=i, column=1, padx=20, pady=10, sticky="w")
        
        # Configure grid weights
        self.system_content.grid_columnconfigure(0, weight=1)
        system_info_frame.grid_columnconfigure(1, weight=1)
        cpu_info_frame.grid_columnconfigure(1, weight=1)
    
    def init_disk_tab(self):
        """Initialize the disk information tab."""
        # Create a canvas with scrollbar
        self.disk_canvas = tk.Canvas(self.disk_frame, bg=self.frame_bg)
        scrollbar = ttk.Scrollbar(self.disk_frame, orient="vertical", command=self.disk_canvas.yview)
        self.disk_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.disk_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas
        self.disk_content = ttk.Frame(self.disk_canvas, style="Card.TFrame")
        self.disk_canvas.create_window((0, 0), window=self.disk_content, anchor="nw")
        
        # Configure the canvas to resize with the window
        self.disk_content.bind("<Configure>", lambda e: self.disk_canvas.configure(
            scrollregion=self.disk_canvas.bbox("all"),
            width=e.width
        ))
        
        # Title
        title_label = ttk.Label(self.disk_content, text="Disk Information", style="Title.TLabel")
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Disk Table Frame
        disk_table_frame = ttk.LabelFrame(self.disk_content, text="Mounted Partitions", padding=10)
        disk_table_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Create Treeview for disk information
        self.disk_tree = ttk.Treeview(disk_table_frame, columns=("device", "mountpoint", "fstype", "total", "used", "free", "percent"))
        
        # Define column headings
        self.disk_tree.heading("#0", text="")
        self.disk_tree.heading("device", text="Device")
        self.disk_tree.heading("mountpoint", text="Mount Point")
        self.disk_tree.heading("fstype", text="Type")
        self.disk_tree.heading("total", text="Total")
        self.disk_tree.heading("used", text="Used")
        self.disk_tree.heading("free", text="Free")
        self.disk_tree.heading("percent", text="Usage")
        
        # Define column widths
        self.disk_tree.column("#0", width=0, stretch=tk.NO)
        self.disk_tree.column("device", width=100)
        self.disk_tree.column("mountpoint", width=150)
        self.disk_tree.column("fstype", width=80)
        self.disk_tree.column("total", width=100)
        self.disk_tree.column("used", width=100)
        self.disk_tree.column("free", width=100)
        self.disk_tree.column("percent", width=80)
        
        # Add scrollbar
        disk_tree_scrollbar = ttk.Scrollbar(disk_table_frame, orient="vertical", command=self.disk_tree.yview)
        self.disk_tree.configure(yscrollcommand=disk_tree_scrollbar.set)
        
        # Pack the treeview and scrollbar
        disk_tree_scrollbar.pack(side="right", fill="y")
        self.disk_tree.pack(expand=True, fill="both", padx=10, pady=10)
        
        # Disk Usage Visualization Title
        viz_title_label = ttk.Label(self.disk_content, text="Disk Usage Visualization", style="Title.TLabel")
        viz_title_label.grid(row=2, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Frame for disk usage visualization
        self.disk_viz_frame = ttk.LabelFrame(self.disk_content, text="Usage Bars", padding=10)
        self.disk_viz_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        # Configure grid weights
        self.disk_content.grid_columnconfigure(0, weight=1)
        self.disk_content.grid_rowconfigure(1, weight=1)
        self.disk_content.grid_rowconfigure(3, weight=1)
    
    def init_calendar_tab(self):
        """Initialize the calendar tab."""
        # Create a canvas with scrollbar
        self.calendar_canvas = tk.Canvas(self.calendar_frame, bg=self.frame_bg)
        scrollbar = ttk.Scrollbar(self.calendar_frame, orient="vertical", command=self.calendar_canvas.yview)
        self.calendar_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.calendar_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas
        self.calendar_content = ttk.Frame(self.calendar_canvas, style="Card.TFrame")
        self.calendar_canvas.create_window((0, 0), window=self.calendar_content, anchor="nw")
        
        # Configure the canvas to resize with the window
        self.calendar_content.bind("<Configure>", lambda e: self.calendar_canvas.configure(
            scrollregion=self.calendar_canvas.bbox("all"),
            width=e.width
        ))
        
        # Title
        title_label = ttk.Label(self.calendar_content, text="Calendar", style="Title.TLabel")
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # Calendar Frame
        calendar_frame = ttk.LabelFrame(self.calendar_content, text="Monthly Calendar", padding=10)
        calendar_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        # Date Navigation
        nav_frame = ttk.Frame(calendar_frame)
        nav_frame.pack(fill="x", padx=10, pady=10)
        
        self.prev_month_btn = ttk.Button(nav_frame, text="< Previous", command=self.prev_month)
        self.prev_month_btn.pack(side="left", padx=10)
        
        self.current_month_label = ttk.Label(nav_frame, text="", font=('Helvetica', 12, 'bold'))
        self.current_month_label.pack(side="left", padx=20)
        
        self.next_month_btn = ttk.Button(nav_frame, text="Next >", command=self.next_month)
        self.next_month_btn.pack(side="left", padx=10)
        
        # Calendar display
        self.calendar_display = tk.Text(calendar_frame, height=15, width=50, font=("Courier", 14), 
                                       bg=self.frame_bg, fg=self.text_color)
        self.calendar_display.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Initialize with current month
        self.current_year = datetime.now().year
        self.current_month = datetime.now().month
        self.update_calendar()
        
        # Configure grid weights
        self.calendar_content.grid_columnconfigure(0, weight=1)
        self.calendar_content.grid_rowconfigure(1, weight=1)
    
    def init_maintenance_tab(self):
        """Initialize the maintenance tab."""
        # Create a canvas with scrollbar
        self.maintenance_canvas = tk.Canvas(self.maintenance_frame, bg=self.frame_bg)
        scrollbar = ttk.Scrollbar(self.maintenance_frame, orient="vertical", command=self.maintenance_canvas.yview)
        self.maintenance_canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.maintenance_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Create a frame inside the canvas
        self.maintenance_content = ttk.Frame(self.maintenance_canvas, style="Card.TFrame")
        self.maintenance_canvas.create_window((0, 0), window=self.maintenance_content, anchor="nw")
        
        # Configure the canvas to resize with the window
        self.maintenance_content.bind("<Configure>", lambda e: self.maintenance_canvas.configure(
            scrollregion=self.maintenance_canvas.bbox("all"),
            width=e.width
        ))
        
        # Title
        title_label = ttk.Label(self.maintenance_content, text="System Maintenance", style="Title.TLabel")
        title_label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")
        
        # System Update Frame
        update_frame = ttk.LabelFrame(self.maintenance_content, text="System Update", padding=10)
        update_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        
        update_desc = ttk.Label(update_frame, text="Update package lists and upgrade installed packages.")
        update_desc.pack(anchor="w", padx=10, pady=10)
        
        self.update_button = ttk.Button(update_frame, text="Run System Update", command=self.run_system_update)
        self.update_button.pack(padx=10, pady=10)
        
        # System Cleanup Frame
        cleanup_frame = ttk.LabelFrame(self.maintenance_content, text="System Cleanup", padding=10)
        cleanup_frame.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        
        cleanup_desc = ttk.Label(cleanup_frame, text="Clean apt cache, remove unused packages, and clean temporary files.")
        cleanup_desc.pack(anchor="w", padx=10, pady=10)
        
        self.cleanup_button = ttk.Button(cleanup_frame, text="Run System Cleanup", command=self.run_system_cleanup)
        self.cleanup_button.pack(padx=10, pady=10)
        
        # Output Log Frame
        log_frame = ttk.LabelFrame(self.maintenance_content, text="Operation Log", padding=10)
        log_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        
        self.log_text = tk.Text(log_frame, height=15, width=80, wrap=tk.WORD, bg="black", fg="white")
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        log_scrollbar.pack(side="right", fill="y")
        self.log_text.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Configure grid weights
        self.maintenance_content.grid_columnconfigure(0, weight=1)
        self.maintenance_content.grid_rowconfigure(3, weight=1)
    
    def format_bytes(self, bytes_value):
        """Format bytes to human-readable format."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def get_system_info(self):
        """Get basic system information."""
        uname = platform.uname()
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime_seconds = time.time() - psutil.boot_time()
        days = int(uptime_seconds // (24 * 3600))
        hours = int((uptime_seconds % (24 * 3600)) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        return {
            "system": uname.system,
            "node": uname.node,
            "release": uname.release,
            "version": uname.version,
            "machine": uname.machine,
            "processor": uname.processor or "Unknown",
            "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
            "uptime": f"{days}d {hours}h {minutes}m"
        }
    
    def get_cpu_info(self):
        """Get CPU information."""
        cpu_percent = psutil.cpu_percent(interval=0.1)
        cpu_freq = psutil.cpu_freq()
        
        return {
            "physical_cores": psutil.cpu_count(logical=False),
            "logical_cores": psutil.cpu_count(logical=True),
            "max_freq": f"{cpu_freq.max:.2f} MHz" if cpu_freq and cpu_freq.max else "Unknown",
            "current_freq": f"{cpu_freq.current:.2f} MHz" if cpu_freq and cpu_freq.current else "Unknown",
            "percent": cpu_percent
        }
    
    def get_memory_info(self):
        """Get memory information."""
        memory = psutil.virtual_memory()
        
        return {
            "total": memory.total,
            "available": memory.available,
            "percent": memory.percent,
            "used": memory.used,
            "free": memory.free
        }
    
    def get_disk_info(self):
        """Get disk information."""
        partitions = []
        for partition in psutil.disk_partitions():
            if os.name == 'nt' and ('cdrom' in partition.opts or partition.fstype == ''):
                continue
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                partitions.append({
                    "device": partition.device,
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent
                })
            except PermissionError:
                continue
        
        return partitions
    
    def update_system_info(self):
        """Update all system information."""
        # Update CPU and memory history
        cpu_info = self.get_cpu_info()
        memory_info = self.get_memory_info()
        
        self.cpu_usage_history.pop(0)
        self.cpu_usage_history.append(cpu_info["percent"])
        
        self.memory_usage_history.pop(0)
        self.memory_usage_history.append(memory_info["percent"])
        
        # Update dashboard
        self.update_dashboard()
        
        # Update system info page if visible
        if self.notebook.index(self.notebook.select()) == 1:  # System Info tab
            self.update_system_page()
        
        # Update disk info page if visible
        if self.notebook.index(self.notebook.select()) == 2:  # Disk Info tab
            self.update_disk_info()
        
        # Schedule next update
        self.after(self.update_interval, self.update_system_info)
    
    def update_dashboard(self):
        """Update dashboard information."""
        # Update CPU card
        cpu_info = self.get_cpu_info()
        self.cpu_progress["value"] = cpu_info["percent"]
        self.cpu_percent_label.config(text=f"{cpu_info['percent']:.1f}%")
        
        # Update CPU chart
        self.cpu_line.set_ydata(self.cpu_usage_history)
        self.cpu_figure.canvas.draw_idle()
        
        # Update Memory card
        memory_info = self.get_memory_info()
        self.memory_progress["value"] = memory_info["percent"]
        total_gb = memory_info["total"] / (1024 ** 3)
        used_gb = memory_info["used"] / (1024 ** 3)
        self.memory_info_label.config(text=f"{used_gb:.1f} / {total_gb:.1f} GB ({memory_info['percent']:.1f}%)")
        
        # Update Memory chart
        self.memory_line.set_ydata(self.memory_usage_history)
        self.memory_figure.canvas.draw_idle()
        
        # Update System Overview
        system_info = self.get_system_info()
        
        self.system_info_text.config(state=tk.NORMAL)
        self.system_info_text.delete("1.0", tk.END)
        self.system_info_text.insert("1.0", f"OS: {system_info['system']}\n")
        self.system_info_text.insert(tk.END, f"Hostname: {system_info['node']}\n")
        self.system_info_text.insert(tk.END, f"Kernel: {system_info['release']}\n")
        self.system_info_text.insert(tk.END, f"Architecture: {system_info['machine']}\n")
        self.system_info_text.insert(tk.END, f"Uptime: {system_info['uptime']}\n")
        self.system_info_text.insert(tk.END, f"Boot Time: {system_info['boot_time']}")
        self.system_info_text.config(state=tk.DISABLED)
        
        # Update Disk Overview
        disk_info = self.get_disk_info()
        
        self.disk_info_text.config(state=tk.NORMAL)
        self.disk_info_text.delete("1.0", tk.END)
        
        for partition in disk_info:
            total = self.format_bytes(partition["total"])
            used = self.format_bytes(partition["used"])
            free = self.format_bytes(partition["free"])
            self.disk_info_text.insert(tk.END, f"Device: {partition['device']}\n")
            self.disk_info_text.insert(tk.END, f"Mount: {partition['mountpoint']}\n")
            self.disk_info_text.insert(tk.END, f"Usage: {used} / {total} ({partition['percent']}%)\n\n")
        
        self.disk_info_text.config(state=tk.DISABLED)
    
    def update_system_page(self):
        """Update system information page."""
        system_info = self.get_system_info()
        cpu_info = self.get_cpu_info()
        
        # Update system info values
        self.system_info_values["OS"].config(text=system_info["system"])
        self.system_info_values["Hostname"].config(text=system_info["node"])
        self.system_info_values["Kernel"].config(text=system_info["release"])
        self.system_info_values["Architecture"].config(text=system_info["machine"])
        self.system_info_values["Processor"].config(text=system_info["processor"])
        self.system_info_values["Uptime"].config(text=system_info["uptime"])
        self.system_info_values["Boot Time"].config(text=system_info["boot_time"])
        
        # Update CPU info values
        self.cpu_info_values["Physical Cores"].config(text=str(cpu_info["physical_cores"]))
        self.cpu_info_values["Logical Cores"].config(text=str(cpu_info["logical_cores"]))
        self.cpu_info_values["Max Frequency"].config(text=cpu_info["max_freq"])
        self.cpu_info_values["Current Frequency"].config(text=cpu_info["current_freq"])
        self.cpu_info_values["CPU Usage"].config(text=f"{cpu_info['percent']}%")
    
    def update_disk_info(self):
        """Update disk information page."""
        disk_info = self.get_disk_info()
        
        # Clear existing items
        for item in self.disk_tree.get_children():
            self.disk_tree.delete(item)
        
        # Add new items
        for partition in disk_info:
            self.disk_tree.insert("", "end", values=(
                partition["device"],
                partition["mountpoint"],
                partition["fstype"],
                self.format_bytes(partition["total"]),
                self.format_bytes(partition["used"]),
                self.format_bytes(partition["free"]),
                f"{partition['percent']}%"
            ))
        
        # Update disk visualization
        # Clear existing widgets
        for widget in self.disk_viz_frame.winfo_children():
            widget.destroy()
        
        # Create progress bars for each partition
        for i, partition in enumerate(disk_info):
            frame = ttk.Frame(self.disk_viz_frame, padding=5)
            frame.pack(fill="x", padx=10, pady=5)
            
            label = ttk.Label(frame, text=f"{partition['mountpoint']} ({partition['device']})")
            label.pack(anchor="w", padx=5, pady=2)
            
            progress = ttk.Progressbar(frame, orient="horizontal", length=400, mode="determinate")
            progress.pack(fill="x", padx=5, pady=2)
            progress["value"] = partition["percent"]
            
            info_label = ttk.Label(frame, text=f"{self.format_bytes(partition['used'])} / {self.format_bytes(partition['total'])} ({partition['percent']}%)")
            info_label.pack(anchor="e", padx=5, pady=2)
    
    def update_calendar(self):
        """Update calendar display."""
        # Update month label
        month_name = calendar.month_name[self.current_month]
        self.current_month_label.config(text=f"{month_name} {self.current_year}")
        
        # Get calendar text
        cal_text = calendar.month(self.current_year, self.current_month)
        
        # Update calendar display
        self.calendar_display.config(state=tk.NORMAL)
        self.calendar_display.delete("1.0", tk.END)
        self.calendar_display.insert("1.0", cal_text)
        self.calendar_display.config(state=tk.DISABLED)
    
    def prev_month(self):
        """Go to previous month."""
        self.current_month -= 1
        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1
        self.update_calendar()
    
    def next_month(self):
        """Go to next month."""
        self.current_month += 1
        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1
        self.update_calendar()
    
    def run_system_update(self):
        """Run system update commands."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert("1.0", "Starting system update...\n")
        self.log_text.config(state=tk.DISABLED)
        
        # Disable buttons during operation
        self.update_button.config(state=tk.DISABLED)
        self.cleanup_button.config(state=tk.DISABLED)
        
        # Run update in a separate thread
        threading.Thread(target=self._run_system_update_thread, daemon=True).start()
    
    def _run_system_update_thread(self):
        """Thread function for system update."""
        try:
            # Check if we're running as root
            if os.geteuid() != 0:
                self.log_append("This operation requires root privileges. Please run with sudo.")
                messagebox.showerror("Permission Error", "This operation requires root privileges. Please run with sudo.")
                self.update_button.config(state=tk.NORMAL)
                self.cleanup_button.config(state=tk.NORMAL)
                return
            
            # Update package lists
            self.log_append("Updating package lists...")
            process = subprocess.Popen(["apt", "update"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_append(output.strip())
            
            if process.returncode != 0:
                self.log_append("Error updating package lists.")
                messagebox.showerror("Update Error", "Error updating package lists.")
                self.update_button.config(state=tk.NORMAL)
                self.cleanup_button.config(state=tk.NORMAL)
                return
            
            # Upgrade packages
            self.log_append("\nUpgrading packages...")
            process = subprocess.Popen(["apt", "upgrade", "-y"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_append(output.strip())
            
            if process.returncode != 0:
                self.log_append("Error upgrading packages.")
                messagebox.showerror("Update Error", "Error upgrading packages.")
            else:
                self.log_append("\nSystem update completed successfully!")
                messagebox.showinfo("Update Complete", "System update completed successfully!")
        
        except Exception as e:
            self.log_append(f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
        
        finally:
            # Re-enable buttons
            self.update_button.config(state=tk.NORMAL)
            self.cleanup_button.config(state=tk.NORMAL)
    
    def run_system_cleanup(self):
        """Run system cleanup commands."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.insert("1.0", "Starting system cleanup...\n")
        self.log_text.config(state=tk.DISABLED)
        
        # Disable buttons during operation
        self.update_button.config(state=tk.DISABLED)
        self.cleanup_button.config(state=tk.DISABLED)
        
        # Run cleanup in a separate thread
        threading.Thread(target=self._run_system_cleanup_thread, daemon=True).start()
    
    def _run_system_cleanup_thread(self):
        """Thread function for system cleanup."""
        try:
            # Check if we're running as root
            if os.geteuid() != 0:
                self.log_append("This operation requires root privileges. Please run with sudo.")
                messagebox.showerror("Permission Error", "This operation requires root privileges. Please run with sudo.")
                self.update_button.config(state=tk.NORMAL)
                self.cleanup_button.config(state=tk.NORMAL)
                return
            
            # Clean apt cache
            self.log_append("Cleaning apt cache...")
            process = subprocess.Popen(["apt", "clean"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_append(output.strip())
            
            # Remove unused packages
            self.log_append("\nRemoving unused packages...")
            process = subprocess.Popen(["apt", "autoremove", "-y"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.log_append(output.strip())
            
            # Clean temporary files
            self.log_append("\nCleaning temporary files...")
            try:
                subprocess.run(["rm", "-rf", "/tmp/*"], check=True)
                self.log_append("Temporary files cleaned.")
            except subprocess.CalledProcessError:
                self.log_append("Error cleaning temporary files.")
            
            self.log_append("\nSystem cleanup completed successfully!")
            messagebox.showinfo("Cleanup Complete", "System cleanup completed successfully!")
        
        except Exception as e:
            self.log_append(f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
        
        finally:
            # Re-enable buttons
            self.update_button.config(state=tk.NORMAL)
            self.cleanup_button.config(state=tk.NORMAL)
    
    def log_append(self, text):
        """Append text to log and scroll to end."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        # Update the UI
        self.update_idletasks()

if __name__ == "__main__":
    app = LinuxSystemAssistant()
    app.mainloop()
