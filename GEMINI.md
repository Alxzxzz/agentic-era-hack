# Documentación de IA para el Proyecto: infra-vision-agent

Este documento proporciona un análisis exhaustivo del proyecto `infra-vision-agent`, sirviendo como contexto centralizado para herramientas de desarrollo asistidas por IA y para la incorporación de nuevos desarrolladores.

---

## 1. Resumen del Proyecto

- **Nombre del Proyecto:** `infra-vision-agent`
- **Propósito Principal:** Actuar como un agente de IA especializado en la optimización de costos y análisis de infraestructura en **Google Cloud Platform (GCP)**.
- **Tecnología Core:** Construido sobre el **Agent Development Kit (ADK)** de Google, implementando un patrón de agente ReAct (Reasoning and Acting).

El agente está diseñado para interactuar en lenguaje natural, permitiendo a los usuarios solicitar análisis complejos sobre sus recursos de GCP, recibir recomendaciones de optimización y visualizar su infraestructura sin necesidad de consultar manualmente las consolas o APIs de GCP.

---

## 2. Arquitectura y Funcionalidades Clave

La funcionalidad del agente se centra en su capacidad para utilizar un conjunto de herramientas (`tools`) que interactúan directamente con los servicios de GCP.

### 2.1. El Agente Principal (`app/agent.py`)

- **Agente:** `root_agent` (instancia de `Agent` de ADK).
- **Nombre:** `infrastructure_vision_agent`.
- **Modelo IA:** `gemini-2.5-flash`.
- **Instrucciones (Persona):** Se le instruye para que actúe como un "Agente de Optimización de Costos de Infraestructura". Su rol es analizar la infraestructura de GCP, generar diagramas visuales y proporcionar recomendaciones para reducir costos.

### 2.2. Herramientas Disponibles para el Agente

El agente utiliza las siguientes funciones como herramientas para ejecutar las peticiones del usuario:

1.  **`set_project_id(project_id: str)`**
    - **Fuente:** `app/state_manager.py`
    - **Descripción:** Permite al usuario especificar el **ID del Proyecto de GCP** que desea analizar. Este estado se mantiene para las siguientes operaciones.

2.  **`analyze_infrastructure(query: str)`**
    - **Fuente:** `app/agent.py` (orquestando `app/infrastructure_analyzer.py`)
    - **Descripción:** Realiza un análisis completo de los recursos del proyecto GCP especificado. Devuelve un resumen detallado que incluye:
        - Lista de recursos detectados (VMs, Cloud SQL, GKE, Storage, etc.).
        - Desglose de costos mensuales estimados por recurso.
        - Un mapa de interconectividad básica entre los recursos.
    - **Fuente de Datos:** Utiliza **Google Cloud Asset Inventory** a través de la clase `GCPRealDataCollector` para obtener una lista real y granular de los recursos.

3.  **`get_google_cloud_recommendations(query: str)`**
    - **Fuente:** `app/agent.py` (orquestando `app/recommender_service.py`)
    - **Descripción:** Obtiene y formatea las recomendaciones de optimización oficiales proporcionadas por **Google Cloud Recommender API**.
    - **Categorías:** Las recomendaciones se agrupan por impacto: `COST`, `SECURITY`, `PERFORMANCE`, `RELIABILITY`.
    - **Ahorro Potencial:** Calcula y muestra el ahorro mensual total estimado si se aplican las recomendaciones de costo.

4.  **`generate_infrastructure_image(query: str)`**
    - **Fuente:** `app/agent.py`
    - **Descripción:** Genera una visualización (diagrama de arquitectura) de la infraestructura analizada.
    - **Proceso:**
        1.  Obtiene los datos de la infraestructura con `InfrastructureAnalyzer`.
        2.  Construye un *prompt* detallado que describe los recursos, sus costos y relaciones.
        3.  Utiliza un modelo de generación de imágenes de Gemini (`gemini-2.5-flash-image-preview`) para crear el diagrama.
        4.  Guarda la imagen resultante en el fichero `infrastructure_diagram.png`.

---

## 3. Estructura del Repositorio

```
infra-vision-agent/
├── app/                 # Core application code
│   ├── agent.py         # Main agent logic
│   ├── agent_engine_app.py # Agent Engine application logic
│   └── utils/           # Utility functions and helpers
├── .cloudbuild/         # CI/CD pipeline configurations for Google Cloud Build
├── deployment/          # Infrastructure and deployment scripts
├── notebooks/           # Jupyter notebooks for prototyping and evaluation
├── tests/               # Unit, integration, and load tests
├── Makefile             # Makefile for common commands
├── GEMINI.md            # AI-assisted development guide
└── pyproject.toml       # Project dependencies and configuration
```

