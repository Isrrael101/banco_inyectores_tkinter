import tkinter as tk
from tkinter import ttk, messagebox
from motor_database import MotorDatabase

class MotorSimulation:
    def __init__(self, root):
        self.root = root
        self.root.title("Simulación de Inyectores Multi-Motor")
        
        # Definir constantes
        self.MIN_CILINDROS = 1
        self.MAX_CILINDROS = 18

        # Obtener la base de datos de motores
        self.motors = MotorDatabase.get_all_motors()

        # Variables de simulación
        self.frequency = tk.StringVar(value="1")
        self.cylinders = tk.IntVar(value=4)
        self.firing_order = tk.StringVar(value="1,3,4,2")
        self.configuration = tk.StringVar(value="En Línea")
        self.rpm_equivalent = tk.StringVar(value="60.0 RPM")
        self.running = False
        self.cycle_position = 0

        # Colores para los estados del motor
        self.state_colors = {
            'Admisión': '#90EE90',    # Verde claro
            'Compresión': '#FFB6C1',  # Rosa claro
            'Explosión': '#FF6B6B',   # Rojo
            'Escape': '#87CEEB',      # Azul claro
            'Inactivo': '#FFFFFF'     # Blanco
        }

        # Configurar el grid principal
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        # Frame principal
        self.main_frame = ttk.Frame(root)
        self.main_frame.grid(sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(1, weight=1)

        # Panel de control superior izquierdo
        left_control = ttk.LabelFrame(self.main_frame, text="Selección de Motor", padding="10")
        left_control.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Combobox de selección de motor
        ttk.Label(left_control, text="Motor Comercial:").pack(pady=5)
        self.motor_selector = ttk.Combobox(
            left_control,
            values=list(self.motors.keys()),
            state="readonly",
            width=40
        )
        self.motor_selector.pack(pady=5, padx=10, fill='x')
        self.motor_selector.bind('<<ComboboxSelected>>', self.update_motor_selection)
        
        # Configuración del motor
        config_frame = ttk.LabelFrame(left_control, text="Configuración", padding="5")
        config_frame.pack(fill='x', padx=5, pady=5)
        
        # Radio buttons para configuración
        ttk.Label(config_frame, text="Tipo:").pack(pady=2)
        config_type = ttk.Frame(config_frame)
        config_type.pack(fill='x', pady=2)
        ttk.Radiobutton(config_type, text="En Línea", variable=self.configuration, 
                    value="En Línea").pack(side='left', padx=10)
        ttk.Radiobutton(config_type, text="En V", variable=self.configuration, 
                    value="En V").pack(side='left', padx=10)

        # Panel de control superior derecho
        right_control = ttk.LabelFrame(self.main_frame, text="Control de Motor", padding="10")
        right_control.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
        
        # Control de cilindros
        cylinder_frame = ttk.Frame(right_control)
        cylinder_frame.pack(fill='x', pady=5)
        ttk.Label(cylinder_frame, text="Cilindros:").pack(side='left', padx=5)
        ttk.Button(cylinder_frame, text="-", width=2, 
                command=lambda: self.adjust_cylinders(-1)).pack(side='left', padx=2)
        self.cylinder_spin = ttk.Spinbox(
            cylinder_frame,
            from_=self.MIN_CILINDROS,
            to=self.MAX_CILINDROS,
            textvariable=self.cylinders,
            width=3
        )
        self.cylinder_spin.pack(side='left', padx=2)
        ttk.Button(cylinder_frame, text="+", width=2, 
                command=lambda: self.adjust_cylinders(1)).pack(side='left', padx=2)

        # Orden de encendido
        firing_frame = ttk.Frame(right_control)
        firing_frame.pack(fill='x', pady=5)
        ttk.Label(firing_frame, text="Orden de Encendido:").pack(side='left', padx=5)
        self.firing_order_entry = ttk.Entry(firing_frame, textvariable=self.firing_order)
        self.firing_order_entry.pack(side='left', fill='x', expand=True, padx=5)

        # Control de frecuencia
        freq_frame = ttk.LabelFrame(right_control, text="Control de Frecuencia", padding="5")
        freq_frame.pack(fill='x', pady=5)
        
        # Slider de frecuencia (solo valores enteros)
        freq_control = ttk.Frame(freq_frame)
        freq_control.pack(fill='x', pady=5)
        ttk.Label(freq_control, text="Hz:").pack(side='left', padx=5)
        self.freq_slider = ttk.Scale(
            freq_control,
            from_=1,     # Mínimo entero
            to=100,      # Máximo entero
            orient="horizontal",
            variable=self.frequency
        )
        self.freq_slider.pack(side='left', fill='x', expand=True, padx=5)
        
        # Entrada de frecuencia
        vcmd = (self.root.register(self.validate_frequency), '%P')
        self.freq_entry = ttk.Entry(
            freq_control,
            textvariable=self.frequency,
            width=6,
            validate='key',
            validatecommand=vcmd
        )
        self.freq_entry.pack(side='left', padx=5)

        # RPM equivalentes
        rpm_frame = ttk.Frame(freq_frame)
        rpm_frame.pack(fill='x')
        ttk.Label(rpm_frame, text="RPM Equivalentes:").pack(side='left', padx=5)
        ttk.Label(rpm_frame, textvariable=self.rpm_equivalent).pack(side='left')

        # Botones de control y estado
        control_panel = ttk.LabelFrame(right_control, text="Control de Simulación", padding="5")
        control_panel.pack(fill='x', pady=5)

        # Frame para botones y estado
        self.button_frame = ttk.Frame(control_panel)  # Guardar como variable de instancia
        self.button_frame.pack(fill='x', padx=5, pady=5)
        self.button_frame.grid_columnconfigure(0, weight=1)  # para centrar

        """ # Crear las variables StringVar para el estado y frecuencia
        self.status_text = tk.StringVar(value="Estado: Detenido")
        self.freq_text = tk.StringVar(value="Frecuencia actual: 0 Hz") """

        # Botón de inicio/parada
        self.start_btn = ttk.Button(
            self.button_frame,
            text="Iniciar",
            width=20
        )
        self.start_btn.grid(row=0, column=0, padx=5, pady=5)  # usar grid en lugar de pack

        """ # Estado de simulación usando StringVar
        self.simulation_status = ttk.Label(
            self.button_frame,      # Usa self.button_frame
            text="Estado: Detenido",  # Usar text en lugar de textvariable
            font=('Arial', 9, 'bold'),
            foreground='red'
        )
        self.simulation_status.pack(side='left', padx=20)

        # Monitor de frecuencia usando StringVar
        self.freq_monitor = ttk.Label(
            self.button_frame,      # Usa self.button_frame
            text="Frecuencia actual: 0 Hz",  # Usar text en lugar de textvariable
            font=('Arial', 9)
        )
        self.freq_monitor.pack(side='right', padx=5) """

        # Estilo para el botón de acción
        style = ttk.Style()
        style.configure(
            "Action.TButton",
            font=('Arial', 10, 'bold'),
            padding=5
        )

        # Área de visualización (canvas y tabla)
        visual_frame = ttk.Frame(self.main_frame)
        visual_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=5, pady=5)
        visual_frame.grid_columnconfigure(0, weight=2)
        visual_frame.grid_columnconfigure(1, weight=1)
        visual_frame.grid_rowconfigure(0, weight=1)  # Importante para el scroll vertical

        # Panel izquierdo: Canvas para inyectores con scroll
        canvas_frame = ttk.LabelFrame(visual_frame, text="Visualización de Inyectores", padding="10")
        canvas_frame.grid(row=0, column=0, sticky="nsew")
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        # Contenedor del canvas con scrollbars
        canvas_container = ttk.Frame(canvas_frame)
        canvas_container.pack(fill="both", expand=True)
        
        # Canvas principal con scrollbars
        self.canvas = tk.Canvas(
            canvas_container,
            width=600,  # Ancho aumentado
            height=600,
            bg='white',
            scrollregion=(0, 0, 1200, 1000)  # Área scrollable más grande
        )
        
        # Scrollbars
        self.scroll_y = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(canvas_container, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)
        
        # Scrollbars para el canvas
        self.scroll_y = ttk.Scrollbar(canvas_container, orient="vertical", command=self.canvas.yview)
        self.scroll_x = ttk.Scrollbar(canvas_container, orient="horizontal", command=self.canvas.xview)

        # Configurar scroll del canvas
        self.canvas.configure(yscrollcommand=self.scroll_y.set, xscrollcommand=self.scroll_x.set)

        # Empaquetar con grid para mejor control
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scroll_y.grid(row=0, column=1, sticky="ns")
        self.scroll_x.grid(row=1, column=0, sticky="ew")
        canvas_container.grid_rowconfigure(0, weight=1)
        canvas_container.grid_columnconfigure(0, weight=1)

        # Panel derecho: Tabla con scroll
        table_frame = ttk.LabelFrame(visual_frame, text="Tiempos de los Cilindros", padding="10")
        table_frame.grid(row=0, column=1, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Contenedor de la tabla con scroll
        table_container = ttk.Frame(table_frame)
        table_container.grid(sticky="nsew")
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Canvas y scrollbar para la tabla
        self.table_canvas = tk.Canvas(table_container, height=600)
        table_scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.table_canvas.yview)
        table_scrollbar_x = ttk.Scrollbar(table_container, orient="horizontal", command=self.table_canvas.xview)
        
        self.table_content = ttk.Frame(self.table_canvas)
        self.table_canvas.configure(yscrollcommand=table_scrollbar.set, xscrollcommand=table_scrollbar_x.set)

        # Empaquetar con grid
        self.table_canvas.grid(row=0, column=0, sticky="nsew")
        table_scrollbar.grid(row=0, column=1, sticky="ns")
        table_scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        # Crear ventana para el contenido de la tabla
        self.table_window = self.table_canvas.create_window(
            (0, 0),
            window=self.table_content,
            anchor="nw"
        )

        # Configurar scroll de la tabla
        def on_frame_configure(event):
            self.table_canvas.configure(scrollregion=self.table_canvas.bbox("all"))
        self.table_content.bind("<Configure>", on_frame_configure)

        def on_canvas_configure(event):
            self.table_canvas.itemconfig(self.table_window, width=event.width)
        self.table_canvas.bind("<Configure>", on_canvas_configure)

        # Inicializar tabla
        self.initialize_table()

        # Crear leyenda de estados
        legend_frame = ttk.LabelFrame(self.main_frame, text="Leyenda de Estados", padding="5")
        legend_frame.grid(row=2, column=0, columnspan=2, pady=5, sticky="ew")

        # Grid para la leyenda
        for i, (estado, color) in enumerate(self.state_colors.items()):
            if estado != 'Inactivo':  # No mostrar estado inactivo
                frame = ttk.Frame(legend_frame)
                frame.grid(row=i//2, column=i%2, padx=10, pady=2, sticky="w")
                
                # Indicador de color
                color_box = tk.Label(
                    frame,
                    bg=color,
                    width=3,
                    height=1,
                    relief="solid"
                )
                color_box.pack(side="left", padx=(0,5))
                
                # Nombre del estado
                ttk.Label(frame, text=estado).pack(side="left")

        # Barra de estado principal
        status_frame = ttk.Frame(self.main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=5)

        # Indicador de red
        self.network_indicator = ttk.Label(
            status_frame,
            text="●",
            font=('Arial', 12),
            foreground='red'
        )
        self.network_indicator.pack(side="left", padx=5)

        # Barra de estado
        self.status_bar = ttk.Label(
            status_frame,
            text="Sistema iniciado",
            relief="sunken",
            padding=(5,2)
        )
        self.status_bar.pack(side="left", fill="x", expand=True)

        # Configurar bindings y trazas
        self.firing_order_entry.bind('<Return>', self.validate_firing_order)
        self.firing_order_entry.bind('<FocusOut>', self.validate_firing_order)
        self.frequency.trace_add("write", self.on_frequency_change)
        self.cylinders.trace_add("write", self.on_cylinder_change)
        self.freq_slider.configure(command=self.on_slider_change)
        self.configuration.trace_add("write", lambda *args: self.on_config_change())

        # Inicialización de inyectores
        self.injectors = {}
        self.setup_initial_state()

        # Crear menú
        self.create_menu()

        # Establecer valor por defecto en el selector de motor
        self.motor_selector.set(list(self.motors.keys())[0])

        # Mostrar mensaje inicial
        self.update_status_bar("Sistema listo para operar")

    def on_config_change(self):
        """Maneja el cambio de configuración del motor"""
        print(f"Configuración cambiada a: {self.configuration.get()}")
        self.update_simulation_params()
        self.update_injectors()
    
    def on_frequency_change(self, *args):
        """Maneja cambios en la frecuencia"""
        if not hasattr(self, '_frequency_update_pending'):
            self._frequency_update_pending = False
        
        if not self._frequency_update_pending:
            self._frequency_update_pending = True
            self.root.after(100, self._process_frequency_change)

    def adjust_cylinders(self, delta):
        """Ajusta el número de cilindros por +/- 1"""
        current = self.cylinders.get()
        new_value = current + delta
        
        # Validar límites
        if self.MIN_CILINDROS <= new_value <= self.MAX_CILINDROS:
            self.cylinders.set(new_value)
            self.on_cylinder_change()

    def initialize_table(self):
        """Inicializa la tabla de tiempos"""
        # Headers
        headers = ["Cilindro", "1er Tiempo", "2do Tiempo", "3er Tiempo", "4to Tiempo"]
        
        # Configurar anchos de columna
        widths = [13, 15, 15, 15, 15]  # Aumentar el primer número para hacer más ancha la columna Cilindro
        
        for col, header in enumerate(headers):
            lbl = ttk.Label(
                self.table_content, 
                text=header, 
                font=('Arial', 10, 'bold'),
                width=widths[col]  # Aplicar el ancho correspondiente
            )
            lbl.grid(row=0, column=col, padx=2, pady=2)
            self.table_content.grid_columnconfigure(col, weight=1)

        # Inicializar grid de células
        self.cells = {}
        for row in range(1, self.MAX_CILINDROS + 1):
            for col in range(5):
                if col == 0:
                    # Hacer la columna Cilindro más ancha
                    label = ttk.Label(self.table_content, text=f"Cilindro {row}", width=widths[0])
                else:
                    label = ttk.Label(self.table_content, text="", width=widths[col], relief="solid")
                    self.cells[(row, col)] = label
                label.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
    
    def validate_firing_order(self, event=None):
        """Valida el orden de encendido ingresado"""
        try:
            input_order = self.firing_order.get().split(',')
            order = [int(x.strip()) for x in input_order]
            num_cylinders = self.cylinders.get()
            
            # Validar longitud
            if len(order) > num_cylinders:
                order = order[:num_cylinders]
            elif len(order) < num_cylinders:
                # Completar con números faltantes
                used_nums = set(order)
                available_nums = [x for x in range(1, num_cylinders + 1) if x not in used_nums]
                order.extend(available_nums[:(num_cylinders - len(order))])
            
            # Actualizar el campo con el orden validado
            self.firing_order.set(",".join(map(str, order)))
            self.update_simulation_params()
            
        except (ValueError, AttributeError):
            self.restore_default_firing_order()
    
    def create_menu(self):
        """Crea el menú de la aplicación"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # Menú de simulación
        sim_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Simulación", menu=sim_menu)
        sim_menu.add_command(label="Reiniciar", command=self.reset_simulation)
        
        # Menú de red
        network_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Red", menu=network_menu)
        network_menu.add_command(label="Configurar WiFi", 
                            command=lambda: self.controller.show_wifi_config())
        network_menu.add_command(label="Estado de Red", 
                            command=lambda: self.controller.show_network_info())
    
    def show_wifi_config(self):
        """Muestra diálogo de configuración WiFi"""
        if hasattr(self, 'controller'):
            self.controller.show_wifi_config()
        else:
            messagebox.showerror("Error", "Controlador no inicializado")

    def show_network_info(self):
        """Muestra información de red"""
        if hasattr(self, 'controller'):
            self.controller.show_network_info()
        else:
            messagebox.showerror("Error", "Controlador no inicializado")

    def calculate_injector_positions(self, num_cylinders):
        """Calcula las posiciones de los inyectores en el canvas"""
        positions = []
        margin = 50
        
        # Ajustar espaciado según número de cilindros
        if num_cylinders > 8:
            base_spacing_x = 80  # Reducir espaciado para más cilindros
            base_spacing_y = 120
            canvas_width = 1000  # Aumentar ancho
            canvas_height = 900  # Aumentar alto
        else:
            base_spacing_x = 120
            base_spacing_y = 180
            canvas_width = 800
            canvas_height = 600

        # Configurar dimensiones del canvas
        self.canvas.configure(width=canvas_width, height=canvas_height)
        
        if self.configuration.get() == "En Línea":
            max_per_row = 6
            num_rows = (num_cylinders + max_per_row - 1) // max_per_row
            cylinders_per_row = min(max_per_row, (num_cylinders + num_rows - 1) // num_rows)
            
            for row in range(num_rows):
                start_cylinder = row * cylinders_per_row
                end_cylinder = min(start_cylinder + cylinders_per_row, num_cylinders)
                cylinders_this_row = end_cylinder - start_cylinder
                
                row_width = cylinders_this_row * base_spacing_x
                start_x = margin + (canvas_width - row_width) / 2
                base_y = margin + row * base_spacing_y
                
                for i in range(cylinders_this_row):
                    x = start_x + (i * base_spacing_x)
                    positions.append((x, base_y))
        else:
            # Configuración en V
            cylinders_per_bank = num_cylinders // 2
            extra_cylinder = num_cylinders % 2
            
            bank_width = max(cylinders_per_bank, cylinders_per_bank + extra_cylinder) * base_spacing_x
            start_x = margin + (canvas_width - bank_width) / 2
            
            # Banco superior
            for i in range(cylinders_per_bank):
                x = start_x + (i * base_spacing_x)
                positions.append((x, margin))
            
            # Banco inferior
            for i in range(cylinders_per_bank + extra_cylinder):
                x = start_x + (i * base_spacing_x)
                positions.append((x, margin + base_spacing_y))

        # Configurar región de scroll
        max_x = max(x for x, y in positions) + margin * 2
        max_y = max(y for x, y in positions) + margin * 2
        self.canvas.configure(scrollregion=(0, 0, max_x, max_y))
        
        return positions
    
    def create_injector_shape(self, x, y):
        """Crea la forma del inyector con mejor visualización"""
        # Ajustar tamaño según número de cilindros
        num_cylinders = self.cylinders.get()
        if num_cylinders > 8:
            width, height = 24, 48
            nozzle_width, nozzle_height = 8, 12
            font_size = 8
        else:
            width, height = 30, 60
            nozzle_width, nozzle_height = 10, 15
            font_size = 10

        parts = []
        
        # Cuerpo principal
        body = self.canvas.create_rectangle(
            x - width/2, y - height/2,
            x + width/2, y + height/2,
            outline='black', fill='white', width=2
        )
        parts.append(body)
        
        # Boquilla
        nozzle = self.canvas.create_polygon(
            x - nozzle_width/2, y + height/2,
            x + nozzle_width/2, y + height/2,
            x + nozzle_width/4, y + height/2 + nozzle_height,
            x - nozzle_width/4, y + height/2 + nozzle_height,
            outline='black', fill='white', width=2
        )
        parts.append(nozzle)
        
        return parts 
    
    def update_injectors(self):
        """Actualiza la visualización de los inyectores"""
        self.canvas.delete("all")
        self.injectors.clear()
        
        try:
            num_cylinders = min(self.cylinders.get(), 18)  # Asegurar máximo 18
            positions = self.calculate_injector_positions(num_cylinders)
            font_size = 9 if num_cylinders > 8 else 10
            
            for i, pos in enumerate(positions, 1):
                injector_parts = self.create_injector_shape(pos[0], pos[1])
                
                # Número de inyector
                num_text = self.canvas.create_text(
                    pos[0], pos[1] - 40,
                    text=f"Inyector {i}",
                    font=('Arial', font_size, 'bold')
                )
                
                # Estado
                state_text = self.canvas.create_text(
                    pos[0], pos[1],
                    text="",
                    font=('Arial', font_size - 1)
                )
                
                # Línea de spray
                spray_width = 8 if num_cylinders > 8 else 10
                spray_line = self.canvas.create_line(
                    pos[0], pos[1] + 35,
                    pos[0], pos[1] + 55,
                    width=spray_width, fill='yellow', state='hidden'
                )
                
                self.injectors[i] = {
                    'parts': injector_parts,
                    'num_text': num_text,
                    'state_text': state_text,
                    'spray_line': spray_line,
                    'position': pos
                }
                
        except Exception as e:
            print(f"Error al actualizar inyectores: {e}")
            self.update_status_bar("Error al actualizar visualización")

    def update_simulation_params(self):
        """Actualiza los parámetros de la simulación"""
        try:
            # Validar orden de encendido
            input_order = self.firing_order.get().split(',')
            order = [int(x.strip()) for x in input_order]
            num_cylinders = self.cylinders.get()
            
            # Validar que tenemos suficientes números en el orden
            while len(order) < num_cylinders:
                next_num = len(order) + 1
                if next_num not in order:
                    order.append(next_num)
            
            # Truncar si tenemos demasiados números
            order = order[:num_cylinders]
            
            # Validar que los números están en el rango correcto
            if not all(1 <= x <= num_cylinders for x in order):
                raise ValueError("Números fuera de rango")
            
            # Actualizar el orden de encendido
            self.custom_firing_order = order
            self.firing_order.set(",".join(map(str, order)))
            
            # Actualizar visualizaciones
            self.update_firing_table()
            self.update_injectors()
            self.calculate_rpm_equivalent()
            
        except (ValueError, AttributeError) as e:
            print(f"Error en configuración: {str(e)}")
            self.restore_default_firing_order()
    
    def on_cylinder_change(self, *args):
        """Maneja cambios en el número de cilindros"""
        try:
            num_cylinders = self.cylinders.get()
            
            # Validar límites
            if num_cylinders < self.MIN_CILINDROS:
                num_cylinders = self.MIN_CILINDROS
                self.cylinders.set(self.MIN_CILINDROS)
            elif num_cylinders > self.MAX_CILINDROS:
                num_cylinders = self.MAX_CILINDROS
                self.cylinders.set(self.MAX_CILINDROS)

            print(f"Número de cilindros actualizado a: {num_cylinders}")
            
            # Actualizar orden de encendido
            self.update_firing_order()
            
            # Actualizar visualización
            self.update_simulation_params()
            
            # Notificar al controlador si existe
            if hasattr(self, 'controller'):
                self.controller.update_motor_selection(None)
                
        except tk.TclError:
            # Si hay error en la conversión, restaurar valor por defecto
            self.cylinders.set(4)
            self.update_firing_order()    
            
    def update_firing_table(self):
        """Actualiza la tabla de tiempos del motor"""
        num_cylinders = self.cylinders.get()
        phases = ["Admisión", "Compresión", "Explosión", "Escape"]
        
        # Limpiar tabla existente
        for row in range(1, self.MAX_CILINDROS + 1):
            if (row, 1) in self.cells:
                if row <= num_cylinders:
                    for col in range(1, 5):
                        self.cells[(row, col)].grid()  # Mostrar celdas necesarias
                else:
                    for col in range(1, 5):
                        self.cells[(row, col)].grid_remove()  # Ocultar celdas extras
        
        # Actualizar estados según el orden de encendido actual
        firing_order = list(map(int, self.firing_order.get().split(',')))
        for cyl_num in range(1, num_cylinders + 1):
            phase_index = firing_order.index(cyl_num) if cyl_num in firing_order else 0
            for col in range(1, 5):
                if (cyl_num, col) in self.cells:
                    current_phase = phases[(phase_index + col - 1) % 4]
                    self.cells[(cyl_num, col)].configure(
                        text=current_phase,
                        background=self.state_colors[current_phase]
                    )

    def update_firing_order(self):
        """Actualiza el orden de encendido según el número de cilindros"""
        num_cylinders = self.cylinders.get()
        
        # Definir órdenes de encendido predeterminados
        if num_cylinders <= 6:
            default_order = ",".join(str(i) for i in range(1, num_cylinders + 1))
        elif num_cylinders == 8:
            default_order = "1,5,4,8,6,3,7,2"
        elif num_cylinders == 10:
            default_order = "1,6,2,7,3,8,4,9,5,10"
        elif num_cylinders == 12:
            default_order = "1,12,5,8,3,10,6,7,2,11,4,9"
        elif num_cylinders == 16:
            default_order = "1,16,8,9,3,14,6,11,2,15,7,10,4,13,5,12"
        elif num_cylinders == 18:
            default_order = "1,18,9,10,3,16,7,12,2,17,8,11,4,15,6,13,5,14"
        else:
            # Para números no estándar, generar orden secuencial
            default_order = ",".join(str(i) for i in range(1, num_cylinders + 1))
        
        print(f"Actualizando orden de encendido a: {default_order}")  # Debug
        self.firing_order.set(default_order)
    
    def calculate_rpm_equivalent(self):
        """Calcula las RPM equivalentes"""
        try:
            freq = float(self.frequency.get())
            # RPM = frecuencia * 60 segundos * (2 / cilindros)
            # El factor 2 es porque cada ciclo completo requiere 2 vueltas del cigüeñal
            rpm = freq * 60 * (2 / self.cylinders.get())
            self.rpm_equivalent.set(f"{rpm:.1f} RPM")
        except ValueError:
            self.rpm_equivalent.set("Error en frecuencia")
    
    def setup_initial_state(self):
        """Configura el estado inicial de la simulación"""
        # Inicializar variables
        self.custom_firing_order = list(map(int, self.firing_order.get().split(',')))
        
        # Actualizar visualizaciones
        self.update_simulation_params()
        
        # Actualizar estado
        self.update_status_bar("Sistema inicializado")
    
    def connect_controller(self, controller):
        """Conecta los eventos de la vista con el controlador"""
        self.controller = controller
        # Importante: cambiamos esto para usar el método de la vista directamente
        self.motor_selector.bind('<<ComboboxSelected>>', self.update_motor_selection)
        self.start_btn.config(command=controller.toggle_simulation)
        self.freq_slider.config(command=lambda e: controller.update_frequency())

    def update_simulation(self):
        """Actualiza el estado de la simulación en cada ciclo"""
        if self.running:
            try:
                freq = int(self.frequency.get())
                delay = int(1000 / freq)
                
                """ # Actualizar textos usando StringVar
                self.status_text.set("Estado: Activo")
                self.simulation_status.configure(foreground='green')
                self.freq_text.set(f"Frecuencia actual: {freq} Hz") """
                
                # Actualizar ciclo
                self.cycle_position = (self.cycle_position + 1) % 4
                self.update_all_states()
                
                # Programar siguiente actualización
                self.root.after(delay, self.update_simulation)
                
            except ValueError:
                print("Error en la frecuencia")
                self.stop_simulation()

    def reset_simulation(self):
        """Reinicia la simulación a su estado inicial"""
        self.running = False
        self.start_btn.config(text="Iniciar")
        self.cycle_position = 0
        self.update_firing_table()
        
        # Resetear inyectores
        for injector in self.injectors.values():
            for part in injector['parts']:
                self.canvas.itemconfig(part, fill='white')
            self.canvas.itemconfig(injector['spray_line'], state='hidden')
            self.canvas.itemconfig(injector['state_text'], text="")

        # Resetear tabla
        for row in range(1, self.cylinders.get() + 1):
            for col in range(1, 5):
                if (row, col) in self.cells:
                    self.cells[(row, col)].configure(background='white')

    def update_motor_selection(self, event):
        """Actualiza la configuración cuando se selecciona un nuevo motor"""
        if not hasattr(self, 'motor_selector'):
            return
            
        selected_motor = self.motor_selector.get()
        if selected_motor in self.motors:  # Verificar que el motor existe en la base de datos
            cylinders, firing_order, config = self.motors[selected_motor]
            
            # Actualizar valores de forma explícita
            self.cylinders.set(cylinders)  # Establecer número de cilindros
            self.firing_order.set(firing_order)  # Establecer orden de encendido
            self.configuration.set(config)  # Establecer configuración (En Línea/En V)
            
            # Forzar actualización de visualizaciones
            self.update_firing_table()  # Actualizar tabla
            self.update_injectors()  # Actualizar visualización de inyectores
            
            # Notificar al controlador
            if hasattr(self, 'controller'):
                self.controller.send_config_to_esp32()
            
            print(f"Motor actualizado: {selected_motor}")
            print(f"Cilindros: {cylinders}")
            print(f"Orden: {firing_order}")
            print(f"Configuración: {config}")

    def update_firing_order(self):
        """Actualiza el orden de encendido según el número de cilindros"""
        cylinders = self.cylinders.get()
        if cylinders <= 6:
            default_order = ",".join(str(i) for i in range(1, cylinders + 1))
        elif cylinders == 8:
            default_order = "1,5,4,8,6,3,7,2"
        elif cylinders == 10:
            default_order = "1,6,2,7,3,8,4,9,5,10"
        elif cylinders == 12:
            default_order = "1,12,5,8,3,10,6,7,2,11,4,9"
        self.firing_order.set(default_order)
        self.update_simulation_params()

    def update_frequency(self):
        """Actualiza la frecuencia y envía al ESP32"""
        try:
            if hasattr(self.view, 'frequency'):
                freq = float(self.view.frequency.get())
                config = {
                    "cilindros": self.view.cylinders.get(),
                    "orden": self.view.firing_order.get(),
                    "configuracion": self.view.configuration.get(),
                    "frecuencia": freq
                }
                self.send_config_to_esp32()
        except Exception as e:
            print(f"Error al actualizar frecuencia: {e}")
    
    def update_status_bar(self, message):
        """Actualiza la barra de estado con nuevo mensaje"""
        if hasattr(self, 'status_bar'):
            self.status_bar.configure(text=message)
            self.root.update_idletasks()
    
    def update_status_bar(self, message):
        """Actualiza la barra de estado"""
        self.status_bar.config(text=message)

    def update_injector_states(self, estados_dict):
        """Actualiza los estados de los inyectores en tiempo real"""
        num_cylinders = self.cylinders.get()
        estados = ["ADM", "COM", "EXP", "ESC"]
        orden = list(map(int, self.firing_order.get().split(',')))
        
        try:
            for i in range(num_cylinders):
                cyl_num = orden[i] if i < len(orden) else i + 1
                estado = estados[(self.cycle_position + i) % 4]
                
                if cyl_num in self.injectors:
                    injector = self.injectors[cyl_num]
                    color = self.state_colors[self.get_state_name(estado)]
                    
                    # Actualizar color del inyector
                    for part in injector['parts']:
                        self.canvas.itemconfig(part, fill=color)
                    
                    # Actualizar texto de estado
                    self.canvas.itemconfig(
                        injector['state_text'],
                        text=self.get_state_name(estado)
                    )
                    
                    # Actualizar línea de spray (amarilla)
                    spray_state = 'normal' if estado == 'EXP' else 'hidden'
                    self.canvas.itemconfig(injector['spray_line'], state=spray_state)
                    
                    # Actualizar tabla
                    self.update_cylinder_table(cyl_num, estado)
            
            self.root.update_idletasks()
                
        except Exception as e:
            print(f"Error en actualización: {e}")

    def update_simulation(self):
        """Actualiza el estado de la simulación en cada ciclo"""
        if self.running:
            try:
                freq = float(self.frequency.get())
                delay = int(1000 / freq)  # ms por ciclo completo
                
                # Actualizar ciclo
                self.cycle_position = (self.cycle_position + 1) % 4
                
                # Actualizar estados
                num_cylinders = self.cylinders.get()
                estados = {}
                orden = list(map(int, self.firing_order.get().split(',')))
                
                for i in range(num_cylinders):
                    cylinder = orden[i] if i < len(orden) else i + 1
                    estado_index = (self.cycle_position + i) % 4
                    estados[cylinder] = estado_index
                
                # Actualizar visualización
                self.update_injector_states(estados)
                
                # Programar siguiente actualización
                self.root.after(delay, self.update_simulation)
                
            except ValueError:
                print("Error en la frecuencia")
                self.running = False
                self.start_btn.config(text="Iniciar")
               
    def animate_spray(self, spray_line):
        """Anima la línea de spray"""
        self.canvas.itemconfig(spray_line, state='normal')
        
        def toggle_spray():
            if not self.running:
                return
            current_state = self.canvas.itemcget(spray_line, 'state')
            new_state = 'hidden' if current_state == 'normal' else 'normal'
            self.canvas.itemconfig(spray_line, state=new_state)
            
            if self.running:
                self.root.after(100, toggle_spray)
        
        toggle_spray()

    def restore_default_firing_order(self):
        """Restaura el orden de encendido por defecto según el número de cilindros"""
        num_cylinders = self.cylinders.get()
        
        if num_cylinders <= 6:
            default_order = ",".join(str(i) for i in range(1, num_cylinders + 1))
        elif num_cylinders == 8:
            default_order = "1,5,4,8,6,3,7,2"
        elif num_cylinders == 10:
            default_order = "1,6,2,7,3,8,4,9,5,10"
        elif num_cylinders == 12:
            default_order = "1,12,5,8,3,10,6,7,2,11,4,9"
        elif num_cylinders == 16:
            default_order = "1,16,8,9,3,14,6,11,2,15,7,10,4,13,5,12"
        elif num_cylinders == 18:
            default_order = "1,18,9,10,3,16,7,12,2,17,8,11,4,15,6,13,5,14"
        else:
            # Para números no estándar, crear orden secuencial
            default_order = ",".join(str(i) for i in range(1, num_cylinders + 1))
        
        self.firing_order.set(default_order)
        self.update_simulation_params()

    def update_all_states(self):
        """Actualiza todos los estados basados en el ciclo actual"""
        num_cylinders = self.cylinders.get()
        states = ["ADM", "COM", "EXP", "ESC"]
        estados = {}
        
        # Calcular estados para cada cilindro
        orden = list(map(int, self.firing_order.get().split(',')))
        for i in range(num_cylinders):
            cylinder = orden[i] if i < len(orden) else i + 1
            state_index = (self.cycle_position + i) % 4
            estados[cylinder] = states[state_index]
        
        # Actualizar visualización
        self.update_injector_states(estados)

    def toggle_simulation(self):
        """Inicia o detiene la simulación"""
        if not self.running:
            self.running = True
            self.start_btn.configure(text="Detener")
            freq = int(self.frequency.get())
            # Actualizar usando StringVar
            self.status_text.set("Estado: Activo")
            self.simulation_status.configure(foreground='green')
            self.freq_text.set(f"Frecuencia actual: {freq} Hz")
            self.cycle_position = 0
            self.update_simulation()
        else:
            self.stop_simulation()

    def reset_states(self):
        """Reinicia todos los estados a inactivo"""
        for injector in self.injectors.values():
            # Restaurar color blanco
            for part in injector['parts']:
                self.canvas.itemconfig(part, fill='white')
            # Ocultar spray
            self.canvas.itemconfig(injector['spray_line'], state='hidden')
            # Limpiar texto de estado
            self.canvas.itemconfig(injector['state_text'], text="")

        # Limpiar tabla
        for cell_key in self.cells:
            self.cells[cell_key].configure(text="", background='white')

    def get_phase_for_column(self, current_state, offset):
        """Calcula el estado para una columna específica basado en el estado actual"""
        estados = ['ADM', 'COM', 'EXP', 'ESC']
        if current_state not in estados:
            return 'OFF'
        current_index = estados.index(current_state)
        return estados[(current_index + offset) % 4]

    def create_status_indicators(self):
        """Crea indicadores de estado en la interfaz"""
        status_frame = ttk.Frame(self.control_frame)
        status_frame.grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")
        
        # Indicador de red
        self.network_indicator = ttk.Label(status_frame, text="●", font=('Arial', 12))
        self.network_indicator.pack(side="left", padx=5)
        
        # Barra de estado
        self.status_bar = ttk.Label(status_frame, text="Listo", relief="sunken")
        self.status_bar.pack(side="left", fill="x", expand=True, padx=5)

    def update_network_indicator(self, connected):
        """Actualiza el indicador de conexión de red"""
        if hasattr(self, 'network_indicator'):
            self.network_indicator.configure(
                foreground='green' if connected else 'red'
            )

    def _process_frequency_change(self):
        """Procesa cambios de frecuencia con limitación de rate"""
        self._frequency_update_pending = False
        self.update_frequency()

    def setup_bindings(self):
        """Configura los bindings de eventos"""
        self.frequency.trace_add("write", self.on_frequency_change)
        self.cylinders.trace_add("write", lambda *args: self.on_cylinder_change())
        self.firing_order.trace_add("write", lambda *args: self.validate_firing_order())
        
        # Binding para el slider de frecuencia
        self.freq_slider.configure(command=self.on_slider_change)

    def on_slider_change(self, value):
        """Maneja cambios en el slider de frecuencia"""
        try:
            freq = float(value)
            self.frequency.set(f"{freq:.2f}")
            if hasattr(self, 'controller'):
                self.controller.update_frequency()
        except ValueError as e:
            print(f"Error en slider: {e}")

    def update_simulation_speed(self):
        """Actualiza la velocidad de simulación basada en la frecuencia"""
        if self.running:
            try:
                freq = float(self.frequency.get())
                delay = int(1000 / (freq * 2))  # ms por ciclo
                self.root.after(delay, self.update_simulation)
            except ValueError:
                self.running = False
                self.start_btn.config(text="Iniciar")
                self.update_status_bar("Error en frecuencia")

    def update_cylinder_table(self, cylinder_num, current_state):
        """Actualiza la fila de la tabla para un cilindro específico"""
        try:
            estados_ciclo = ['ADM', 'COM', 'EXP', 'ESC']
            estados_nombres = {
                'ADM': 'Admisión',
                'COM': 'Compresión',
                'EXP': 'Explosión',
                'ESC': 'Escape',
                'OFF': 'Inactivo'
            }

            if current_state in estados_ciclo:
                current_index = estados_ciclo.index(current_state)
                for col in range(1, 5):
                    if (cylinder_num, col) in self.cells:
                        # Calcular el estado para esta columna
                        estado_index = (current_index + col - 1) % 4
                        estado = estados_ciclo[estado_index]
                        estado_nombre = estados_nombres[estado]
                        color = self.state_colors[estado_nombre]
                        
                        # Actualizar celda
                        self.cells[(cylinder_num, col)].configure(
                            text=estado_nombre,
                            background=color
                        )
            else:
                # Si el estado no es válido, mostrar inactivo
                for col in range(1, 5):
                    if (cylinder_num, col) in self.cells:
                        self.cells[(cylinder_num, col)].configure(
                            text="Inactivo",
                            background="white"
                        )
        except Exception as e:
            print(f"Error al actualizar tabla para cilindro {cylinder_num}: {e}")
            self.update_status_bar(f"Error en tabla - cilindro {cylinder_num}")
    
    def create_legend(self):
        """Crea una leyenda de colores para los estados"""
        legend_frame = ttk.LabelFrame(self.control_frame, text="Leyenda de Estados", 
                                    padding="5")
        legend_frame.grid(row=8, column=0, columnspan=2, pady=5, sticky="ew")

        # Grid de 2 columnas para la leyenda
        for i, (estado, color) in enumerate(self.state_colors.items()):
            if estado != 'Inactivo':  # No mostrar estado inactivo
                frame = ttk.Frame(legend_frame)
                frame.grid(row=i//2, column=i%2, padx=5, pady=2, sticky="w")
                
                # Indicador de color
                color_indicator = tk.Label(frame, bg=color, width=3, height=1)
                color_indicator.pack(side="left", padx=(0,5))
                
                # Nombre del estado
                ttk.Label(frame, text=estado).pack(side="left")

    def create_frequency_controls(self):
        """Crea los controles de frecuencia mejorados"""
        # Frame para controles de frecuencia
        freq_frame = ttk.LabelFrame(self.control_frame, text="Control de Frecuencia", padding="5")
        freq_frame.grid(row=4, column=0, columnspan=2, pady=5, sticky="ew")

        # Control de frecuencia con slider y entrada numérica
        control_frame = ttk.Frame(freq_frame)
        control_frame.pack(fill="x", expand=True, padx=5, pady=5)

        # Slider horizontal
        self.freq_slider = ttk.Scale(
            control_frame,
            from_=0.1,
            to=100.0,
            orient="horizontal",
            variable=self.frequency,
            command=self.on_slider_change
        )
        self.freq_slider.pack(side="left", fill="x", expand=True, padx=(0, 5))

        # Entrada numérica
        vcmd = (self.root.register(self.validate_frequency), '%P')
        self.freq_entry = ttk.Entry(
            control_frame,
            textvariable=self.frequency,
            width=8,
            validate='key',
            validatecommand=vcmd
        )
        self.freq_entry.pack(side="left")
        ttk.Label(control_frame, text="Hz").pack(side="left", padx=(2, 0))

        # RPM equivalentes
        rpm_frame = ttk.Frame(freq_frame)
        rpm_frame.pack(fill="x", pady=(5, 0))
        ttk.Label(rpm_frame, text="RPM Equivalentes:").pack(side="left")
        ttk.Label(rpm_frame, textvariable=self.rpm_equivalent).pack(side="left", padx=(5, 0))

    def validate_frequency(self, value):
        """Valida que la frecuencia sea un número entero"""
        if value == "":
            return True
        try:
            freq = int(value)  # Cambiar a int en lugar de float
            return 1 <= freq <= 100  # Validar rango
        except ValueError:
            return False

    def on_slider_change(self, value):
        """Maneja cambios en el slider"""
        try:
            freq = float(value)
            self.frequency.set(f"{freq:.2f}")
            self.calculate_rpm_equivalent()
            if hasattr(self, 'controller'):
                self.controller.send_config_to_esp32()
        except ValueError:
            pass

    def on_frequency_change(self, *args):
        """Maneja cambios en la frecuencia"""
        try:
            freq = int(self.frequency.get())
            if 1 <= freq <= 100:
                self.calculate_rpm_equivalent()
                if hasattr(self, 'controller'):
                    self.controller.update_frequency()
        except ValueError:
            pass

    def center_window(self):
        """Centra la ventana en la pantalla"""
        # Asegurar que la ventana está actualizada
        self.root.update_idletasks()
        
        # Obtener dimensiones de la ventana
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        
        # Calcular posición para centrar
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        
        # Establecer geometría
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def get_state_color(self, estado):
        """Obtiene el color correspondiente al estado"""
        estado_nombres = {
            'ADM': 'Admisión',
            'COM': 'Compresión',
            'EXP': 'Explosión',
            'ESC': 'Escape',
            'OFF': 'Inactivo'
        }
        estado_nombre = estado_nombres.get(estado, 'Inactivo')
        return self.state_colors.get(estado_nombre, 'white')

    def get_state_name(self, estado):
        """Obtiene el nombre completo del estado"""
        estados = {
            'ADM': 'Admisión',
            'COM': 'Compresión',
            'EXP': 'Explosión',
            'ESC': 'Escape',
            'OFF': 'Inactivo'
        }
        return estados.get(estado, 'Inactivo')

    def update_motor_selection(self, event):
        """Actualiza la configuración cuando se selecciona un nuevo motor"""
        try:
            # Obtener el motor seleccionado
            selected_motor = self.motor_selector.get()
            print(f"Motor seleccionado: {selected_motor}")  # Debug
            
            if selected_motor in self.motors:
                # Obtener la configuración del motor
                cylinders, firing_order, config = self.motors[selected_motor]
                print(f"Configuración obtenida: {cylinders} cilindros, orden {firing_order}, {config}")  # Debug
                
                # Actualizar valores de forma explícita
                self.cylinders.set(cylinders)
                self.firing_order.set(firing_order)
                self.configuration.set(config)
                
                # Forzar actualización de visualizaciones
                self.update_firing_table()  # Actualiza la tabla
                self.update_injectors()     # Actualiza los inyectores
                self.update_simulation_params()  # Actualiza otros parámetros
                
                # Actualizar también la frecuencia y RPM
                self.calculate_rpm_equivalent()
                
                # Si hay controlador, enviar al ESP32
                if hasattr(self, 'controller'):
                    self.controller.send_config_to_esp32()
                
                print("Actualización de motor completada")  # Debug
                self.update_status_bar(f"Motor actualizado: {selected_motor}")
        except Exception as e:
            print(f"Error al actualizar motor: {e}")
            self.update_status_bar("Error al actualizar motor")

    def stop_simulation(self):
        """Detiene la simulación"""
        self.running = False
        self.start_btn.configure(text="Iniciar")
        """ # Actualizar usando StringVar
        self.status_text.set("Estado: Detenido")
        self.simulation_status.configure(foreground='red')
        self.freq_text.set("Frecuencia actual: 0 Hz")
        self.reset_states() """

if __name__ == "__main__":
    root = tk.Tk()
    app = MotorSimulation(root)
    root.mainloop()
