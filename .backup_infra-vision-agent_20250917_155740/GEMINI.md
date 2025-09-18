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

-   `app/`: Contiene toda la lógica del agente, las herramientas y la interacción con las APIs de GCP.
-   `.cloudbuild/`: Define los pipelines de CI/CD para Google Cloud Build (ej. `staging.yaml` para despliegue en staging y `pr_checks.yaml` para validaciones en Pull Requests).
-   `deployment/`: Contiene la configuración de Infraestructura como Código (IaC) usando **Terraform** para provisionar los recursos necesarios en GCP.
-   `tests/`: Alberga los tests unitarios, de integración y de carga (`locust`).
-   `Makefile`: Proporciona comandos de alto nivel para tareas comunes de desarrollo (instalar, probar, desplegar).
-   `pyproject.toml`: Define las dependencias del proyecto y la configuración de herramientas de linting y formato.

---

## 4. Flujo de Desarrollo y Despliegue

El proyecto está configurado para seguir las mejores prácticas de MLOps y DevOps.

### 4.1. Desarrollo Local

1.  **Instalación:** Se utiliza `uv` como gestor de paquetes. Las dependencias se instalan con:
    ```bash
    make install
    ```
2.  **Prueba Interactiva:** Se puede lanzar un playground web local para chatear con el agente:
    ```bash
    make playground
    ```
3.  **Tests Automatizados:** Se ejecutan los tests unitarios y de integración con:
    ```bash
    make test
    ```

### 4.2. Despliegue

-   **Entorno de Desarrollo en Cloud:** Se pueden provisionar recursos de desarrollo en GCP usando Terraform con:
    ```bash
    make setup-dev-env
    ```
-   **Despliegue en Agent Engine:** El agente se despliega en un entorno gestionado de Vertex AI Agent Engine con:
    ```bash
    make backend
    ```
-   **CI/CD Automatizado:** El repositorio utiliza **Google Cloud Build** para automatizar el despliegue. Al hacer merge a la rama principal, el pipeline definido en `.cloudbuild/staging.yaml` se ejecuta, desplegando el agente en el entorno de *staging*, ejecutando pruebas de carga y finalmente, disparando el despliegue a producción (que puede requerir aprobación manual).