---

## 4. Requisitos

Antes de comenzar, asegúrese de tener:
- **uv**: Python package manager (usado para toda la gestión de dependencias en este proyecto) - [Instalación](https://docs.astral.sh/uv/getting-started/installation/)
- **Google Cloud SDK**: Para servicios de GCP - [Instalación](https://cloud.google.com/sdk/docs/install)
- **Terraform**: Para el despliegue de infraestructura - [Instalación](https://developer.hashicorp.com/terraform/downloads)
- **make**: Herramienta de automatización de compilación - [Instalación](https://www.gnu.org/software/make/) (preinstalado en la mayoría de los sistemas basados en Unix)

---

## 5. Guía de Inicio Rápido (Pruebas Locales)

Instale los paquetes requeridos y lance el entorno de desarrollo local:

```bash
make install && make playground
```

---

## 6. Comandos

| Comando              | Descripción                                                                                 |
| -------------------- | ------------------------------------------------------------------------------------------- |
| `make install`       | Instalar todas las dependencias requeridas usando uv                                                  |
| `make playground`    | Lanzar la interfaz de Streamlit para probar el agente local y remotamente |
| `make backend`       | Desplegar el agente en Agent Engine |
| `make test`          | Ejecutar pruebas unitarias y de integración                                                              |
| `make lint`          | Ejecutar comprobaciones de calidad del código (codespell, ruff, mypy)                                             |
| `make setup-dev-env` | Configurar los recursos del entorno de desarrollo usando Terraform                         |
| `uv run jupyter lab` | Lanzar Jupyter notebook                                                                     |

Para obtener todas las opciones de comando y su uso, consulte el [Makefile](Makefile).

---

## 7. Uso

Este template sigue un enfoque "trae tu propio agente": te centras en tu lógica de negocio y el template se encarga de todo lo demás (UI, infraestructura, despliegue, monitorización).

1. **Prototipo:** Construye tu Agente de IA Generativa usando los notebooks de introducción en `notebooks/` como guía. Usa Vertex AI Evaluation para evaluar el rendimiento.
2. **Integración:** Importa tu agente en la aplicación editando `app/agent.py`.
3. **Prueba:** Explora la funcionalidad de tu agente usando el playground de Streamlit con `make playground`. El playground ofrece características como historial de chat, feedback de usuario y varios tipos de entrada, y recarga automáticamente tu agente en los cambios de código.
4. **Despliegue:** Configura e inicia los pipelines de CI/CD, personalizando las pruebas según sea necesario. Consulta la [sección de despliegue](#8-despliegue) para obtener instrucciones completas. Para un despliegue de infraestructura simplificado, simplemente ejecuta `uvx agent-starter-pack setup-cicd`.
5. **Monitorización:** Rastrea el rendimiento y recopila información usando Cloud Logging, Tracing y el panel de Looker Studio para iterar en tu aplicación.

---

## 8. Despliegue

> **Nota:** Para un despliegue simplificado en un solo comando de todo el pipeline de CI/CD y la infraestructura usando Terraform, puedes usar el comando `agent-starter-pack setup-cicd` de la CLI. Actualmente es compatible con GitHub y Google Cloud Build o GitHub Actions como ejecutores de CI/CD.

### Entorno de Desarrollo

Puedes probar el despliegue en un entorno de desarrollo usando el siguiente comando:

```bash
gcloud config set project <your-dev-project-id>
make backend
```

El repositorio incluye una configuración de Terraform para la configuración del proyecto de desarrollo de Google Cloud.
Consulta [deployment/README.md](deployment/README.md) para obtener instrucciones.

### Despliegue en Producción

El repositorio incluye una configuración de Terraform para la configuración de un proyecto de producción de Google Cloud. Consulta [deployment/README.md](deployment/README.md) para obtener instrucciones detalladas sobre cómo desplegar la infraestructura y la aplicación.

---

## 9. Monitorización y Observabilidad
> Puedes usar esta plantilla de [panel de Looker Studio](https://lookerstudio.google.com/reporting/46b35167-b38b-4e44-bd37-701ef4307418/page/tEnnC) para visualizar los eventos que se registran en BigQuery. Consulta la pestaña "Instrucciones de configuración" para comenzar.

La aplicación utiliza OpenTelemetry para una observabilidad completa, con todos los eventos enviados a Google Cloud Trace y Logging para monitorización y a BigQuery para almacenamiento a largo plazo.
