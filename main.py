import tkinter as tk
from tkinter import ttk, messagebox
import subprocess

DNS_SERVERS = [
    ("CloudFlare DNS", "1.1.1.1", "1.0.0.1"),    
    ("OpenDNS", "208.67.222.222", "208.67.220.220"),    
    ("Google Public DNS", "8.8.8.8", "8.8.4.4"),    
    ("Quad9", "9.9.9.9", "149.112.112.112"),    
    ("Comodo SecureDNS", "8.26.56.26", "8.20.247.20"),    
    ("OpenDNS Familiy Shield", "208.67.222.123", "208.67.220.123"),
    ("Verisign","64.6.64.6","64.6.65.6"),
    ("Yandex Basic","77.88.8.8","77.88.8.1"),
    ("Yandex Safe","77.88.8.88","77.88.8.2"),
    ("Yandex Family","77.88.8.7","77.88.8.3"),
    ("AdGuard","176.103.130.130","176.103.130.131"),
    ("CleanBrowsing Security","185.228.168.168","185.228.169.9"),
    ]

def ping_dns(dns):
    cmd = f"ping {dns} -n 1"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = result.stdout.decode('utf-8')
    if "TTL" in output:
        time = output.split("time=")[1].split("ms")[0].strip()
        return time
    else:
        return "-"

def find_fastest_dns():
    fastest_time = float('inf')
    fastest_dns = None
    for dns in DNS_SERVERS:
        primary_dns = dns[1]
        secondary_dns = dns[2]
        primary_time = ping_dns(primary_dns)
        secondary_time = ping_dns(secondary_dns)
        if primary_time != "-" and secondary_time != "-":
            avg_time = (float(primary_time) + float(secondary_time)) / 2
            if avg_time < fastest_time:
                fastest_time = avg_time
                fastest_dns = dns
    return fastest_dns

def set_dns(dns):
    primary_dns = dns[1]
    secondary_dns = dns[2]
    wifi_interface = "Wi-Fi"
    ethernet_interface = "Ethernet"
    cmd_wifi = f"netsh interface ip set dns name=\"{wifi_interface}\" static {primary_dns} primary"
    cmd_ethernet = f"netsh interface ip set dns name=\"{ethernet_interface}\" static {primary_dns} primary"
    result = subprocess.run(cmd_wifi, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if result.returncode != 0:
        result = subprocess.run(cmd_ethernet, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    cmd_wifi = f"netsh interface ip add dns name=\"{wifi_interface}\" {secondary_dns} index=2"
    cmd_ethernet = f"netsh interface ip add dns name=\"{ethernet_interface}\" {secondary_dns} index=2"
    result = subprocess.run(cmd_wifi, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    if result.returncode != 0:
        result = subprocess.run(cmd_ethernet, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

root = tk.Tk()
root.title("En Hızlı DNS Sunucusu")
 

# Öğeleri konumlandırmak için paket kullanımı
# Use of packages to position items
top_frame = tk.Frame(root)
top_frame.pack(side=tk.TOP, padx=10, pady=10)

bottom_frame = tk.Frame(root)
bottom_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

# Treeview sütunları
# Treeview colums
columns = ("DNS Sunucusu", "Ön Tanımlı DNS", "Alternatif DNS", "Ön Tanımlı Ping Süresi", "Alternatif Ping Süresi")

# Treeview
treeview = ttk.Treeview(bottom_frame, columns=columns, show="headings")
treeview.pack(side=tk.LEFT)
treeview.column("DNS Sunucusu", width=120, anchor="center")
treeview.column("Ön Tanımlı DNS", width=120, anchor="center")
treeview.column("Alternatif DNS", width=120, anchor="center")
treeview.column("Ön Tanımlı Ping Süresi", width=150, anchor="center")
treeview.column("Alternatif Ping Süresi", width=150, anchor="center")


# Top frame'i hizala
# Align top frame
top_frame.grid_columnconfigure(0, weight=1)
top_frame.grid_columnconfigure(1, weight=1)
top_frame.grid_columnconfigure(2, weight=1)

# Sütun başlıkları
# Column headings
for col in columns:
    treeview.heading(col, text=col)

# DNS sunucularını pingle ve Treeview'a ekle
# Ping DNS servers and add them to Treeview
for dns in DNS_SERVERS:
    name, primary, secondary = dns
    primary_time = ping_dns(primary)
    secondary_time = ping_dns(secondary)
    treeview.insert("", "end", values=(name, primary, secondary, primary_time, secondary_time))

# En hızlı DNS sunucusunu bul ve etikete yazdır
# Find the fastest DNS server and print it on the label
fastest_dns = find_fastest_dns()
label = tk.Label(top_frame, text=f"En hızlı DNS sunucusu: {fastest_dns[0]}", font=("Helvetica", 16), fg="darkblue", pady=10)
label.pack()

# Değiştir düğmesi
# Change button
def change_dns():
    set_dns(fastest_dns)
    messagebox.showinfo("Bilgi", "DNS ayarları başarı ile değiştirildi.")
change_button = tk.Button(top_frame, text="Değiştir", bg="lightblue", command=change_dns, width=10)
change_button.pack(side="left", padx=2, pady=2)


# İptal düğmesi
# Cancel button
cancel_button = tk.Button(top_frame, text="İptal", bg="lightblue", command=root.destroy, width=10)
cancel_button.pack(side="right", padx=2, pady=2)

# En hızlı DNS sunucusunu Treeview'da vurgula
# Highlight the fastest DNS server in Treeview
for i in treeview.get_children():
    if treeview.item(i)['values'][0] == fastest_dns[0]:
        treeview.item(i, tags=('selected',))
        treeview.tag_configure('selected', background='yellow')


# En hızlı DNS sunucusu bulunamazsa uyarı ver
# Alert if the fastest DNS server cannot be found
if not fastest_dns:
    messagebox.showwarning("Uyarı", "Hiçbir DNS sunucusuna erişilemiyor.", icon="warning")
    root.destroy()
else:
    root.mainloop()