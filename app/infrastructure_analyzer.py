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
        return self.data_collector.get_real_infrastructure()

    def get_google_recommendations(self) -> Dict:
        """Obtiene recomendaciones oficiales de Google Cloud Recommender"""
        
        recommender = RecommenderService(self.project_id)
        recommendations = recommender.get_cost_recommendations()
        
        return recommendations
    # Mantener el resto de funciones igual
