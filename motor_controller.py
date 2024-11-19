import requests
import json
import time
import threading
from tkinter import messagebox

class MotorController:
    def __init__(self, view):
        self.view = view
        self.esp32_ip = "192.168.4.1"
        self.simulacion_activa = False
        self.monitor_thread = None
        self.last_config = None
        self.last_frequency = 1.0
        
    def send_config_to_esp32(self):
        """Envía la configuración actual al ESP32"""
        try:
            config = {
                "cilindros": self.view.cylinders.get(),
                "orden": self.view.firing_order.get(),
                "configuracion": self.view.configuration.get(),
                "frecuencia": float(self.view.frequency.get())
            }
            
            # Evitar envíos duplicados
            if self.last_config == config:
                return
            
            self.last_config = config
            print(f"Enviando configuración: {json.dumps(config, indent=2)}")
            
            response = requests.post(
                f'http://{self.esp32_ip}/config',
                json=config,
                timeout=2
            )
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'success' in data and data['success']:
                        print(f"Respuesta del ESP32: {data['message']}")
                        if 'config' in data:
                            print(data['config'])
                        self.view.update_status_bar("Configuración actualizada correctamente")
                    else:
                        raise Exception(data.get('message', 'Error desconocido'))
                except json.JSONDecodeError:
                    print(f"Respuesta texto plano: {response.text}")
                    self.view.update_status_bar("Configuración actualizada")
            else:
                raise Exception(f"Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión: {str(e)}"
            print(error_msg)
            self.view.update_status_bar(error_msg)
        except Exception as e:
            error_msg = f"Error al enviar configuración: {str(e)}"
            print(error_msg)
            self.view.update_status_bar(error_msg)

    def update_view_with_states(self, data):
        """Actualiza la vista con los estados recibidos"""
        try:
            print(f"Datos recibidos: {data}")  # Debug
            
            # Convertir lista de estados a diccionario
            if 'estados' in data and isinstance(data['estados'], list):
                estados = {}
                for i, estado in enumerate(data['estados'], 1):  # Empezar desde 1
                    estados[i] = estado
                
                print(f"Estados procesados: {estados}")  # Debug
                self.view.update_injector_states(estados)
            
            # Actualizar frecuencia si ha cambiado
            if 'frecuencia' in data:
                freq = float(data['frecuencia'])
                current_freq = float(self.view.frequency.get())
                if abs(freq - current_freq) > 0.01:
                    self.view.frequency.set(f"{freq:.2f}")
                    self.view.calculate_rpm_equivalent()
            
            # Actualizar estado de red
            if 'modo' in data:
                status = f"Conectado - {data['modo']} - {data['ip']}"
                if 'rssi' in data:
                    status += f" ({data['rssi']} dBm)"
                self.view.update_status_bar(status)
                
        except Exception as e:
            print(f"Error en update_view_with_states: {e}")
            self.view.update_status_bar(f"Error de actualización: {str(e)}")
    
    def monitor_states(self):
        """Monitorea los estados del ESP32"""
        retry_count = 0
        max_retries = 3
        
        while self.simulacion_activa:
            try:
                response = requests.get(f'http://{self.esp32_ip}/estado', timeout=1)
                if response.status_code == 200:
                    data = response.json()
                    print(f"Datos recibidos del ESP32: {data}")  # Debug
                    self.update_view_with_states(data)
                    retry_count = 0
                else:
                    print(f"Error en respuesta: {response.status_code}")
            except requests.exceptions.RequestException as e:
                retry_count += 1
                print(f"Error de conexión ({retry_count}/{max_retries}): {e}")
                if retry_count >= max_retries:
                    print("Demasiados errores, deteniendo monitoreo")
                    self.simulacion_activa = False
                    self.view.reset_simulation()
                    break
            except Exception as e:
                print(f"Error en monitor_states: {e}")
            
            time.sleep(0.1)  # 100ms entre actualizaciones
    
    def update_motor_selection(self, event):
        """Actualiza la selección del motor"""
        self.view.update_motor_selection(event)
        print("Configuración del motor cambiada, enviando al ESP32...")
        self.send_config_to_esp32()

    def toggle_simulation(self):
        """Inicia/detiene la simulación"""
        try:
            action = "start" if not self.simulacion_activa else "stop"
            print(f"Enviando comando de simulación: {action}")
            
            response = requests.post(
                f'http://{self.esp32_ip}/simulacion',
                json={"action": action},
                timeout=2
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    self.simulacion_activa = (action == "start")
                    self.view.running = self.simulacion_activa
                    self.view.start_btn.config(
                        text="Detener" if self.simulacion_activa else "Iniciar"
                    )
                    
                    if self.simulacion_activa:
                        print("Iniciando simulación y monitoreo")
                        self.view.update_simulation()
                        self.start_monitoring()
                    else:
                        print("Deteniendo simulación")
                        self.view.reset_simulation()
                    
                    self.view.update_status_bar(data['message'])
                else:
                    raise Exception(data.get('message', 'Error en la respuesta'))
            else:
                raise Exception(f"Error {response.status_code}")
                
        except Exception as e:
            error_msg = f"Error en simulación: {str(e)}"
            print(error_msg)
            messagebox.showerror("Error", error_msg)
            self.view.update_status_bar(error_msg)

    def start_monitoring(self):
        """Inicia el monitoreo de estados"""
        if self.simulacion_activa and (not self.monitor_thread or not self.monitor_thread.is_alive()):
            self.monitor_thread = threading.Thread(target=self.monitor_states)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            print("Monitoreo iniciado")

    def cleanup(self):
        """Limpia recursos antes de cerrar"""
        print("Limpiando recursos...")
        self.simulacion_activa = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)

    def update_frequency(self):
        """Actualiza la frecuencia en el ESP32"""
        try:
            freq = float(self.view.frequency.get())
            if freq != self.last_frequency:  # Evitar actualizaciones innecesarias
                self.last_frequency = freq
                self.send_config_to_esp32()
        except ValueError as e:
            print(f"Error al actualizar frecuencia: {e}")
            self.view.frequency.set("1.0")  # Restaurar valor por defecto
