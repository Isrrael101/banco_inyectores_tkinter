#include <WiFi.h>
#include <WebServer.h>
#include <ArduinoJson.h>

// Configuración de red
#define MAX_CILINDROS 18
const char* AP_SSID = "BANCO_INYECTORES";
const char* AP_PASS = "12345678";
const char* STA_SSID = "";
const char* STA_PASS = "";

// Definición de pines para los inyectores
const int INYECTOR_PINS[MAX_CILINDROS] = {
    13, 12, 14, 27,  // Inyectores 1-4
    26, 25, 33, 32,  // Inyectores 5-8
    15,  2,  0,  4,  // Inyectores 9-12
    16, 17,  5, 18,  // Inyectores 13-16
    19, 21           // Inyectores 17-18
};

// Servidor web
WebServer server(80);

// Variables de estado
bool isAP = true;
bool simulacionActiva = false;
unsigned long ultimoTiempo = 0;
int posicionCiclo = 0;

// Estructura para la configuración del motor
struct ConfiguracionMotor {
    int numCilindros;
    String ordenEncendido;
    String configuracion;
    float frecuencia;
    int ordenArray[MAX_CILINDROS];
} configMotor;

// Estados posibles de los inyectores
enum EstadoInyector {
    ADMISION,
    COMPRESION,
    EXPLOSION,
    ESCAPE,
    INACTIVO
};

// Array de estados de los inyectores
EstadoInyector estadosInyectores[MAX_CILINDROS];

// Nombres de los estados para el monitor serial
const char* nombresEstados[] = {"ADM", "COM", "EXP", "ESC", "OFF"};

// Colores para los estados
const char* ESTADO_COLORS[] = {
    "#90EE90",  // ADM - Verde claro
    "#FFB6C1",  // COM - Rosa claro
    "#FF6B6B",  // EXP - Rojo
    "#87CEEB",  // ESC - Azul claro
    "#FFFFFF"   // OFF - Blanco
};

// Funciones de actualización y control
void actualizarOrdenEncendido() {
    String orden = configMotor.ordenEncendido;
    int index = 0;
    
    // Limpiar array actual
    for (int i = 0; i < MAX_CILINDROS; i++) {
        configMotor.ordenArray[i] = 0;
    }
    
    // Parsear string de orden
    while (orden.length() > 0 && index < configMotor.numCilindros) {
        int coma = orden.indexOf(',');
        if (coma == -1) {
            configMotor.ordenArray[index++] = orden.toInt();
            break;
        }
        String numero = orden.substring(0, coma);
        configMotor.ordenArray[index++] = numero.toInt();
        orden = orden.substring(coma + 1);
    }
    
    Serial.print("Orden actualizado: ");
    for (int i = 0; i < configMotor.numCilindros; i++) {
        Serial.print(configMotor.ordenArray[i]);
        Serial.print(" ");
    }
    Serial.println();
}

void reiniciarEstados() {
    for (int i = 0; i < MAX_CILINDROS; i++) {
        estadosInyectores[i] = INACTIVO;
        digitalWrite(INYECTOR_PINS[i], LOW);
    }
    posicionCiclo = 0;
    Serial.println("Estados reiniciados");
    enviarEstadosPorSerial();
}

void iniciarWiFiAP() {
    WiFi.disconnect();
    delay(100);
    WiFi.mode(WIFI_AP);
    WiFi.softAP(AP_SSID, AP_PASS);
    isAP = true;
    
    Serial.println("=== Modo AP Iniciado ===");
    Serial.printf("SSID: %s\n", AP_SSID);
    Serial.printf("Password: %s\n", AP_PASS);
    Serial.printf("IP AP: %s\n", WiFi.softAPIP().toString().c_str());
}

void iniciarWiFiSTA() {
    WiFi.disconnect();
    delay(100);
    WiFi.mode(WIFI_STA);
    WiFi.begin(STA_SSID, STA_PASS);
    
    Serial.print("Conectando a WiFi");
    int intentos = 0;
    while (WiFi.status() != WL_CONNECTED && intentos < 20) {
        delay(500);
        Serial.print(".");
        intentos++;
    }
    Serial.println();
    
    if (WiFi.status() == WL_CONNECTED) {
        isAP = false;
        Serial.println("=== Modo STA Activo ===");
        Serial.printf("Conectado a: %s\n", STA_SSID);
        Serial.printf("IP: %s\n", WiFi.localIP().toString().c_str());
        Serial.printf("RSSI: %d dBm\n", WiFi.RSSI());
    } else {
        Serial.println("\nError de conexión STA, volviendo a modo AP");
        iniciarWiFiAP();
    }
}

