import tkinter as tk
from motor_simulation_view import MotorSimulation
from motor_controller import MotorController

def main():
    root = tk.Tk()
    root.title("Simulador de Banco de Inyectores")
    
    # Crear instancias
    view = MotorSimulation(root)
    controller = MotorController(view)
    
    # Conectar el controlador con la vista
    view.connect_controller(controller)
    
    # Manejar cierre de la aplicación
    def on_closing():
        if hasattr(controller, 'cleanup'):
            controller.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Iniciar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()