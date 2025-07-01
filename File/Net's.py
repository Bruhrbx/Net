import socket
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext, simpledialog, messagebox
import psutil
import subprocess
import platform
import json
import os
import urllib.request

# === Warna Tema ===
PRIMARY = "#1E90FF"
DARK = "#104E8B"
LIGHT = "#E6F0FA"

# === Global Variables ===
USERS_FILE = "acc.json"
current_username = None
reply_to_username = None
client_socket = None
server_socket = None
chat_initialized = False

# === GitHub Update Configuration ===
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Bruhrbx/Net/main/File/Net's.py"
LOCAL_APP_FILE = os.path.basename(__file__)

# === Root Window ===
window = tk.Tk()
window.title("Net's Chat App")
window.geometry("700x500")
window.configure(bg=LIGHT)

# === Style Setup ===
style = ttk.Style(window)
style.theme_use("default")
style.configure("TNotebook", background=LIGHT, borderwidth=0)
style.configure("TNotebook.Tab", background=PRIMARY, foreground="white", padding=10)
style.map("TNotebook.Tab", background=[("selected", DARK)])
style.configure("TLabel", background=LIGHT)
style.configure("TButton", background=PRIMARY, foreground="white")
style.map("TButton", background=[("active", DARK)])

tab_control = ttk.Notebook(window)

# === User Authentication Functions ===
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_users(users):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Username sudah ada."
    users[username] = password
    save_users(users)
    return True, "Registrasi berhasil!"

def login_user(username, password):
    users = load_users()
    if username in users and users[username] == password:
        return True, "Login berhasil!"
    return False, "Username atau password salah."

def authenticate_user():
    global current_username
    auth_success = False

    while not auth_success:
        action = messagebox.askyesno("Login/Register", "Apakah Anda sudah punya akun? (Pilih 'No' untuk Registrasi)")

        if action: # Login
            username = simpledialog.askstring("Login", "Masukkan Username:")
            if not username: return False
            password = simpledialog.askstring("Login", "Masukkan Password:", show='*')
            if not password: return False

            success, message = login_user(username, password)
            if success:
                current_username = username
                messagebox.showinfo("Login", message)
                auth_success = True
            else:
                messagebox.showerror("Login Gagal", message + "\nCoba lagi atau daftar.")
        else: # Register
            username = simpledialog.askstring("Register", "Buat Username:")
            if not username: continue
            password = simpledialog.askstring("Register", "Buat Password:", show='*')
            if not password: continue

            success, message = register_user(username, password)
            if success:
                current_username = username
                messagebox.showinfo("Register", message + "\nAnda sekarang sudah login.")
                auth_success = True
            else:
                messagebox.showerror("Registrasi Gagal", message)
    return auth_success

# === Variabel Server Config ===
server_name = tk.StringVar(value="Server A")
server_ip = tk.StringVar(value="127.0.0.1")
server_port = tk.IntVar(value=12345)

# === Tab Home ===
home_tab = ttk.Frame(tab_control, padding=20)
tab_control.add(home_tab, text='Home')
welcome_label = ttk.Label(home_tab, text="Selamat Datang di Chat App!", font=("Segoe UI", 16, "bold"))
welcome_label.pack(pady=50)

# === Tab Server ===
server_tab = ttk.Frame(tab_control, padding=10)
tab_control.add(server_tab, text='Server')

server_status = tk.StringVar()
server_status.set("Server belum berjalan.")

top_server_frame = ttk.Frame(server_tab)
top_server_frame.pack(fill='x', padx=5, pady=10)

# Server Config Panel
config_frame = ttk.LabelFrame(top_server_frame, text="Server Config", padding=10)
config_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

