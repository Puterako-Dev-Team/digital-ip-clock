import tkinter as tk
import socket
import datetime
import threading
import time
import pickle
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox
from datetime import datetime

def resource_path(filename):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(__file__)
    return os.path.join(base_path, filename)

IP_LIST_FILE = "ip_list.pkl"

# Warna perusahaan
COLOR_RED = "#D9252A"
COLOR_GREEN = "#8CC63F"
COLOR_WHITE = "#FFFFFF"
COLOR_BLACK = "#000000"
COLOR_PASTEL = "#FCB53B"

class NP301SyncTool:
    def __init__(self, root):
        self.root = root
        icon_path = resource_path("assets/favicon.ico")
        if os.path.exists(icon_path):
            self.root.iconbitmap(icon_path)
        self.root.title("Digital IP Clock By Puterako")
        self.root.geometry("1000x550")
        self.root.configure(bg=COLOR_WHITE)
        self.root.resizable(True, True)
        
        # PERBAIKAN 1: Tambah cleanup handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.ip_list = self.load_ip_list()
        self.executor = ThreadPoolExecutor(max_workers=50)

        # ===== Frame Atas: Jam & Trial =====
        top_frame = tk.Frame(root, bg=COLOR_WHITE, height=100)
        top_frame.pack(fill=tk.X, pady=(10,0))
        top_frame.pack_propagate(False)

        self.time_label = tk.Label(top_frame, text="", font=("Consolas", 36, "bold"),
                                   fg=COLOR_BLACK, bg=COLOR_WHITE)
        self.time_label.pack(pady=(10,0), anchor="center", expand=True)
        self.update_clock()

        # ===== Frame Tengah =====
        middle_frame = tk.Frame(root, bg=COLOR_WHITE)
        middle_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=(10,0))

        # --- Left VStack ---
        left_vstack = tk.Frame(middle_frame, bg=COLOR_WHITE, width=500)
        left_vstack.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        left_vstack.pack_propagate(False)

        input_labelframe = tk.LabelFrame(left_vstack, text="Tambah / Hapus Device",
                                         font=("Arial", 10, "bold"), fg=COLOR_BLACK, bg=COLOR_WHITE)
        input_labelframe.pack(fill=tk.X, padx=5, pady=(5,2))

        input_frame = tk.Frame(input_labelframe, bg=COLOR_WHITE)
        input_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Label(input_frame, text="IP Device:", font=("Arial", 12, "bold"),
                 fg=COLOR_GREEN, bg=COLOR_WHITE).pack(side=tk.LEFT)
        self.ip_entry = tk.Entry(input_frame, font=("Arial", 14), width=12, fg=COLOR_BLACK)
        self.ip_entry.pack(side=tk.LEFT, padx=3)

        tk.Label(input_frame, text="Port:", font=("Arial", 12, "bold"),
                 fg=COLOR_GREEN, bg=COLOR_WHITE).pack(side=tk.LEFT)
        self.port_entry = tk.Entry(input_frame, font=("Arial", 14), width=5, fg=COLOR_BLACK)
        self.port_entry.pack(side=tk.LEFT, padx=3)
        self.port_entry.insert(0, str(1001))

        btn_add = tk.Button(input_frame, text="Tambah", command=self.add_ip,
                            bg=COLOR_GREEN, fg="white", width=8, font=("Arial", 10))
        btn_add.pack(side=tk.LEFT, padx=3)

        btn_del = tk.Button(input_frame, text="Hapus", command=self.delete_ip,
                            bg=COLOR_RED, fg="white", width=8, font=("Arial", 10))
        btn_del.pack(side=tk.LEFT, padx=3)

        ip_labelframe = tk.LabelFrame(left_vstack, text="Daftar IP Tersimpan",
                                      font=("Arial", 10, "bold"), fg=COLOR_BLACK, bg=COLOR_WHITE)
        ip_labelframe.pack(fill=tk.X, padx=5, pady=(2,2))

        self.ip_listbox = tk.Listbox(ip_labelframe, font=("Consolas", 11), height=5,
                                     selectmode=tk.SINGLE, bg=COLOR_WHITE, width=30)
        self.ip_listbox.pack(fill=tk.X, padx=5, pady=5)

        log_labelframe = tk.LabelFrame(left_vstack, text="Log Aktivitas",
                                       font=("Arial", 10, "bold"), fg=COLOR_BLACK, bg=COLOR_WHITE)
        log_labelframe.pack(fill=tk.BOTH, padx=5, pady=(2,5), expand=True)

        self.log_text = tk.Text(log_labelframe, height=8, bg=COLOR_WHITE,
                                fg=COLOR_BLACK, font=("Courier", 9), width=40)
        self.log_text.pack(fill=tk.BOTH, padx=5, pady=5, expand=True)

        # --- Right Panel ---
        right_panel = tk.Frame(middle_frame, bg=COLOR_WHITE, width=520)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right_panel.pack_propagate(False)

        status_labelframe = tk.LabelFrame(right_panel, text="Status IP Device",
                                          font=("Arial", 10, "bold"), fg=COLOR_BLACK, bg=COLOR_WHITE)
        status_labelframe.pack(fill=tk.BOTH, padx=5, pady=(5,5), expand=True)

        self.status_frame = tk.Frame(status_labelframe, bg=COLOR_WHITE)
        self.status_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.status_buttons = {}

        # Init data
        self.refresh_ip_listbox()
        self.live_running = False
        self.toggle_live()

    # PERBAIKAN 2: Tambah cleanup method
    def on_closing(self):
        """Cleanup sebelum tutup aplikasi"""
        self.live_running = False
        self.executor.shutdown(wait=False)
        self.root.destroy()

    def load_ip_list(self):
        local_file = os.path.join(os.getcwd(), IP_LIST_FILE)
        if os.path.exists(local_file):
            try:
                with open(local_file, "rb") as f:
                    return pickle.load(f)
            except Exception:
                return ["192.168.2.246"]
        return ["192.168.2.246"]

    def save_ip_list(self):
        with open(IP_LIST_FILE, "wb") as f:
            pickle.dump(self.ip_list, f)

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.time_label.config(text=now)
        self.root.after(1000, self.update_clock)

    def log(self, msg):
        self.root.after(0, lambda: self._append_log(msg))

    def _append_log(self, msg):
        now = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{now}] : {msg}\n")
        lines = self.log_text.get("1.0", tk.END).splitlines()
        if len(lines) > 500:
            self.log_text.delete("1.0", f"{len(lines)-500}.0")
        self.log_text.see(tk.END)

    def refresh_ip_listbox(self):
        self.ip_listbox.delete(0, tk.END)
        for ip in self.ip_list:
            self.ip_listbox.insert(tk.END, ip)
        self.refresh_status_panel()

    def refresh_status_panel(self):
        max_cols = 7
        # Hapus label untuk IP yang sudah tidak ada di list
        ips_to_remove = [ip for ip in self.status_buttons if ip not in self.ip_list]
        for ip in ips_to_remove:
            self.status_buttons[ip].destroy()
            del self.status_buttons[ip]
        
        # Buat atau update posisi label untuk IP yang ada
        for idx, ip in enumerate(self.ip_list):
            if ip not in self.status_buttons:
                short_ip = ip.split('.')[-1]
                lbl = tk.Label(self.status_frame, text=short_ip, width=6, height=2,
                               bg="grey", fg="white", font=("Consolas", 12, "bold"),
                               relief=tk.RIDGE, borderwidth=1)
                self.status_buttons[ip] = lbl
            # Update posisi grid untuk semua label
            self.status_buttons[ip].grid(row=idx // max_cols, column=idx % max_cols, padx=4, pady=4)

    # PERBAIKAN 3: Thread-safe status update
    def set_status(self, ip, status):
        self.root.after(0, lambda: self._set_status_impl(ip, status))

    def _set_status_impl(self, ip, status):
        lbl = self.status_buttons.get(ip)
        if not lbl: return
        short_ip = ip.split('.')[-1]
        if status == "C":
            lbl.config(bg=COLOR_GREEN, text=f"{short_ip} C", fg="white")
        elif status == "T":
            lbl.config(bg=COLOR_PASTEL, text=f"{short_ip} T", fg="white")
        else:
            lbl.config(bg="grey", text=short_ip, fg="white")

    def add_ip(self):
        ip = self.ip_entry.get().strip()
        if not ip:
            self.log("IP kosong.")
            return
        if ip in self.ip_list:
            self.log("IP sudah ada.")
            return
        self.ip_list.append(ip)
        self.save_ip_list()
        self.refresh_ip_listbox()
        self.log(f"IP {ip} ditambahkan.")

    def delete_ip(self):
        selected = self.ip_listbox.curselection()
        if selected:
            ip = self.ip_listbox.get(selected[0])
            self.ip_list.remove(ip)
            self.save_ip_list()
            self.refresh_ip_listbox()
            self.log(f"IP {ip} dihapus.")
        else:
            self.log("Pilih IP yang mau dihapus di list.")

    def get_port(self):
        try:
            return int(self.port_entry.get().strip())
        except ValueError:
            self.log("Port tidak valid, gunakan angka.")
            return 1001

    def build_time_string(self):
        now = datetime.now()
        if now.second % 2 == 0:
            timestr = now.strftime("%H:%M:%S")
        else:
            timestr = now.strftime("%H %M %S")
        return timestr + "\r"

    def send_time_to_ip(self, ip, port, msg):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.3)
                s.connect((ip, port))
                s.sendall(msg.encode("latin1"))
            self.set_status(ip, "C")
        except Exception:
            self.set_status(ip, "T")

    def live_worker(self):
        while datetime.now().microsecond > 100000:
            time.sleep(0.01)
        next_tick = time.time() + 1.0
        try:
            while self.live_running:
                msg = self.build_time_string()
                port = self.get_port()
                for ip in self.ip_list:
                    self.executor.submit(self.send_time_to_ip, ip, port, msg)
                next_tick += 1.0
                sleep_time = next_tick - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    next_tick = time.time() + 1.0
        except Exception as e:
            self.log(f"Live worker error: {e}")

    def toggle_live(self):
        if not self.live_running:
            self.live_running = True
            threading.Thread(target=self.live_worker, daemon=True).start()
            self.log("Live sync dimulai")
        else:
            self.live_running = False
            self.log("Live sync dihentikan")

if __name__ == "__main__":
    root = tk.Tk()
    app = NP301SyncTool(root)
    root.mainloop()