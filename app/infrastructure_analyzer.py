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

    def get_google_recommendations(self) -> Dict:
        """Obtiene recomendaciones oficiales de Google Cloud Recommender"""
        
        recommender = RecommenderService(self.project_id)
        recommendations = recommender.get_cost_recommendations()
        
        return recommendations
    # Mantener el resto de funciones igual
