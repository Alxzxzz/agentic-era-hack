import json
from typing import Dict, List
from app.gcp_real_data import GCPRealDataCollector
from app.recommender_service import RecommenderService

class InfrastructureAnalyzer:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.data_collector = GCPRealDataCollector(project_id)
    
    def get_infrastructure_summary(self) -> Dict:
        """Obtiene datos REALES de GCP"""
        
        # Obtener datos reales
        real_data = self.data_collector.get_real_infrastructure()
        
        # NO añadir datos falsos, usar SOLO lo real
        resources = {
            "vms": real_data.get("vms", []),
            "databases": real_data.get("databases", []),  # Solo si existen realmente
            "storage": real_data.get("storage", []),      # Solo si existen realmente  
            "total_monthly_cost": real_data.get("total_monthly_cost", 0),
            "potential_savings": real_data.get("potential_savings", 0),
            "is_real_data": True,
            "project_id": self.project_id,
            "detected_resources": real_data.get("detected_resources", "")
        }
        
        return resources
    def get_smart_recommendations(self) -> str:
        """Genera recomendaciones basadas en monitoring real"""
    
        resources = self.get_infrastructure_summary()
        monitor = MonitoringAnalyzer(self.project_id)
        recommendations = monitor.generate_recommendations(resources)
        
        if not recommendations:
            return "No se encontraron optimizaciones significativas."
        
        response = "**Recomendaciones basadas en uso real (últimas 24h):**\n\n"
        
        total_savings = 0
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. **{rec['type'].replace('-', ' ').title()}** para `{rec['resource']}`\n"
            response += f"   - Razón: {rec['reason']}\n"
            response += f"   - Ahorro estimado: ${rec['monthly_savings']:.2f}/mes\n"
            response += f"   - Confianza: {rec['confidence']}\n\n"
            total_savings += rec['monthly_savings']
        
        response += f"**💰 Ahorro total potencial: ${total_savings:.2f}/mes**"
        
        return response
    def get_google_recommendations(self) -> str:
        """Obtiene recomendaciones oficiales de Google Cloud Recommender"""
        
        recommender = RecommenderService(self.project_id)
        recommendations = recommender.get_cost_recommendations()
        
        if not recommendations["recommendation_count"]:
            return "No hay recomendaciones de optimización disponibles actualmente."
        
        response = "🎯 **Recomendaciones Oficiales de Google Cloud:**\n\n"
        
        # VM Rightsizing
        if recommendations["recommendations"]["vm_rightsizing"]:
            response += "**🖥️ Optimización de VMs:**\n"
            for rec in recommendations["recommendations"]["vm_rightsizing"]:
                response += f"- {rec['resource']}: {rec['description']}\n"
                if rec['monthly_savings'] > 0:
                    response += f"  💰 Ahorro: ${rec['monthly_savings']}/mes\n"
        
        # Recursos Idle
        if recommendations["recommendations"]["idle_resources"]:
            response += "\n**⏸️ Recursos Sin Uso:**\n"
            for rec in recommendations["recommendations"]["idle_resources"]:
                response += f"- {rec['resource']}: {rec['description']}\n"
                if rec['monthly_savings'] > 0:
                    response += f"  💰 Ahorro: ${rec['monthly_savings']}/mes\n"
        
        # Committed Use
        if recommendations["recommendations"]["committed_use"]:
            response += "\n**📋 Descuentos por Compromiso:**\n"
            for rec in recommendations["recommendations"]["committed_use"]:
                response += f"- {rec['description']}\n"
                if rec['monthly_savings'] > 0:
                    response += f"  💰 Ahorro: ${rec['monthly_savings']}/mes\n"
        
        response += f"\n**💰 AHORRO TOTAL POTENCIAL: ${recommendations['total_monthly_savings']}/mes**"
        
        return response
    # Mantener el resto de funciones igual