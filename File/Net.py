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

# === Color Theme ===
PRIMARY = "#1E90FF"
DARK = "#104E8B"
LIGHT = "#E6F0FA"

# === Global Variables ===
USERS_FILE = "acc.json"
RECENT_GROUPS_FILE = "recent_groups.json"
current_username = None
reply_to_username = None
client_socket = None
server_socket = None
chat_initialized = False
clients = []
online_users = {}

# === GitHub Update Configuration ===
GITHUB_RAW_URL = "https://raw.githubusercontent.com/Bruhrbx/Net/main/File/Net.py"
LOCAL_APP_FILE = os.path.basename(__file__)

# === Root Window ===
window = tk.Tk()
window.title("Net's Chat App")
window.geometry("840x536")
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
        return False, "Username already exists."
    users[username] = password
    save_users(users)
    return True, "Registration successful!"

def login_user(username, password):
    users = load_users()
    if username in users and users[username] == password:
        return True, "Login successful!"
    return False, "Incorrect username or password."

def authenticate_user():
    global current_username
    auth_success = False

    while not auth_success:
        action = messagebox.askyesno("Login/Register", "Do you have an account? (Select 'No' to Register)")

        if action: # Login
            username = simpledialog.askstring("Login", "Enter Username:")
            if not username: return False
            password = simpledialog.askstring("Login", "Enter Password:", show='*')
            if not password: return False

            success, message = login_user(username, password)
            if success:
                current_username = username
                messagebox.showinfo("Login", message)
                auth_success = True
            else:
                messagebox.showerror("Login Failed", message + "\nPlease try again or register.")
        else: # Register
            username = simpledialog.askstring("Register", "Create Username:")
            if not username: continue
            password = simpledialog.askstring("Register", "Create Password:", show='*')
            if not password: continue

            success, message = register_user(username, password)
            if success:
                current_username = username
                messagebox.showinfo("Register", message + "\nYou are now logged in.")
                auth_success = True
            else:
                messagebox.showerror("Registration Failed", message)
    return auth_success

# === Recent Groups Functions ===
def load_recent_groups():
    if os.path.exists(RECENT_GROUPS_FILE):
        with open(RECENT_GROUPS_FILE, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {"Net's Office": "lOsT iP LOl"}

def save_recent_groups(groups):
    with open(RECENT_GROUPS_FILE, 'w') as f:
        json.dump(groups, f, indent=4)

def add_recent_group(group_name, address):
    groups = load_recent_groups()
    groups[group_name] = address
    save_recent_groups(groups)

# === Server Config Variables ===
server_name = tk.StringVar(value="Net's")
server_ip = tk.StringVar(value="127.0.0.1")
server_port = tk.IntVar(value=12345)

# === Home Tab ===
def create_home_tab():
    global home_tab
    home_tab = ttk.Frame(tab_control, padding=20)
    tab_control.add(home_tab, text='Home')
    
    welcome_label = ttk.Label(home_tab, 
                            text=f"Welcome, {current_username}!" if current_username else "Welcome to Chat App!",
                            font=("Segoe UI", 16, "bold"))
    welcome_label.pack(pady=(0, 20))

    # Main container frame
    main_frame = ttk.Frame(home_tab)
    main_frame.pack(fill='both', expand=True)

    # Left column (Announcements)
    left_frame = ttk.Frame(main_frame)
    left_frame.pack(side='left', fill='both', expand=True, padx=5)

    # Announcement Section
    announcement_frame = ttk.LabelFrame(left_frame, text="📢 Announcements", padding=10)
    announcement_frame.pack(fill='both', expand=True, pady=5)

    announcements = [
        "🎉 New Feature: Recents Server",
        "📢 Join our group: 'discord.gg/f9HGQkDGgb"

        "📢 Coming Version: '2.1"
    ]

    announcement_text = scrolledtext.ScrolledText(
        announcement_frame, 
        height=6, 
        wrap='word', 
        bg='white',
        font=("Arial", 10)
    )
    for item in announcements:
        announcement_text.insert('end', f"• {item}\n\n")
    announcement_text.config(state='disabled')
    announcement_text.pack(fill='both', expand=True)

    # Right column (Recent Groups)
    right_frame = ttk.Frame(main_frame)
    right_frame.pack(side='right', fill='y', padx=5)

    recent_groups_frame = ttk.LabelFrame(right_frame, text="====== Recent Groups ======", padding=10)
    recent_groups_frame.pack(fill='both', expand=True, pady=5)

    recent_groups = load_recent_groups()

    group_listbox = tk.Listbox(
        recent_groups_frame,
        height=6,
        bg='white',
        font=("Courier", 10),
        relief='flat'
    )
    
    for group, address in recent_groups.items():
        group_listbox.insert('end', f"{group:15} {address}")

    scrollbar = ttk.Scrollbar(recent_groups_frame)
    scrollbar.pack(side='right', fill='y')
    group_listbox.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=group_listbox.yview)

    group_listbox.pack(fill='both', expand=True)

    def connect_to_selected_group():
        selection = group_listbox.curselection()
        if selection:
            selected_text = group_listbox.get(selection[0])
            parts = selected_text.split()
            group_name = ' '.join(parts[:-1])
            address = parts[-1]
            
            server_address_var.set(address)
            tab_control.select(chat_tab)
            messagebox.showinfo("Connecting", f"Connecting to {group_name}...")

    connect_btn = ttk.Button(
        recent_groups_frame,
        text="Connect to Selected",
        command=connect_to_selected_group
    )
    connect_btn.pack(pady=5, fill='x')