void actualizarSalidasFisicas() {
    // Activar las salidas según el estado
    for (int i = 0; i < configMotor.numCilindros; i++) {
        // Solo activar el pin si está en estado de explosión
        bool activo = (estadosInyectores[i] == EXPLOSION);
        digitalWrite(INYECTOR_PINS[i], activo ? HIGH : LOW);
        
        // Debug por serial
        if (activo) {
            Serial.printf("Activando inyector %d (PIN %d)\n", i+1, INYECTOR_PINS[i]);
        }
    }
}

void actualizarEstadosInyectores() {
    if (!simulacionActiva) {
        for (int i = 0; i < MAX_CILINDROS; i++) {
            digitalWrite(INYECTOR_PINS[i], LOW);
        }
        return;
    }

    unsigned long tiempoActual = millis();
    unsigned long intervalo = (1000.0 / configMotor.frecuencia);

    if (tiempoActual - ultimoTiempo >= intervalo) {
        posicionCiclo = (posicionCiclo + 1) % 4;

        // Debug del orden de encendido
        Serial.print("Orden de encendido: ");
        for(int i = 0; i < configMotor.numCilindros; i++) {
            Serial.printf("%d ", configMotor.ordenArray[i]);
        }
        Serial.println();

        // Actualizar estados y salidas
        for (int i = 0; i < configMotor.numCilindros; i++) {
            // El índice del cilindro es el valor en ordenArray menos 1
            int cilindro = configMotor.ordenArray[i] - 1;
            // Asegurar que el índice es válido
            if (cilindro >= 0 && cilindro < MAX_CILINDROS) {
                // Calcular estado
                estadosInyectores[cilindro] = (EstadoInyector)((posicionCiclo + i) % 4);
                
                // Activar salida si está en explosión
                if (estadosInyectores[cilindro] == EXPLOSION) {
                    digitalWrite(INYECTOR_PINS[cilindro], HIGH);
                    Serial.printf("Activando inyector %d en pin %d\n", cilindro + 1, INYECTOR_PINS[cilindro]);
                } else {
                    digitalWrite(INYECTOR_PINS[cilindro], LOW);
                }
            }
        }
        
        ultimoTiempo = tiempoActual;
    }
}

void enviarEstadosPorSerial() {
    String mensaje = "Estados => \n";
    for (int i = 0; i < configMotor.numCilindros; i++) {
        if (i > 0 && i % 6 == 0) mensaje += "\n";
        mensaje += "C" + String(i + 1) + ":" + 
                  String(nombresEstados[estadosInyectores[i]]) + " ";
    }
    Serial.println(mensaje);
}

// Función para enviar actualizaciones al Serial Monitor Web
void enviarActualizacionSerial() {
    static unsigned long ultimaActualizacion = 0;
    const unsigned long INTERVALO_ACTUALIZACION = 200; // 200ms entre actualizaciones
    
    unsigned long tiempoActual = millis();
    if (tiempoActual - ultimaActualizacion >= INTERVALO_ACTUALIZACION) {
        ultimaActualizacion = tiempoActual;
        
        DynamicJsonDocument doc(1024);
        doc["type"] = "serial";
        
        // Estado actual
        String estado = "Estados => ";
        for (int i = 0; i < configMotor.numCilindros; i++) {
            estado += "C" + String(i + 1) + ":" + nombresEstados[estadosInyectores[i]] + " ";
            if ((i + 1) % 6 == 0) estado += "\n           ";
        }
        
        doc["message"] = estado;
        String serialData;
        serializeJson(doc, serialData);
        
        // Usar el cliente web para enviar la actualización
        server.send(200, "application/json", serialData);
    }
}

String obtenerEstadoJSON() {
    DynamicJsonDocument doc(2048);
    
    doc["modo"] = isAP ? "AP" : "STA";
    doc["ip"] = isAP ? WiFi.softAPIP().toString() : WiFi.localIP().toString();
    if (!isAP) {
        doc["rssi"] = WiFi.RSSI();
    }
    
    doc["cilindros"] = configMotor.numCilindros;
    doc["orden"] = configMotor.ordenEncendido;
    doc["configuracion"] = configMotor.configuracion;
    doc["frecuencia"] = configMotor.frecuencia;
    doc["activo"] = simulacionActiva;

    JsonArray estados = doc.createNestedArray("estados");
    for (int i = 0; i < configMotor.numCilindros; i++) {
        estados.add(nombresEstados[estadosInyectores[i]]);
    }
    
    String response;
    serializeJson(doc, response);
    return response;
}

// Manejadores del servidor web
void handleRoot() {
    String html = "<!DOCTYPE html><html><head>";
    html += "<meta charset='UTF-8'>";
    html += "<title>Monitor de Inyectores</title>";
    
    // Estilos CSS
    html += "<style>";
    html += "body{font-family:Arial,sans-serif;margin:20px;background-color:#f0f0f0}";
    html += ".container{max-width:600px;margin:0 auto;text-align:center}";  // Centrado
    html += ".info-card{background:white;border-radius:8px;padding:20px;margin:20px auto;box-shadow:0 2px 4px rgba(0,0,0,0.1)}";
    html += ".value{font-size:24px;font-weight:bold;color:#007bff;margin:10px 0}";
    html += "</style>";

    // Script para actualización dinámica
    html += "<script>";
    html += "function updateValues(){";
    html += "  fetch('/estado')";
    html += "    .then(response=>response.json())";
    html += "    .then(data=>{";
    html += "      document.getElementById('frecuencia').textContent=data.frecuencia.toFixed(0) + ' Hz';";  // Sin decimales
    html += "      document.getElementById('rpm').textContent=((data.frecuencia * 60)/data.cilindros * 2).toFixed(1) + ' RPM';";
    html += "    });";
    html += "}";
    html += "setInterval(updateValues,100);"; // Actualizar cada 100ms
    html += "</script></head>";

    // Contenido HTML
    html += "<body><div class='container'>";
    html += "<div class='info-card'>";
    html += "<h2>Frecuencia Motor</h2>";
    html += "<div class='value' id='frecuencia'>0 Hz</div>";
    html += "</div>";
    html += "<div class='info-card'>";
    html += "<h2>RPM Equivalentes</h2>";
    html += "<div class='value' id='rpm'>0.0 RPM</div>";
    html += "</div>";
    html += "</div></body></html>";

    server.send(200, "text/html", html);
}

void handleRoot2() {
    String html = ""; // Continuación del HTML
    
    // Panel de Control Principal
    html += "<div class='card'>";
    html += "<h2>Panel de Control</h2>";
    html += "<div class='controls'>";
    html += "<button class='btn btn-primary' id='startBtn' onclick='toggleSimulation(true)'>Iniciar Simulación</button>";
    html += "<button class='btn btn-danger' id='stopBtn' style='display:none' onclick='toggleSimulation(false)'>Detener Simulación</button>";
    html += "<button class='btn btn-primary' onclick='toggleWiFiMode()'>Cambiar Modo WiFi</button>";
    html += "</div>";
    html += "</div>";

    // Estado del Sistema
    html += "<div class='card'>";
    html += "<h2>Estado del Sistema</h2>";
    html += "<div class='system-info'>";
    html += "<p><strong>Modo WiFi: </strong><span id='modo'>" + String(isAP ? "AP" : "STA") + "</span></p>";
    html += "<p><strong>IP: </strong><span id='ip'>" + String(isAP ? WiFi.softAPIP().toString() : WiFi.localIP().toString()) + "</span></p>";
    if (!isAP) {
        html += "<p><strong>RSSI: </strong><span id='rssi'>" + String(WiFi.RSSI()) + " dBm</span></p>";
    }
    html += "<p><strong>Estado: </strong><span id='status' class='" + String(simulacionActiva ? "status-good" : "status-bad") + "'>";
    html += simulacionActiva ? "ACTIVO" : "DETENIDO";
    html += "</span></p>";
    html += "</div>";
    html += "</div>";

    // Configuración del Motor
    html += "<div class='card'>";
    html += "<h2>Configuración del Motor</h2>";
    html += "<p><strong>Cilindros: </strong><span id='cylinders'>" + String(configMotor.numCilindros) + "</span></p>";
    html += "<p><strong>Orden de Encendido: </strong><span id='order'>" + configMotor.ordenEncendido + "</span></p>";
    html += "<p><strong>Configuración: </strong><span id='configuration'>" + configMotor.configuracion + "</span></p>";
    html += "<p><strong>Frecuencia: </strong><span id='frequency'>" + String(configMotor.frecuencia, 2) + "</span> Hz</p>";
    html += "</div>";

    // Visualización de Inyectores
    html += "<div class='card'>";
    html += "<h2>Estado de los Inyectores</h2>";
    html += "<div class='injector-grid'>";
    
    for (int i = 0; i < configMotor.numCilindros; i++) {
        String estadoActual = nombresEstados[estadosInyectores[i]];
        String color = ESTADO_COLORS[estadosInyectores[i]];
        bool esExplosion = (estadosInyectores[i] == EXPLOSION);
        
        html += "<div class='injector-card' id='injector-" + String(i) + "'>";
        html += "<h3>Inyector " + String(i + 1) + "</h3>";
        html += "<div class='state-indicator" + String(esExplosion ? " explosion" : "") + "'";
        html += " style='background-color: " + color + "'></div>";
        html += "<p class='state-text'>" + estadoActual + "</p>";
        html += "</div>";
    }
    
    html += "</div>"; // cierra injector-grid
    html += "</div>"; // cierra card

    // Monitor Serial Web
    html += "<div class='card'>";
    html += "<h2>Monitor Serial</h2>";
    html += "<div id='serial-monitor' style='height:200px;overflow-y:auto;background:#000;color:#0f0;padding:10px;font-family:monospace'>";
    html += "</div>";
    html += "</div>";

    // Script adicional para el monitor serial
    html += "<script>";
    html += "function updateSerialMonitor(message) {";
    html += "  const monitor = document.getElementById('serial-monitor');";
    html += "  const date = new Date().toLocaleTimeString();";
    html += "  monitor.innerHTML += `[${date}] ${message}<br>`;";
    html += "  monitor.scrollTop = monitor.scrollHeight;";
    html += "}";
    html += "</script>";

    html += "</div></body></html>"; // Cierra container y body
    
    server.send(200, "text/html", html);
}

