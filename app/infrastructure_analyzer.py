import json
from typing import Dict, List
import random

class InfrastructureAnalyzer:
    def __init__(self, project_id: str):
        self.project_id = project_id
    
    def get_infrastructure_summary(self) -> Dict:
        """Simula recursos de GCP con costos para el hackathon"""
        
        resources = {
            "vms": [
                {"name": "web-server-prod-1", "type": "e2-medium", "monthly_cost": 120, "status": "running"},
                {"name": "app-server-prod-1", "type": "n2-standard-4", "monthly_cost": 280, "status": "running"},
                {"name": "worker-node-dev-1", "type": "e2-small", "monthly_cost": 45, "status": "idle"},
                {"name": "ml-training-node", "type": "n2-highmem-8", "monthly_cost": 560, "status": "running"},
            ],
            "databases": [
                {"name": "cloud-sql-prod", "type": "PostgreSQL", "monthly_cost": 450},
                {"name": "cloud-sql-dev", "type": "MySQL", "monthly_cost": 125},
            ],
            "storage": [
                {"name": "media-bucket", "size_gb": 500, "monthly_cost": 15},
                {"name": "backup-bucket", "size_gb": 2000, "monthly_cost": 40},
                {"name": "logs-bucket", "size_gb": 100, "monthly_cost": 3},
            ],
            "total_monthly_cost": 1638,
            "potential_savings": 485
        }
        
        return resources
    
    def generate_cost_prompt(self, resources: Dict) -> str:
        """Genera prompt para visualización con Vertex AI"""
        
        expensive_items = []
        for vm in resources.get("vms", []):
            if vm["monthly_cost"] > 200:
                expensive_items.append(f"{vm['name']}: ${vm['monthly_cost']}/month")
        
        for db in resources.get("databases", []):
            if db["monthly_cost"] > 200:
                expensive_items.append(f"{db['name']}: ${db['monthly_cost']}/month")
        
        prompt = f"""
        Create a professional Google Cloud Platform infrastructure diagram showing:
        
        COMPONENTS:
        - {len(resources['vms'])} Virtual Machines (VMs)
        - {len(resources['databases'])} Cloud SQL databases
        - {len(resources['storage'])} Cloud Storage buckets
        
        COST VISUALIZATION:
        - Total monthly cost: ${resources['total_monthly_cost']}
        - Highlight in RED the expensive items: {', '.join(expensive_items)}
        - Show in GREEN the potential savings: ${resources['potential_savings']}/month
        - Add cost badges ($XXX/mo) next to each component
        
        STYLE REQUIREMENTS:
        - Professional white background
        - Use official Google Cloud icons and colors
        - Organize in logical tiers: Web tier, App tier, Data tier
        - Connect related services with dotted lines
        - Add a cost legend: Red=High Cost (>$200), Yellow=Medium ($50-200), Green=Low (<$50)
        - Include a savings opportunity callout box
        
        Make it look like a real enterprise architecture diagram that would impress executives.
        """
        
        return prompt
    
    def get_optimization_recommendations(self) -> List[Dict]:
        """Genera recomendaciones de optimización"""
        
        recommendations = [
            {
                "title": "Rightsize Overprovisioned VMs",
                "description": "ml-training-node is using only 30% CPU on average",
                "monthly_savings": 180,
                "effort": "Low",
                "action": "Change from n2-highmem-8 to n2-standard-4"
            },
            {
                "title": "Shutdown Idle Development Resources",
                "description": "worker-node-dev-1 has been idle for 2 weeks",
                "monthly_savings": 45,
                "effort": "Low", 
                "action": "Implement auto-shutdown policy"
            },
            {
                "title": "Use Committed Use Discounts",
                "description": "Commit to 1-year usage for production resources",
                "monthly_savings": 260,
                "effort": "Medium",
                "action": "Purchase committed use contract"
            }
        ]
        
        return recommendations