ttk.Label(config_frame, text="Nama Server:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
ttk.Entry(config_frame, textvariable=server_name).grid(row=0, column=1, padx=5, pady=2)

ttk.Label(config_frame, text="IP Address:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
ttk.Entry(config_frame, textvariable=server_ip).grid(row=1, column=1, padx=5, pady=2)

ttk.Label(config_frame, text="Port:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
ttk.Entry(config_frame, textvariable=server_port).grid(row=2, column=1, padx=5, pady=2)

# System Info Panel
system_info_frame = ttk.LabelFrame(top_server_frame, text="System Info", padding=10)
system_info_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

cpu_usage_var = tk.StringVar(value="CPU: --%")
mem_usage_var = tk.StringVar(value="Mem: --%")
ping_latency_var = tk.StringVar(value="Ping: --ms")

ttk.Label(system_info_frame, textvariable=cpu_usage_var).pack(anchor='w', padx=5, pady=2)
ttk.Label(system_info_frame, textvariable=mem_usage_var).pack(anchor='w', padx=5, pady=2)
ttk.Label(system_info_frame, textvariable=ping_latency_var).pack(anchor='w', padx=5, pady=2)

def update_system_info():
    # CPU Usage
    cpu_percent = psutil.cpu_percent(interval=None)
    cpu_usage_var.set(f"CPU: {cpu_percent:.1f}%")

    # Memory Usage
    mem_percent = psutil.virtual_memory().percent
    mem_usage_var.set(f"Mem: {mem_percent:.1f}%")

    # Ping Latency
    target_ip = "8.8.8.8"
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', target_ip]

    kwargs = {
        'capture_output': True,
        'text': True,
        'timeout': 1
    }
    if platform.system().lower() == 'windows':
        kwargs['creationflags'] = subprocess.CREATE_NO_WINDOW

    try:
        process = subprocess.run(command, **kwargs)
        output = process.stdout
        latency = "--"
        if platform.system().lower() == 'windows':
            if "Average =" in output:
                avg_line = [line for line in output.split('\n') if "Average =" in line]
                if avg_line:
                    avg_ms = avg_line[0].split("Average =")[1].split("ms")[0].strip()
                    latency = f"{avg_ms}ms"
        else:
            if "avg/" in output:
                parts = output.split("avg/")[1].split(" ")[0].split("/")
                if len(parts) >= 2:
                    latency = f"{float(parts[1]):.1f}ms"
        ping_latency_var.set(f"Ping: {latency}")
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        ping_latency_var.set("Ping: Gagal")
    except Exception as e:
        ping_latency_var.set(f"Ping: Error ({e})")

    window.after(3000, update_system_info)

window.after(100, update_system_info)

# Server Log Panel
server_log = scrolledtext.ScrolledText(server_tab, height=12, state='disabled', wrap='word', bg='white')
server_log.pack(padx=5, pady=(5, 10), fill='both', expand=True)

def log_server(text):
    server_log.config(state='normal')
    server_log.insert(tk.END, text + "\n")
    server_log.config(state='disabled')
    server_log.yview(tk.END)

def start_server():
    global server_socket
    
    def handle_client(conn, addr):
        log_server(f"[+] Client {addr} terhubung.")
        client_username = None
        
        try:
            # Receive username from client
            username_msg = conn.recv(1024).decode()
            if username_msg.startswith("USERNAME:"):
                client_username = username_msg.split(":")[1]
                log_server(f"[+] {addr} login sebagai {client_username}")
            
            while True:
                msg = conn.recv(1024).decode()
                if msg:
                    if client_username:
                        broadcast_msg = f"{client_username}: {msg}"
                    else:
                        broadcast_msg = f"{addr}: {msg}"
                    
                    log_server(broadcast_msg)
                    # Broadcast to all clients
                    for client in clients:
                        try:
                            client.send(broadcast_msg.encode())
                        except:
                            continue
                else:
                    break
        except:
            pass
        
        conn.close()
        if client_username:
            log_server(f"[-] {client_username} ({addr}) terputus.")
        else:
            log_server(f"[-] Client {addr} terputus.")

    def server_thread():
        global server_socket, clients
        clients = []
        
        try:
            ip = server_ip.get()
            port = server_port.get()
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.bind((ip, port))
            server_socket.listen(5)
            server_status.set(f"{server_name.get()} berjalan di {ip}:{port}")
            log_server(f"[✓] Server '{server_name.get()}' berjalan di {ip}:{port}, menunggu koneksi...")

            while True:
                conn, addr = server_socket.accept()
                clients.append(conn)
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            log_server(f"[Error] {e}")
            server_status.set("Gagal menjalankan server.")

    threading.Thread(target=server_thread, daemon=True).start()

ttk.Label(server_tab, textvariable=server_status).pack(pady=(0, 5))
ttk.Button(server_tab, text="Mulai Server", command=start_server).pack()

# === Tab Chat ===
chat_tab = ttk.Frame(tab_control, padding=10)
tab_control.add(chat_tab, text='Chat')

# Frame for chat display and user list
chat_main_frame = ttk.Frame(chat_tab)
chat_main_frame.pack(expand=True, fill='both', padx=5, pady=5)

# Chat display (left side)
chat_display = scrolledtext.ScrolledText(chat_main_frame, state='normal', wrap='word', bg='white')
chat_display.pack(side='left', expand=True, fill='both', padx=(0, 5))

# Online Users Panel (right side)
online_users_frame = ttk.LabelFrame(chat_main_frame, text="Online Users", padding=5)
online_users_frame.pack(side='right', fill='y', padx=(5, 0))

total_players_var = tk.StringVar(value="Total Players: 0")
ttk.Label(online_users_frame, textvariable=total_players_var).pack(pady=(0, 5))

online_users_listbox = tk.Listbox(online_users_frame, height=10, bg='white')
online_users_listbox.pack(expand=True, fill='both')

input_frame = tk.Frame(chat_tab, bg=LIGHT)
input_frame.pack(fill='x', padx=5, pady=5)

msg_entry = tk.Entry(input_frame)
msg_entry.pack(side='left', fill='x', expand=True, padx=(0, 5), pady=5)

def set_reply_target():
    global reply_to_username
    reply_to_username = simpledialog.askstring("Balas ke", "Masukkan nama pengguna yang ingin Anda balas:")
    if reply_to_username:
        messagebox.showinfo("Balas", f"Akan membalas ke {reply_to_username}")

def send_msg():
    global client_socket, reply_to_username
    msg = msg_entry.get().strip()
    if msg and client_socket and current_username:
        if reply_to_username:
            full_msg = f"{current_username} >> {reply_to_username} : {msg}"
            reply_to_username = None
        else:
            full_msg = f"{current_username}: {msg}"
        update_chat_display(f"Anda: {full_msg}")
        try:
            client_socket.send(full_msg.encode())
        except Exception as e:
            messagebox.showerror("Error", f"Gagal mengirim pesan: {e}")
    elif not current_username:
        messagebox.showwarning("Belum Login", "Anda harus login atau registrasi terlebih dahulu untuk chat.")
    msg_entry.delete(0, tk.END)

msg_entry.bind("<Return>", lambda event: send_msg())

reply_button = tk.Button(input_frame, text="Balas", bg='orange', fg='white', command=set_reply_target)
reply_button.pack(side='right', padx=(0, 5), pady=5)

send_button = tk.Button(input_frame, text="Kirim", bg=PRIMARY, fg='white', command=send_msg)
send_button.pack(side='right', pady=5)

def update_chat_display(text):
    chat_display.insert(tk.END, text + "\n")
    chat_display.yview(tk.END)

def receive_messages():
    global client_socket
    if not client_socket: return
    
    while True:
        try:
            msg = client_socket.recv(1024).decode()
            if msg:
                update_chat_display(msg)
            else:
                update_chat_display("[SERVER] Server terputus.")
                client_socket.close()
                break
        except Exception as e:
            update_chat_display(f"[ERROR] Terjadi kesalahan saat menerima pesan: {e}")
            client_socket.close()
            break

# === Tab Settings ===
settings_tab = ttk.Frame(tab_control, padding=10)
tab_control.add(settings_tab, text='Settings')

# Color variables for settings
primary_color_var = tk.StringVar(value=PRIMARY)
dark_color_var = tk.StringVar(value=DARK)
light_color_var = tk.StringVar(value=LIGHT)

def apply_theme_colors():
    global PRIMARY, DARK, LIGHT
    PRIMARY = primary_color_var.get()
    DARK = dark_color_var.get()
    LIGHT = light_color_var.get()

    window.configure(bg=LIGHT)
    style.configure("TNotebook", background=LIGHT)
    style.configure("TNotebook.Tab", background=PRIMARY)
    style.map("TNotebook.Tab", background=[("selected", DARK)])
    style.configure("TLabel", background=LIGHT)
    style.configure("TButton", background=PRIMARY, foreground="white")
    style.map("TButton", background=[("active", DARK)])

    input_frame.configure(bg=LIGHT)
    chat_display.configure(bg="white")
    server_log.configure(bg="white")
    online_users_listbox.configure(bg="white")

settings_frame = ttk.LabelFrame(settings_tab, text="Theme Colors", padding=10)
settings_frame.pack(fill='x', padx=5, pady=10)

ttk.Label(settings_frame, text="Primary Color:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
ttk.Entry(settings_frame, textvariable=primary_color_var).grid(row=0, column=1, padx=5, pady=2)

ttk.Label(settings_frame, text="Dark Color:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
ttk.Entry(settings_frame, textvariable=dark_color_var).grid(row=1, column=1, padx=5, pady=2)

ttk.Label(settings_frame, text="Light Color:").grid(row=2, column=0, sticky='w', padx=5, pady=2)
ttk.Entry(settings_frame, textvariable=light_color_var).grid(row=2, column=1, padx=5, pady=2)

ttk.Button(settings_frame, text="Apply Colors", command=apply_theme_colors).grid(row=3, column=0, columnspan=2, pady=10)

# Update Function
def update_application():
    response = messagebox.askyesno(
        "Update Aplikasi",
        "Ini akan mencoba mengunduh versi terbaru aplikasi dari GitHub dan menimpa file lokal Anda.\n"
        "Aplikasi perlu di-restart agar perubahan berlaku.\n"
        "Apakah Anda ingin melanjutkan?"
    )
    if not response:
        return

    try:
        messagebox.showinfo("Update", "Mengunduh update... Mohon tunggu.")
        with urllib.request.urlopen(GITHUB_RAW_URL) as response:
            new_code = response.read().decode('utf-8')

        with open(LOCAL_APP_FILE, 'w', encoding='utf-8') as f:
            f.write(new_code)

        messagebox.showinfo(
            "Update Berhasil!",
            "Aplikasi berhasil diupdate.\n"
            "Mohon tutup dan jalankan kembali aplikasi ini agar perubahan berlaku."
        )
    except Exception as e:
        messagebox.showerror("Update Gagal", f"Gagal mengunduh atau menulis update: {e}\n"
                                          "Pastikan URL GitHub benar dan ada koneksi internet.")

update_frame = ttk.LabelFrame(settings_tab, text="App Update", padding=10)
update_frame.pack(fill='x', padx=5, pady=10)
ttk.Label(update_frame, text="Dapatkan versi terbaru aplikasi dari GitHub.").pack(pady=5)
ttk.Button(update_frame, text="Update Me! :D", command=update_application).pack(pady=5)

# === Saat Tab Chat Dibuka (Koneksi Client) ===
def on_tab_change(event):
    global chat_initialized, client_socket
    selected_tab = tab_control.tab(tab_control.select(), "text")
    if selected_tab == "Chat" and not chat_initialized:
        if not current_username:
            messagebox.showwarning("Login Diperlukan", "Anda harus login atau registrasi terlebih dahulu untuk terhubung ke chat.")
            tab_control.select(home_tab)
            return

        ip = simpledialog.askstring("Koneksi ke Server", "Masukkan IP Server:", initialvalue=server_ip.get())
        port = simpledialog.askinteger("Koneksi ke Server", "Masukkan Port Server:", initialvalue=server_port.get())
        if ip and port:
            try:
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.connect((ip, port))
                client_socket.send(f"USERNAME:{current_username}".encode())
                update_chat_display(f"[✓] Terhubung ke server {ip}:{port} sebagai {current_username}")
                chat_initialized = True
                threading.Thread(target=receive_messages, daemon=True).start()
            except Exception as e:
                update_chat_display(f"[Error] Tidak dapat terhubung ke server: {e}")
                chat_initialized = False

tab_control.bind("<<NotebookTabChanged>>", on_tab_change)
tab_control.pack(expand=1, fill='both')

# Run authentication dialog before starting the main loop
if not authenticate_user():
    window.destroy()
else:
    if current_username:
        welcome_label.config(text=f"Selamat Datang, {current_username}!")
    window.mainloop()