create_home_tab()

# === Server Tab ===
server_tab = ttk.Frame(tab_control, padding=10)
tab_control.add(server_tab, text='Server')

server_status = tk.StringVar()
server_status.set("Server is not running.")

top_server_frame = ttk.Frame(server_tab)
top_server_frame.pack(fill='x', padx=5, pady=10)

# Server Config Panel
config_frame = ttk.LabelFrame(top_server_frame, text="Server Config", padding=10)
config_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

ttk.Label(config_frame, text="Server Name:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
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
        ping_latency_var.set("Ping: Failed")
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
        global online_users
        client_username = None
        
        try:
            username_msg = conn.recv(1024).decode()
            if username_msg.startswith("USERNAME:"):
                client_username = username_msg.split(":")[1]
                online_users[client_username] = addr
                log_server(f"[+] {addr} logged in as {client_username}")
                update_online_users()
            
            while True:
                msg = conn.recv(1024).decode()
                if msg:
                    if client_username:
                        broadcast_msg = f"{client_username}: {msg}"
                    else:
                        broadcast_msg = f"{addr}: {msg}"
                    
                    log_server(broadcast_msg)
                    for client in clients:
                        try:
                            client.send(broadcast_msg.encode())
                        except:
                            continue
                else:
                    break
        except Exception as e:
            log_server(f"[!] Error with {addr}: {e}")
        finally:
            conn.close()
            if client_username:
                log_server(f"[-] {client_username} ({addr}) disconnected")
                if client_username in online_users:
                    del online_users[client_username]
                    update_online_users()
            else:
                log_server(f"[-] Client {addr} disconnected")

    def server_thread():
        global server_socket, clients
        clients = []
        
        try:
            ip = server_ip.get()
            port = server_port.get()
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind((ip, port))
            server_socket.listen(5)
            server_status.set(f"{server_name.get()} running on {ip}:{port}")
            log_server(f"[✓] Server '{server_name.get()}' running on {ip}:{port}, waiting for connections...")

            while True:
                conn, addr = server_socket.accept()
                clients.append(conn)
                threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except Exception as e:
            log_server(f"[X] Server error: {e}")
            server_status.set("Failed to start server.")
        finally:
            if server_socket:
                server_socket.close()

    threading.Thread(target=server_thread, daemon=True).start()

def update_online_users():
    online_users_listbox.delete(0, tk.END)
    for username in online_users:
        online_users_listbox.insert(tk.END, username)
    total_players_var.set(f"Total Players: {len(online_users)}")

ttk.Label(server_tab, textvariable=server_status).pack(pady=(0, 5))
ttk.Button(server_tab, text="Start Server", command=start_server).pack()

# === Chat Tab ===
chat_tab = ttk.Frame(tab_control, padding=10)
tab_control.add(chat_tab, text='Chat')

# Connection control frame
connection_frame = ttk.Frame(chat_tab)
connection_frame.pack(fill='x', padx=5, pady=(0, 5))

server_address_var = tk.StringVar(value=f"{server_ip.get()}:{server_port.get()}")
ttk.Entry(connection_frame, textvariable=server_address_var).pack(side='left', fill='x', expand=True, padx=(0, 5))

connect_button = ttk.Button(connection_frame, text="Connect", command=lambda: connect_to_server())
connect_button.pack(side='right')

def connect_to_server():
    global chat_initialized, client_socket
    
    if chat_initialized:
        try:
            client_socket.close()
        except:
            pass
        client_socket = None
        chat_initialized = False
        connect_button.config(text="Connect")
        update_chat_display("[✓] Disconnected from server.")
        return
    
    if not current_username:
        messagebox.showwarning("Login Required", "You must login or register first to chat.")
        return

    address = server_address_var.get().split(":")
    if len(address) != 2:
        messagebox.showerror("Invalid Format", "Server address must be IP:PORT (e.g., 127.0.0.1:12345)")
        return
    
    ip, port = address[0], int(address[1])
    
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, port))
        client_socket.send(f"USERNAME:{current_username}".encode())
        
        # Add to recent groups
        group_name = simpledialog.askstring("Group Name", "Enter name for this group:")
        if group_name:
            add_recent_group(group_name, f"{ip}:{port}")
        
        update_chat_display(f"[✓] Connected to {ip}:{port} as {current_username}")
        chat_initialized = True
        connect_button.config(text="Disconnect")
        threading.Thread(target=receive_messages, daemon=True).start()
    except Exception as e:
        update_chat_display(f"[X] Failed to connect: {e}")
        chat_initialized = False

# Main chat frame
chat_main_frame = ttk.Frame(chat_tab)
chat_main_frame.pack(expand=True, fill='both', padx=5, pady=5)

# Chat display
chat_display = scrolledtext.ScrolledText(chat_main_frame, state='normal', wrap='word', bg='white')
chat_display.pack(side='left', expand=True, fill='both', padx=(0, 5))

# Online Users Panel
online_users_frame = ttk.LabelFrame(chat_main_frame, text="Online Users", padding=5)
online_users_frame.pack(side='right', fill='y', padx=(5, 0))

total_players_var = tk.StringVar(value="Total Players: 0")
ttk.Label(online_users_frame, textvariable=total_players_var).pack(pady=(0, 5))

online_users_listbox = tk.Listbox(online_users_frame, height=10, bg='white')
online_users_listbox.pack(expand=True, fill='both')

# Input frame
input_frame = tk.Frame(chat_tab, bg=LIGHT)
input_frame.pack(fill='x', padx=5, pady=5)

msg_entry = tk.Entry(input_frame)
msg_entry.pack(side='left', fill='x', expand=True, padx=(0, 5), pady=5)

def set_reply_target():
    global reply_to_username
    selected = online_users_listbox.curselection()
    if selected:
        reply_to_username = online_users_listbox.get(selected[0])
        messagebox.showinfo("Reply", f"Replying to {reply_to_username}")
    else:
        reply_to_username = simpledialog.askstring("Reply To", "Enter username to reply to:")
        if reply_to_username:
            messagebox.showinfo("Reply", f"Will reply to {reply_to_username}")

def send_msg():
    global client_socket, reply_to_username
    msg = msg_entry.get().strip()
    if not msg:
        return
        
    if client_socket and current_username:
        try:
            if reply_to_username:
                full_msg = f"{current_username} >> {reply_to_username}: {msg}"
                reply_to_username = None
            else:
                full_msg = f"{current_username}: {msg}"
                
            update_chat_display(f"You: {msg}")
            client_socket.send(full_msg.encode())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message: {e}")
    elif not current_username:
        messagebox.showwarning("Not Logged In", "You must login or register first to chat.")
    msg_entry.delete(0, tk.END)

msg_entry.bind("<Return>", lambda event: send_msg())

reply_button = tk.Button(input_frame, text="Reply", bg='orange', fg='white', command=set_reply_target)
reply_button.pack(side='right', padx=(0, 5), pady=5)

send_button = tk.Button(input_frame, text="Send", bg=PRIMARY, fg='white', command=send_msg)
send_button.pack(side='right', pady=5)

def update_chat_display(text):
    chat_display.config(state='normal')
    chat_display.insert(tk.END, text + "\n")
    chat_display.config(state='disabled')
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
                update_chat_display("[SERVER] Connection closed by server.")
                client_socket.close()
                connect_button.config(text="Connect")
                break
        except ConnectionResetError:
            update_chat_display("[!] Server disconnected you!")
            client_socket.close()
            connect_button.config(text="Connect")
            break
        except Exception as e:
            update_chat_display(f"[ERROR] Connection error: {e}")
            client_socket.close()
            connect_button.config(text="Connect")
            break

# === Settings Tab ===
settings_tab = ttk.Frame(tab_control, padding=10)
tab_control.add(settings_tab, text='Settings')

# Theme settings
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

# Update function
def update_application():
    response = messagebox.askyesno(
        "Update App",
        "This will download the latest version from GitHub and overwrite your local file.\n"
        "The app needs to restart for changes to take effect.\n"
        "Continue?"
    )
    if not response:
        return

    try:
        messagebox.showinfo("Update", "Downloading update... Please wait.")
        with urllib.request.urlopen(GITHUB_RAW_URL) as response:
            new_code = response.read().decode('utf-8')

        with open(LOCAL_APP_FILE, 'w', encoding='utf-8') as f:
            f.write(new_code)

        messagebox.showinfo(
            "Update Complete!",
            "App updated successfully.\n"
            "Please close and restart the application."
        )
    except Exception as e:
        messagebox.showerror("Update Failed", f"Failed to download update: {e}\n"
                                          "Check GitHub URL and internet connection.")

update_frame = ttk.LabelFrame(settings_tab, text="App Update", padding=10)
update_frame.pack(fill='x', padx=5, pady=10)
ttk.Label(update_frame, text="Get the latest version from GitHub. | v2.0 ").pack(pady=5)
ttk.Button(update_frame, text="Update Me! :D", command=update_application).pack(pady=5)

# Run authentication before main loop
if not authenticate_user():
    window.destroy()
else:
    if current_username:
        welcome_label = ttk.Label(home_tab, text=f"Welcome, {current_username}!", font=("Segoe UI", 16, "bold"))
        welcome_label.pack(pady=(0, 20))
    tab_control.pack(expand=1, fill='both')
    window.mainloop()
