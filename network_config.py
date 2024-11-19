import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json

class NetworkManager:
    def __init__(self):
        # IPs por defecto
        self.ap_ip = "192.168.4.1"
        self.sta_ip = None
        self.current_mode = "AP"
        self.current_ip = self.ap_ip

    def update_ip(self, new_ip):
        """Actualiza la IP actual"""
        self.current_ip = new_ip
        if self.current_mode == "AP":
            self.ap_ip = new_ip
        else:
            self.sta_ip = new_ip
        print(f"IP actualizada: {new_ip} en modo {self.current_mode}")

    def get_base_url(self):
        """Obtiene la URL base actual"""
        return f"http://{self.current_ip}"

    def send_request(self, endpoint, method='GET', data=None, timeout=5):
        """Envía una petición HTTP al ESP32"""
        url = f"{self.get_base_url()}{endpoint}"
        try:
            if method == 'GET':
                response = requests.get(url, timeout=timeout)
            else:
                response = requests.post(url, json=data, timeout=timeout)
            return True, response
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión: {e}")
            return False, None

    def get_network_status(self):
        """Obtiene el estado actual de la red"""
        success, response = self.send_request('/estado')
        if success:
            data = response.json()
            # Actualizar modo e IP si es necesario
            self.current_mode = data['modo']
            if data['ip'] != self.current_ip:
                self.update_ip(data['ip'])
            return True, data
        return False, None

class WiFiConfigDialog:
    def __init__(self, parent, network_manager):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuración WiFi")
        self.dialog.geometry("300x250")
        self.network_manager = network_manager
        
        # Frame principal
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Estado actual
        status_frame = ttk.LabelFrame(main_frame, text="Estado Actual", padding="5")
        status_frame.pack(fill=tk.X, pady=5)

        # Modo
        ttk.Label(status_frame, text="Modo:").grid(row=0, column=0, padx=5, pady=2)
        self.modo_label = ttk.Label(status_frame, text="--")
        self.modo_label.grid(row=0, column=1, padx=5, pady=2)

        # IP
        ttk.Label(status_frame, text="IP:").grid(row=1, column=0, padx=5, pady=2)
        self.ip_label = ttk.Label(status_frame, text="--")
        self.ip_label.grid(row=1, column=1, padx=5, pady=2)

        # RSSI
        ttk.Label(status_frame, text="Señal (RSSI):").grid(row=2, column=0, padx=5, pady=2)
        self.rssi_label = ttk.Label(status_frame, text="--")
        self.rssi_label.grid(row=2, column=1, padx=5, pady=2)

        # Botones de modo
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=10)

        ttk.Button(buttons_frame, text="Cambiar a AP", 
                  command=lambda: self.change_mode("AP")).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons_frame, text="Cambiar a STA", 
                  command=lambda: self.change_mode("STA")).pack(side=tk.LEFT, padx=5)

        # Estado de conexión
        self.status_label = ttk.Label(main_frame, text="Estado: --")
        self.status_label.pack(fill=tk.X, pady=5)

        # Actualizar periódicamente
        self.update_status()
        
    def update_status(self):
        """Actualiza la información de estado"""
        success, info = self.network_manager.get_network_status()
        if success:
            self.modo_label.config(text=info['modo'])
            self.ip_label.config(text=info['ip'])
            if 'rssi' in info:
                self.rssi_label.config(text=f"{info['rssi']} dBm")
            else:
                self.rssi_label.config(text="N/A")
            self.status_label.config(text="Estado: Conectado")
        else:
            self.status_label.config(text="Estado: Error de conexión")
        
        # Programar próxima actualización
        self.dialog.after(2000, self.update_status)

    def change_mode(self, mode):
        """Cambia el modo WiFi"""
        self.status_label.config(text=f"Estado: Cambiando a modo {mode}...")
        success, response = self.network_manager.send_request('/modo-wifi', 'POST', {'mode': mode})
        if success:
            self.dialog.after(2000, self.update_status)  # Actualizar después de 2 segundos
        else:
            self.status_label.config(text="Estado: Error al cambiar modo")
            messagebox.showerror("Error", "No se pudo cambiar el modo WiFi")