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
        """Generates a detailed prompt for creating an infrastructure cost visualization."""
        
        prompt = "Create a professional and visually appealing isometric cloud architecture diagram for a GCP project. "
        prompt += "The diagram should represent the following resources, with their sizes and colors reflecting their monthly cost. "
        prompt += "Use a clean, modern style with clear labels. Emphasize the most expensive services.\n\n"

        prompt += "Resources to include:\n"
        
        if resources.get('vms'):
            prompt += f"- {len(resources['vms'])} Virtual Machines. The most expensive is \"{resources['vms'][0]['name']}\" at ${resources['vms'][0]['monthly_cost']}. Show this one as larger and colored red.\n"
        
        if resources.get('databases'):
            prompt += f"- {len(resources['databases'])} Cloud SQL databases. The most expensive is \"{resources['databases'][0]['name']}\" at ${resources['databases'][0]['monthly_cost']}. Color it orange.\n"

        if resources.get('storage'):
            total_storage_cost = sum(b['monthly_cost'] for b in resources['storage'])
            prompt += f"- {len(resources['storage'])} Storage Buckets, with a total cost of ${total_storage_cost:.2f}. Represent this as a group of generic buckets.\n"

        if resources.get('run_services'):
            total_run_cost = sum(s['monthly_cost'] for s in resources['run_services'])
            prompt += f"- {len(resources['run_services'])} Cloud Run Services, with a massive total cost of ${total_run_cost:.2f}. This is the main cost center. Show a large cluster of Cloud Run icons, glowing red to signify the high cost.\n"

        if resources.get('schedulers'):
            prompt += f"- {len(resources['schedulers'])} Cloud Schedulers. Show these as small clock icons, triggering the Cloud Run services.\n"

        prompt += "\nStyling notes:\n"
        prompt += "- Use isometric perspective."
        prompt += "- Label each main component clearly."
        prompt += "- Use arrows to suggest data flow, for example from Schedulers to Cloud Run, and from Cloud Run to the Cloud SQL database."
        prompt += "- The overall mood should be professional, like a diagram for a tech presentation."

        return prompt
