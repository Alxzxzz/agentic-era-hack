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
        recommendations = recommender.get_categorized_recommendations()
        
        return recommendations

    def generate_cost_prompt(self, resources: Dict) -> str:
        """Genera un prompt detallado para crear visualizaciones de costos"""
        
        prompt = f"""
Create a professional Google Cloud Platform architecture diagram showing:

CURRENT INFRASTRUCTURE:
- {len(resources.get('vms', []))} Compute Engine instances (VMs)
- {len(resources.get('databases', []))} Cloud SQL databases
- {len(resources.get('storage', []))} Cloud Storage buckets
- {len(resources.get('clusters', []))} GKE clusters
- {len(resources.get('redis_instances', []))} Memorystore Redis instances
- {len(resources.get('spanner_instances', []))} Spanner instances
- Total monthly cost: ${resources.get('total_monthly_cost', 0)}

VISUAL STYLE:
- Professional Google Cloud architecture diagram
- Official GCP icons (Compute Engine, Cloud SQL, Cloud Storage, GKE, Redis, Spanner)
- Google corporate colors (blue, green, red, yellow)
- Clean and organized layout
- Text in Spanish
- Cost indicators on each service
- Arrows showing data flow

ELEMENTS TO INCLUDE:
- Title: "Arquitectura GCP - Análisis de Costos"
- Each service with its icon and monthly cost
- Connections between services
- Color legend for different resource types
- Usage and optimization metrics

The diagram should be clear, professional and easy to understand for cost analysis.
"""
        return prompt
