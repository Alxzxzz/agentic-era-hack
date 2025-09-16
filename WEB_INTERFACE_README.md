# 🌐 Interfaz Web Personalizada - Agente de Optimización GCP

Esta interfaz web personalizada te permite interactuar con tu agente de optimización de infraestructura GCP a través de una interfaz HTML moderna, diferente al playground de ADK.

## 🎯 Diferencias con el Playground ADK

| Característica | Playground ADK (`make playground`) | Interfaz Personalizada (`make web`) |
|---|---|---|
| **Interfaz** | Interfaz de desarrollo ADK | HTML personalizado moderno |
| **Puerto** | 8501 | 8000 |
| **URL** | http://localhost:8501 | http://localhost:8000 |
| **Diseño** | Interfaz técnica de desarrollo | Diseño moderno y profesional |
| **Imágenes** | No genera imágenes | Genera imágenes automáticamente |
| **WebSocket** | No | Sí, para tiempo real |
| **Responsive** | No | Sí, funciona en móvil |

## ✨ Características de la Interfaz Personalizada

- **💬 Chat en tiempo real**: Interfaz de chat moderna con WebSocket
- **🎨 Generación de imágenes**: Visualizaciones automáticas con Vertex AI Imagen
- **📊 Análisis visual**: Diagramas de costos y arquitectura
- **🔄 Respuestas en streaming**: Respuestas en tiempo real del agente
- **📱 Diseño responsivo**: Funciona en desktop y móvil
- **🎨 UI moderna**: Diseño profesional con gradientes y animaciones

## 🚀 Cómo usar

### 1. Instalar dependencias

```bash
make install
```

### 2. Configurar autenticación GCP

```bash
gcloud auth application-default login
gcloud config set project TU_PROJECT_ID
```

### 3. Ejecutar la interfaz personalizada

```bash
make web
```

### 4. Acceder a la interfaz

Abre tu navegador en: **http://localhost:8000**

## 🔄 Comparación de Comandos

### Playground ADK (Interfaz de desarrollo)
```bash
make playground
# Accede a: http://localhost:8501
# Interfaz técnica de ADK
```

### Interfaz Personalizada (Interfaz HTML)
```bash
make web
# Accede a: http://localhost:8000
# Interfaz HTML personalizada
```

## 🎯 Funcionalidades del Agente

### Análisis de Infraestructura
- **Pregunta**: "Analiza mi infraestructura actual"
- **Respuesta**: Análisis completo de recursos GCP con costos

### Recomendaciones de Optimización
- **Pregunta**: "Genera recomendaciones de optimización"
- **Respuesta**: Sugerencias específicas para reducir costos

### Visualizaciones (Solo en interfaz personalizada)
- **Pregunta**: "Crea una visualización de costos"
- **Respuesta**: Diagrama visual generado automáticamente con Vertex AI Imagen

### Análisis de Recursos Costosos
- **Pregunta**: "¿Cuáles son mis recursos más costosos?"
- **Respuesta**: Lista priorizada de recursos por costo

## 🛠️ Arquitectura Técnica

### Backend (FastAPI)
- **`web_server.py`**: Servidor principal con endpoints REST y WebSocket
- **Integración**: Usa el agente existente sin modificarlo
- **Imágenes**: Generación automática con Vertex AI Imagen

### Frontend (HTML/CSS/JavaScript)
- **`templates/chat.html`**: Interfaz de chat moderna y responsiva
- **WebSocket**: Comunicación en tiempo real
- **CSS**: Diseño moderno con gradientes y animaciones

### Flujo de Datos
1. Usuario envía mensaje por WebSocket
2. Backend procesa mensaje con el agente ADK existente
3. Agente analiza infraestructura GCP
4. Si se solicita visualización, se genera imagen automáticamente
5. Respuesta se envía de vuelta por WebSocket
6. Frontend muestra texto e imágenes

## 🔧 Configuración

### Variables de Entorno

```bash
export GOOGLE_CLOUD_PROJECT="tu-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"
export GOOGLE_GENAI_USE_VERTEXAI="True"
```

### Dependencias

Las dependencias se instalan automáticamente con `make install`:
- `fastapi`: Servidor web
- `uvicorn`: Servidor ASGI
- `jinja2`: Templates HTML
- `python-multipart`: Soporte para formularios

## 🧪 Pruebas

Ejecuta las pruebas para verificar que todo funciona:

```bash
uv run python test_web_interface.py
```

## 🐛 Solución de Problemas

### Error de Autenticación
```bash
gcloud auth application-default login
gcloud config set project TU_PROJECT_ID
```

### Error de Dependencias
```bash
make install
```

### Error de Puerto en Uso
```bash
# Cambiar puerto en web_server.py
uvicorn.run(..., port=8001)
```

### Error de Generación de Imágenes
- Verifica que Vertex AI Imagen esté habilitado
- Revisa permisos de IAM
- El sistema continúa funcionando sin imágenes

## 📊 Monitoreo

### Logs del Servidor
Los logs se muestran en la consola donde ejecutas `make web`

### Métricas de Uso
- Número de sesiones activas
- Tiempo de respuesta del agente
- Errores de generación de imágenes

## 🚀 Despliegue en Producción

### Cloud Run
```bash
# Construir imagen
gcloud builds submit --tag gcr.io/PROJECT_ID/web-interface

# Desplegar
gcloud run deploy web-interface \
  --image gcr.io/PROJECT_ID/web-interface \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature
3. Haz commit de tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📝 Notas Importantes

- **No modifica el agente existente**: La interfaz usa el agente tal como está
- **Generación automática de imágenes**: Solo en la interfaz personalizada
- **Dos interfaces disponibles**: Playground ADK y HTML personalizada
- **Mismo agente, diferentes interfaces**: Ambas usan el mismo agente backend

---

¡Disfruta usando tu agente con una interfaz moderna! 🎉
