#!/usr/bin/env python3
"""
Servidor web personalizado para el agente de optimización GCP
Integra con el agente existente sin modificarlo
"""

import asyncio
import json
import logging
import os
import base64
from datetime import datetime
from typing import Dict, Any, Optional

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Importar el agente existente
from app.agent import root_agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Crear aplicación FastAPI
app = FastAPI(
    title="Agente de Optimización GCP - Interfaz Personalizada",
    description="Interfaz web personalizada para el agente de análisis de infraestructura GCP",
    version="1.0.0"
)

# Configurar templates
templates = Jinja2Templates(directory="templates")

# Modelos Pydantic
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    images: Optional[list] = None
    session_id: str
    timestamp: str

# Servicio de sesiones
session_service = InMemorySessionService()

# Clase para manejar conexiones WebSocket
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket
        logger.info(f"Conexión WebSocket establecida para sesión: {session_id}")

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            logger.info(f"Conexión WebSocket cerrada para sesión: {session_id}")

    async def send_message(self, message: str, session_id: str):
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_text(message)

manager = ConnectionManager()

# Función para generar imágenes con Vertex AI
async def generate_infrastructure_image(resources: Dict) -> Optional[str]:
    """Genera una imagen de infraestructura usando Vertex AI Imagen"""
    try:
        import vertexai
        from vertexai.preview.vision_models import ImageGenerationModel
        
        # Inicializar Vertex AI
        project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        vertexai.init(project=project_id, location="us-central1")
        
        # Crear modelo
        model = ImageGenerationModel.from_pretrained("imagegeneration@006")
        
        # Crear prompt detallado
        prompt = f"""
        Crea un diagrama profesional de arquitectura de Google Cloud Platform que muestre:
        
        INFRAESTRUCTURA ACTUAL:
        - {len(resources.get('vms', []))} instancias de Compute Engine (VMs)
        - {len(resources.get('databases', []))} bases de datos Cloud SQL
        - {len(resources.get('storage', []))} buckets de Cloud Storage
        - {len(resources.get('clusters', []))} clusters GKE
        - {len(resources.get('redis_instances', []))} instancias Memorystore Redis
        - {len(resources.get('spanner_instances', []))} instancias Spanner
        - Costo total mensual: ${resources.get('total_monthly_cost', 0)}
        
        ESTILO VISUAL:
        - Diagrama de arquitectura profesional estilo Google Cloud
        - Iconos oficiales de GCP (Compute Engine, Cloud SQL, Cloud Storage, GKE, Redis, Spanner)
        - Colores corporativos de Google (azul, verde, rojo, amarillo)
        - Layout limpio y organizado
        - Texto en español
        - Indicadores de costo en cada servicio
        - Flechas mostrando flujo de datos
        
        ELEMENTOS A INCLUIR:
        - Título: "Arquitectura GCP - Análisis de Costos"
        - Cada servicio con su icono y costo mensual
        - Conexiones entre servicios
        - Leyenda de colores para diferentes tipos de recursos
        - Métricas de uso y optimización
        
        El diagrama debe ser claro, profesional y fácil de entender para análisis de costos.
        """
        
        # Generar imagen
        response = model.generate_images(
            prompt=prompt,
            number_of_images=1,
            language="es",
            safety_filter_level="block_some",
            person_generation="dont_allow"
        )
        
        if response.images:
            # Convertir a base64
            image = response.images[0]
            image_bytes = image._image_bytes
            base64_string = base64.b64encode(image_bytes).decode('utf-8')
            return f"data:image/png;base64,{base64_string}"
        
        return None
        
    except Exception as e:
        logger.error(f"Error generando imagen: {e}")
        return None

# Función para procesar mensajes del agente
async def process_agent_message(user_message: str, session_id: str) -> Dict[str, Any]:
    """Procesa un mensaje del usuario a través del agente existente"""
    try:
        # Crear o obtener sesión
        try:
            await session_service.create_session(
                app_name="infra_vision_agent",
                user_id="web_user",
                session_id=session_id
            )
        except Exception:
            # La sesión ya existe
            pass

        # Crear runner con el agente existente
        runner = Runner(
            agent=root_agent,
            app_name="infra_vision_agent",
            session_service=session_service
        )

        # Procesar mensaje
        response_text = ""
        images = []
        
        async for event in runner.run_async(
            user_id="web_user",
            session_id=session_id,
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=user_message)]
            ),
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, 'text') and part.text:
                            response_text += part.text

        # Verificar si la respuesta indica que se debe generar una imagen
        if "visualización" in response_text.lower() or "diagrama" in response_text.lower():
            try:
                from app.infrastructure_analyzer import InfrastructureAnalyzer
                from app.state_manager import get_project_id
                
                project_id = get_project_id() or os.getenv("GOOGLE_CLOUD_PROJECT")
                analyzer = InfrastructureAnalyzer(project_id)
                resources = analyzer.get_infrastructure_summary()
                
                # Generar imagen
                image_data = await generate_infrastructure_image(resources)
                if image_data:
                    images.append(image_data)
                    
            except Exception as e:
                logger.warning(f"No se pudo generar imagen: {e}")

        return {
            "response": response_text,
            "images": images,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error procesando mensaje: {e}")
        return {
            "response": f"Error procesando tu consulta: {str(e)}",
            "images": [],
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }

# Rutas de la API
@app.get("/", response_class=HTMLResponse)
async def get_chat_interface(request: Request):
    """Servir la interfaz de chat personalizada"""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(message: ChatMessage):
    """Endpoint para enviar mensajes al agente"""
    session_id = message.session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    result = await process_agent_message(message.message, session_id)
    return ChatResponse(**result)

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket para chat en tiempo real"""
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Recibir mensaje del cliente
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message:
                continue
            
            # Enviar mensaje de "escribiendo..."
            await manager.send_message(
                json.dumps({
                    "type": "typing",
                    "message": "El agente está analizando tu consulta..."
                }),
                session_id
            )
            
            # Procesar mensaje
            result = await process_agent_message(user_message, session_id)
            
            # Enviar respuesta
            await manager.send_message(
                json.dumps({
                    "type": "response",
                    "data": result
                }),
                session_id
            )
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"Error en WebSocket: {e}")
        await manager.send_message(
            json.dumps({
                "type": "error",
                "message": f"Error: {str(e)}"
            }),
            session_id
        )
        manager.disconnect(session_id)

@app.get("/api/health")
async def health_check():
    """Endpoint de salud"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/agent/info")
async def get_agent_info():
    """Información sobre el agente"""
    return {
        "name": root_agent.name,
        "description": "Agente de optimización de infraestructura GCP",
        "capabilities": [
            "Análisis de costos de infraestructura",
            "Recomendaciones de optimización",
            "Generación de visualizaciones",
            "Análisis de recursos GCP (VMs, Storage, SQL, GKE, Redis, Spanner)"
        ],
        "project_id": os.getenv("GOOGLE_CLOUD_PROJECT")
    }

if __name__ == "__main__":
    # Crear directorio de templates si no existe
    os.makedirs("templates", exist_ok=True)
    
    # Ejecutar servidor
    uvicorn.run(
        "web_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )