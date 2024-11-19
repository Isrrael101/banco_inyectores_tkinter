# Banco de Inyectores en Python

Este repositorio contiene un simulador de banco de inyectores desarrollado en Python. Utiliza **Tkinter** para la interfaz gráfica y una arquitectura basada en MVC (Modelo-Vista-Controlador) para separar la lógica de la aplicación, la interacción del usuario y la simulación del motor.

---

## 📋 Índice

- [Descripción](#📖-descripción)
- [Estructura del Proyecto](#🏗️-estructura-del-proyecto)
- [Instalación](#⚙️-instalación)
- [Uso](#🚀-uso)
- [Contribuciones](#🤝-contribuciones)
- [Licencia](#📜-licencia)

---

## 📖 Descripción

El **Simulador de Banco de Inyectores** permite simular el funcionamiento de un motor y su sistema de inyección mediante una interfaz gráfica intuitiva. Este proyecto es ideal para quienes desean experimentar con simulaciones relacionadas con motores y adquirir experiencia práctica en el desarrollo de software interactivo.

El sistema utiliza el patrón **Modelo-Vista-Controlador (MVC)** para:
- Mantener una estructura organizada.
- Facilitar la escalabilidad y el mantenimiento.
- Asegurar una clara separación entre la lógica del negocio, la presentación y la interacción del usuario.

---

## 🏗️ Estructura del Proyecto

El proyecto tiene la siguiente estructura:

```plaintext
.
├── motor_simulation_view.py      # Archivo para la Vista (Interfaz gráfica)
├── motor_controller.py           # Archivo para el Controlador (Lógica del sistema)
├── main.py                       # Archivo principal para ejecutar la aplicación
└── README.md                     # Este archivo, que explica el proyecto