// Modificar handleEstado para incluir más información
void handleEstado() {
    DynamicJsonDocument doc(2048);
    String response;
    
    doc["modo"] = isAP ? "AP" : "STA";
    doc["ip"] = isAP ? WiFi.softAPIP().toString() : WiFi.localIP().toString();
    if (!isAP) {
        doc["rssi"] = WiFi.RSSI();
    }
    
    doc["cilindros"] = configMotor.numCilindros;
    doc["orden"] = configMotor.ordenEncendido;
    doc["configuracion"] = configMotor.configuracion;
    doc["frecuencia"] = configMotor.frecuencia;
    doc["activo"] = simulacionActiva;

    // Crear array de estados
    JsonArray estados = doc.createNestedArray("estados");
    for (int i = 0; i < configMotor.numCilindros; i++) {
        switch (estadosInyectores[i]) {
            case ADMISION: estados.add("ADM"); break;
            case COMPRESION: estados.add("COM"); break;
            case EXPLOSION: estados.add("EXP"); break;
            case ESCAPE: estados.add("ESC"); break;
            default: estados.add("OFF"); break;
        }
    }

    serializeJson(doc, response);
    Serial.println("Enviando estados: " + response); // Debug
    server.send(200, "application/json", response);
}

// Manejador de configuración mejorado
void handleConfig() {
    if (server.hasArg("plain")) {
        String json = server.arg("plain");
        Serial.println("Configuración recibida: " + json);
        
        DynamicJsonDocument doc(1024);
        DeserializationError error = deserializeJson(doc, json);
        
        if (!error) {
            configMotor.numCilindros = doc["cilindros"].as<int>();
            String orden = doc["orden"].as<String>();
            configMotor.frecuencia = doc["frecuencia"].as<float>();
            
            Serial.printf("Cilindros: %d\n", configMotor.numCilindros);
            Serial.printf("Orden: %s\n", orden.c_str());
            Serial.printf("Frecuencia: %.2f\n", configMotor.frecuencia);
            
            // Parsear orden de encendido
            int index = 0;
            while (orden.length() > 0 && index < configMotor.numCilindros) {
                int coma = orden.indexOf(',');
                if (coma == -1) {
                    configMotor.ordenArray[index++] = orden.toInt();
                    break;
                }
                String numero = orden.substring(0, coma);
                configMotor.ordenArray[index++] = numero.toInt();
                orden = orden.substring(coma + 1);
            }
            
            // Debug del orden parseado
            Serial.print("Orden parseado: ");
            for(int i = 0; i < configMotor.numCilindros; i++) {
                Serial.printf("%d ", configMotor.ordenArray[i]);
            }
            Serial.println();
            
            server.send(200, "application/json", "{\"success\":true,\"message\":\"Configuración actualizada\"}");
        } else {
            server.send(400, "application/json", "{\"success\":false,\"message\":\"Error en formato JSON\"}");
        }
    }
}

