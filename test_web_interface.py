#!/usr/bin/env python3
"""
Script de prueba para la interfaz web personalizada
"""

import asyncio
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

async def test_agent_integration():
    """Prueba la integración con el agente existente"""
    
    print("🧪 Probando integración con el agente existente...")
    print("-" * 50)
    
    try:
        # Importar el agente existente
        from app.agent import root_agent
        print(f"✅ Agente importado: {root_agent.name}")
        print(f"   Modelo: {root_agent.model}")
        print(f"   Herramientas: {len(root_agent.tools)}")
        
        # Probar una función del agente
        from app.agent import analyze_infrastructure
        result = analyze_infrastructure("test query")
        print(f"✅ Función analyze_infrastructure funciona")
        print(f"   Respuesta: {result[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

async def test_web_server():
    """Prueba el servidor web"""
    
    print("\n🌐 Probando servidor web...")
    print("-" * 50)
    
    try:
        from web_server import app, process_agent_message
        print("✅ Servidor web importado correctamente")
        
        # Probar procesamiento de mensaje
        result = await process_agent_message("Hola", "test_session")
        print(f"✅ Procesamiento de mensaje funciona")
        print(f"   Respuesta: {result['response'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_files_exist():
    """Verifica que todos los archivos necesarios existen"""
    
    print("📁 Verificando archivos...")
    print("-" * 50)
    
    required_files = [
        "web_server.py",
        "templates/chat.html"
    ]
    
    all_exist = True
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NO ENCONTRADO")
            all_exist = False
    
    return all_exist

async def main():
    """Función principal de prueba"""
    
    print("🚀 Iniciando pruebas de la interfaz web personalizada...")
    print("=" * 60)
    
    # Verificar archivos
    files_ok = test_files_exist()
    
    if not files_ok:
        print("\n❌ No se pueden ejecutar las pruebas - archivos faltantes")
        return
    
    # Probar integración con agente
    agent_ok = await test_agent_integration()
    
    # Probar servidor web
    web_ok = await test_web_server()
    
    print("\n" + "=" * 60)
    print("🎯 Resumen de pruebas:")
    print(f"   {'✅' if files_ok else '❌'} Archivos de interfaz web")
    print(f"   {'✅' if agent_ok else '❌'} Integración con agente")
    print(f"   {'✅' if web_ok else '❌'} Servidor web")
    
    if files_ok and agent_ok and web_ok:
        print("\n🎉 ¡La interfaz web está lista para usar!")
        print("   Ejecuta: make web")
        print("   Accede a: http://localhost:8000")
        print("\n💡 Diferencias con el playground:")
        print("   - Interfaz HTML personalizada")
        print("   - Generación automática de imágenes")
        print("   - Diseño moderno y responsivo")
        print("   - WebSocket para tiempo real")
    else:
        print("\n⚠️ Hay problemas que resolver antes de usar la interfaz")

if __name__ == "__main__":
    asyncio.run(main())
