import sys
import os
import socket
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
from PIL import Image, ImageTk
import threading
import configparser
import struct
import hashlib

# -----------------------------------------------------------------
# Enhanced Resource Path Helper with Debug Output
# -----------------------------------------------------------------
def resource_path(relative_path: str) -> str:
    """
    Get the absolute path to a resource.
    When running as a PyInstaller bundled exe, try sys._MEIPASS,
    then fallback to the directory of the executable.
    Otherwise, use the directory of the source file.
    Debug prints the resolved path and whether it exists.
    """
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
        print("DEBUG: Detected sys._MEIPASS =", base_path)
    elif getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
        print("DEBUG: Running frozen; using sys.executable directory =", base_path)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        print("DEBUG: Not frozen; using __file__ directory =", base_path)
    resolved = os.path.join(base_path, relative_path)
    print(f"DEBUG: Resolving '{relative_path}' to '{resolved}' (exists: {os.path.exists(resolved)})")
    return resolved

# -----------------------------------------------------------------
# Protocol Helper Functions
# -----------------------------------------------------------------
def read_line(sock):
    data = b''
    while True:
        chunk = sock.recv(1)
        if not chunk:
            raise ConnectionError("Socket closed unexpectedly.")
        data += chunk
        if chunk == b'\n':
            break
    return data.decode('utf-8').rstrip('\n')

def send_line(sock, text):
    sock.sendall(text.encode('utf-8') + b'\n')

def recv_exact(sock, nbytes):
    data = b''
    while len(data) < nbytes:
        chunk = sock.recv(nbytes - len(data))
        if not chunk:
            raise ConnectionError("Socket closed while reading exact bytes.")
        data += chunk
    return data

def send_int(sock, value):
    sock.sendall(struct.pack('!Q', value))

def recv_int(sock):
    data = recv_exact(sock, 8)
    return struct.unpack('!Q', data)[0]

def send_str(sock, text):
    encoded = text.encode('utf-8')
    send_int(sock, len(encoded))
    sock.sendall(encoded)

def recv_str(sock):
    length = recv_int(sock)
    data = recv_exact(sock, length)
    return data.decode('utf-8')

def calculate_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            sha256.update(chunk)
    return sha256.hexdigest()

def normalize_filename(filename):
    return filename.lower()

# -----------------------------------------------------------------
# Main Client GUI Class
# -----------------------------------------------------------------
class FileClientGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("File Transfer Client")
        self.configure(bg="#F0F0F0")
        self.minsize(500, 350)
        
        self.bg_color = "#F0F0F0"
        self.text_color = "#333333"
        self.button_color = "#4A90E2"
        self.button_hover = "#357ABD"
        
        # Use resource_path() to load icons.
        icon_save_path = resource_path("icons/save.png")
        icon_load_path = resource_path("icons/load.png")
        
        try:
            self.upload_icon = ImageTk.PhotoImage(
                Image.open(icon_save_path).resize((24, 24))
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load upload icon from '{icon_save_path}': {e}")
            self.upload_icon = None

        try:
            self.download_icon = ImageTk.PhotoImage(
                Image.open(icon_load_path).resize((24, 24))
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load download icon from '{icon_load_path}': {e}")
            self.download_icon = None

        # Main frame
        main_frame = tk.Frame(self, bg=self.bg_color)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = tk.Label(
            main_frame, text="File Transfer Client",
            font=("Arial", 18, "bold"),
            bg=self.bg_color, fg=self.text_color
        )
        title_label.pack(pady=(0, 20))

        # Server configuration frame
        config_frame = tk.Frame(main_frame, bg=self.bg_color)
        config_frame.pack(fill="x", pady=10)
        tk.Label(config_frame, text="Server IP:", bg=self.bg_color, fg=self.text_color).grid(row=0, column=0, padx=5, pady=5)
        self.entry_server_ip = tk.Entry(config_frame)
        self.entry_server_ip.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        tk.Label(config_frame, text="Port:", bg=self.bg_color, fg=self.text_color).grid(row=1, column=0, padx=5, pady=5)
        self.entry_port = tk.Entry(config_frame)
        self.entry_port.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        config_frame.grid_columnconfigure(1, weight=1)

        # Buttons frame
        buttons_frame = tk.Frame(main_frame, bg=self.bg_color)
        buttons_frame.pack(pady=10)
        def on_enter(e): e.widget["background"] = self.button_hover
        def on_leave(e): e.widget["background"] = self.button_color

        self.upload_btn = tk.Button(
            buttons_frame, text="Upload Files", image=self.upload_icon, compound="left",
            bg=self.button_color, fg="white", font=("Arial", 12), padx=10, pady=5, relief="flat",
            command=self.upload_button_clicked
        )
        self.upload_btn.pack(side="left", padx=10)
        self.upload_btn.bind("<Enter>", on_enter)
        self.upload_btn.bind("<Leave>", on_leave)

        self.download_btn = tk.Button(
            buttons_frame, text="Download File", image=self.download_icon, compound="left",
            bg=self.button_color, fg="white", font=("Arial", 12), padx=10, pady=5, relief="flat",
            command=self.download_button_clicked
        )
        self.download_btn.pack(side="left", padx=10)
        self.download_btn.bind("<Enter>", on_enter)
        self.download_btn.bind("<Leave>", on_leave)

        # Progress and status frame
        status_frame = tk.Frame(main_frame, bg=self.bg_color)
        status_frame.pack(fill="x", pady=10)
        self.progress_bar = ttk.Progressbar(status_frame, orient="horizontal", mode="determinate", length=300)
        self.progress_bar.pack(pady=5)
        self.status_label = tk.Label(
            status_frame, text="Status: Idle", bg=self.bg_color, fg=self.text_color,
            font=("Arial", 10)
        )
        self.status_label.pack()

        # Load configuration (using resource_path for config.ini if bundled)
        config = configparser.ConfigParser()
        try:
            config.read(resource_path("config.ini"))
        except Exception:
            config.read("config.ini")
        self.entry_server_ip.insert(0, config.get('client', 'server_ip', fallback='127.0.0.1'))
        self.entry_port.insert(0, config.get('client', 'port', fallback='5000'))

    # ------------------------
    # Upload Logic
    # ------------------------
    def upload_file(self, server_ip, port, file_path):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((server_ip, port))
            send_line(sock, "UPLOAD")
            file_name = normalize_filename(os.path.basename(file_path))
            send_str(sock, file_name)
            response = read_line(sock)
            if response == "FILE_EXISTS":
                raise Exception(f"File '{file_name}' already exists on server.")
            elif response == "PROCEED":
                file_size = os.path.getsize(file_path)
                send_int(sock, file_size)
                chksum = calculate_checksum(file_path)
                send_str(sock, chksum)
                with open(file_path, 'rb') as f:
                    sent = 0
                    while sent < file_size:
                        chunk = f.read(min(4096, file_size - sent))
                        if not chunk:
                            break
                        sock.sendall(chunk)
                        sent += len(chunk)
                        self.progress_bar['value'] = (sent / file_size) * 100
                        self.update_idletasks()
                final_response = read_line(sock)
                if final_response != "SUCCESS":
                    raise Exception(f"Upload of '{file_name}' failed on server.")
            else:
                raise Exception(f"Unexpected server response: {response}")
        finally:
            sock.close()

    def upload_files_thread(self, server_ip, port, file_paths):
        self.upload_btn.config(state="disabled")
        self.download_btn.config(state="disabled")
        self.status_label.config(text="Status: Uploading...")
        for file_path in file_paths:
            try:
                self.upload_file(server_ip, port, file_path)
                messagebox.showinfo("Upload", f"Uploaded {os.path.basename(file_path)} successfully.")
            except Exception as e:
                messagebox.showerror("Upload", str(e))
        self.status_label.config(text="Status: Idle")
        self.progress_bar['value'] = 0
        self.upload_btn.config(state="normal")
        self.download_btn.config(state="normal")

    def upload_button_clicked(self):
        server_ip = self.entry_server_ip.get()
        port = int(self.entry_port.get())
        file_paths = filedialog.askopenfilenames()
        if file_paths:
            threading.Thread(
                target=self.upload_files_thread,
                args=(server_ip, port, file_paths),
                daemon=True
            ).start()

    # ------------------------
    # Download Logic
    # ------------------------
    def download_file(self, server_ip, port, base_name, download_dir):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((server_ip, port))
            send_line(sock, "DOWNLOAD")
            base_name = normalize_filename(base_name)
            send_str(sock, base_name)
            response = read_line(sock)
            if response == "FILE_NOT_FOUND":
                raise Exception(f"No file found for base name '{base_name}'.")
            elif response == "MULTIPLE_FILES":
                raise Exception(f"Multiple files match base name '{base_name}'. Please be more specific.")
            elif response == "FILE_FOUND":
                actual_file_name = recv_str(sock)
                file_size = recv_int(sock)
                chksum = recv_str(sock)
                file_path = os.path.join(download_dir, actual_file_name)
                if os.path.exists(file_path):
                    if not messagebox.askyesno("Overwrite", f"'{actual_file_name}' already exists. Overwrite?"):
                        raise Exception("Download cancelled by user.")
                with open(file_path, 'wb') as f:
                    received = 0
                    while received < file_size:
                        chunk = sock.recv(min(4096, file_size - received))
                        if not chunk:
                            break
                        f.write(chunk)
                        received += len(chunk)
                        self.progress_bar['value'] = (received / file_size) * 100
                        self.update_idletasks()
                if calculate_checksum(file_path) != chksum:
                    send_line(sock, "FAILURE")
                    raise Exception("Checksum mismatch. The downloaded file is corrupted.")
                else:
                    send_line(sock, "SUCCESS")
            else:
                raise Exception(f"Unexpected server response: {response}")
        finally:
            sock.close()

    def download_file_thread(self, server_ip, port, base_name, download_dir):
        self.upload_btn.config(state="disabled")
        self.download_btn.config(state="disabled")
        self.status_label.config(text="Status: Downloading...")
        try:
            self.download_file(server_ip, port, base_name, download_dir)
            messagebox.showinfo("Download", f"Downloaded file(s) starting with '{base_name}' successfully.")
        except Exception as e:
            messagebox.showerror("Download", str(e))
        self.status_label.config(text="Status: Idle")
        self.progress_bar['value'] = 0
        self.upload_btn.config(state="normal")
        self.download_btn.config(state="normal")

    def download_button_clicked(self):
        server_ip = self.entry_server_ip.get()
        port = int(self.entry_port.get())
        base_name = simpledialog.askstring("Download", "Enter the base filename (no extension):")
        if base_name:
            download_dir = './downloads'
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
            threading.Thread(
                target=self.download_file_thread,
                args=(server_ip, port, base_name, download_dir),
                daemon=True
            ).start()

if __name__ == "__main__":
    app = FileClientGUI()
    app.mainloop()