// Manejador de simulación mejorado
void handleSimulacion() {
    String response;
    DynamicJsonDocument respDoc(256);
    
    if (server.hasArg("plain")) {
        DynamicJsonDocument doc(256);
        DeserializationError error = deserializeJson(doc, server.arg("plain"));
        
        if (!error) {
            String action = doc["action"].as<String>();
            
            if (action == "start") {
                simulacionActiva = true;
                posicionCiclo = 0;
                respDoc["success"] = true;
                respDoc["message"] = "Simulación iniciada";
                respDoc["estado"] = "activo";
                
                Serial.println("Simulación iniciada");
                Serial.println("Estado inicial de inyectores:");
                enviarEstadosPorSerial();
                
            } else if (action == "stop") {
                simulacionActiva = false;
                reiniciarEstados();
                respDoc["success"] = true;
                respDoc["message"] = "Simulación detenida";
                respDoc["estado"] = "detenido";
                
                Serial.println("Simulación detenida");
                
            } else {
                respDoc["success"] = false;
                respDoc["message"] = "Acción no válida";
                respDoc["estado"] = simulacionActiva ? "activo" : "detenido";
            }
        } else {
            respDoc["success"] = false;
            respDoc["message"] = "Error en formato JSON";
        }
    } else {
        respDoc["success"] = false;
        respDoc["message"] = "Sin datos";
    }
    
    serializeJson(respDoc, response);
    server.send(200, "application/json", response);
}

void handleModoWiFi() {
    if (isAP) {
        iniciarWiFiSTA();
    } else {
        iniciarWiFiAP();
    }
    server.send(200, "text/plain", "Modo WiFi cambiado");
}

void configurarServidor() {
    // Configurar rutas
    server.on("/", HTTP_GET, []() {
        handleRoot();
        handleRoot2();  // Enviar segunda parte del HTML
    });
    server.on("/estado", HTTP_GET, handleEstado);
    server.on("/config", HTTP_POST, handleConfig);
    server.on("/simulacion", HTTP_POST, handleSimulacion);
    server.on("/modo-wifi", HTTP_POST, handleModoWiFi);
    
    // Habilitar CORS
    server.enableCORS(true);
    
    server.begin();
    Serial.println("Servidor HTTP iniciado");
}

// Función para enviar mensajes al monitor serial web
void enviarMensajeWeb(String mensaje) {
    DynamicJsonDocument doc(512);
    doc["type"] = "serial";
    doc["message"] = mensaje;
    
    String response;
    serializeJson(doc, response);
    // Este mensaje será capturado por el cliente web
    server.send(200, "application/json", response);
}

// Función para manejar cambios desde Python
void handlePythonUpdate() {
    if (server.hasArg("plain")) {
        DynamicJsonDocument doc(1024);
        DeserializationError error = deserializeJson(doc, server.arg("plain"));
        
        if (!error) {
            bool updated = false;
            String updateMsg = "Actualización desde Python:\n";
            
            // Procesar actualizaciones
            if (doc.containsKey("frecuencia")) {
                float nuevaFrec = doc["frecuencia"];
                if (nuevaFrec != configMotor.frecuencia) {
                    configMotor.frecuencia = nuevaFrec;
                    updateMsg += "Frecuencia: " + String(nuevaFrec) + " Hz\n";
                    updated = true;
                }
            }
            
            // ... más actualizaciones según necesites
            
            if (updated) {
                Serial.println(updateMsg);
                server.send(200, "application/json", "{\"success\":true,\"message\":\"" + updateMsg + "\"}");
            } else {
                server.send(200, "application/json", "{\"success\":true,\"message\":\"No hay cambios\"}");
            }
        } else {
            server.send(400, "application/json", "{\"success\":false,\"message\":\"Error en formato JSON\"}");
        }
    }
}

void setup() {
    Serial.begin(115200);
    Serial.println("\nIniciando Simulador de Inyectores...");

    // Configurar pines
    for(int i = 0; i < MAX_CILINDROS; i++) {
        pinMode(INYECTOR_PINS[i], OUTPUT);
        digitalWrite(INYECTOR_PINS[i], LOW);
        Serial.printf("Configurando PIN %d para inyector %d\n", INYECTOR_PINS[i], i+1);
    }

    // Configuración inicial del motor
    configMotor.numCilindros = 4;
    configMotor.ordenEncendido = "1,3,4,2";
    configMotor.configuracion = "En Línea";
    configMotor.frecuencia = 1.0;
    
    actualizarOrdenEncendido();
    reiniciarEstados();
    
    // Iniciar WiFi y servidor
    iniciarWiFiAP();
    configurarServidor();

    Serial.println("Sistema iniciado y listo");
}

// Actualizar loop para incluir actualizaciones seriales
void loop() {
    server.handleClient();
    
    // Solo actualizar estados si la simulación está activa
    if (simulacionActiva) {
        actualizarEstadosInyectores();
    }
    
    // Pequeña pausa para evitar watchdog reset
    delay(1);
}