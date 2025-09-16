from google.cloud.recommender_v1 import RecommenderClient
from typing import List, Dict
import json
import google.auth

class RecommenderService:
    def __init__(self, project_id: str):
        self.project_id = project_id
        try:
            self.client = RecommenderClient()
        except Exception as e:
            print(f"Error initializing RecommenderClient: {e}")
            self.client = None
        
    def get_all_recommendations(self) -> List[Dict]:
        """Obtiene TODAS las recomendaciones de Google Cloud Recommender"""
        
        if not self.client:
            return []

        all_recommendations = []
        locations = ["global", "europe-west1", "europe-west1-b", "us-central1"]
        recommender_types = [
            "google.iam.policy.Recommender",
            "google.iam.serviceAccount.ChangeRiskRecommender",
            "google.iam.policy.ChangeRiskRecommender",
            "google.compute.instance.IdleResourceRecommender",
            "google.compute.instance.MachineTypeRecommender",
            "google.compute.instanceGroupManager.MachineTypeRecommender",
            "google.compute.commitment.UsageCommitmentRecommender",
            "google.compute.disk.IdleResourceRecommender",
            "google.compute.address.IdleResourceRecommender",
            "google.compute.image.IdleResourceRecommender",
            "google.compute.IdleResourceRecommender",
            "google.compute.RightSizeResourceRecommender",
            "google.storage.bucket.SoftDeleteRecommender",
            "google.storage.bucket.AnywhereCacheRecommender",
            "google.cloudsql.instance.IdleRecommender",
            "google.cloudsql.instance.OverprovisionedRecommender",
            "google.cloudsql.instance.UnderprovisionedRecommender",
            "google.cloudsql.instance.SecurityRecommender",
            "google.cloudsql.instance.PerformanceRecommender",
            "google.cloudsql.instance.ReliabilityRecommender",
            "google.cloudsql.instance.OutOfDiskRecommender",
            "google.run.service.CostRecommender",
            "google.run.service.SecurityRecommender",
            "google.run.service.IdentityRecommender",
            "google.bigquery.table.PartitionClusterRecommender",
            "google.bigquery.capacityCommitments.Recommender",
            "google.container.DiagnosisRecommender",
            "google.logging.productSuggestion.ContainerRecommender",
            "google.resourcemanager.projectUtilization.Recommender",
            "google.resourcemanager.serviceLimit.Recommender",
            "google.resourcemanager.project.ChangeRiskRecommender",
            "google.cloudfunctions.PerformanceRecommender",
            "google.firestore.database.FirebaseRulesRecommender",
            "google.firestore.database.ReliabilityRecommender",
            "google.cloud.security.GeneralRecommender",
            "google.cloud.RecentChangeRecommender",
            "google.cloud.deprecation.GeneralRecommender",
            "google.clouderrorreporting.Recommender",
            "google.gmp.project.ManagementRecommender",
        ]

        for location in locations:
            parent = f"projects/{self.project_id}/locations/{location}"
            for recommender_type in recommender_types:
                try:
                    recommender_parent = f"{parent}/recommenders/{recommender_type}"
                    
                    # Listar recomendaciones para este tipo
                    recommendations = self.client.list_recommendations(
                        request={"parent": recommender_parent}
                    )
                    
                    recommendations_list = list(recommendations)
                    print(f"Found {len(recommendations_list)} recommendations for {recommender_type} in {location}")

                    for recommendation in recommendations_list:
                        rec_data = self._parse_recommendation(recommendation)
                        if rec_data:
                            all_recommendations.append(rec_data)
                            
                except Exception as e:
                    creds, _ = google.auth.default()
                    account = creds.service_account_email if hasattr(creds, 'service_account_email') else 'user account'
                    # Algunos recommenders pueden no estar disponibles
                    if "PERMISSION_DENIED" not in str(e) and "NOT_FOUND" not in str(e):
                        print(f"Error getting {recommender_type} for project {self.project_id} as {account}: {e}")
                    continue
        
        return all_recommendations
    
    def _parse_recommendation(self, recommendation) -> Dict:
        """Parsea una recomendación en formato legible"""
        
        try:
            # Extraer información básica
            rec_name = recommendation.name.split("/")[-1]
            rec_type = recommendation.recommender_subtype
            
            # Calcular ahorro
            primary_impact = recommendation.primary_impact
            cost_impact = 0
            
            if primary_impact and primary_impact.cost_projection:
                cost = primary_impact.cost_projection.cost
                if cost and cost.units:
                    cost_impact = abs(int(cost.units))
            
            # Extraer detalles
            description = recommendation.description
            
            # Obtener recurso afectado
            resource = "Unknown"
            if recommendation.content and recommendation.content.operation_groups:
                for op_group in recommendation.content.operation_groups:
                    for operation in op_group.operations:
                        if operation.resource:
                            resource = operation.resource.split("/")[-1]
                            break
            
            return {
                "id": rec_name,
                "type": rec_type,
                "resource": resource,
                "description": description,
                "monthly_savings": cost_impact,
                "state": recommendation.state_info.state.name,
                "priority": recommendation.priority.name,
                "category": recommendation.primary_impact.category.name if recommendation.primary_impact else "COST"
            }
            
        except Exception as e:
            print(f"Error parsing recommendation: {e}")
            return None
    
    def get_cost_recommendations(self) -> Dict:
        """Obtiene solo recomendaciones de ahorro de costos"""
        
        all_recs = self.get_all_recommendations()
        
        # Filtrar solo las de costos
        cost_recs = [r for r in all_recs if r.get("category") == "COST" or r.get("monthly_savings", 0) > 0]
        
        # Agrupar por tipo
        grouped = {
            "vm_rightsizing": [],
            "idle_resources": [],
            "committed_use": [],
            "other": []
        }
        
        for rec in cost_recs:
            if "MachineType" in rec.get("type", ""):
                grouped["vm_rightsizing"].append(rec)
            elif "Idle" in rec.get("type", ""):
                grouped["idle_resources"].append(rec)
            elif "Commitment" in rec.get("type", ""):
                grouped["committed_use"].append(rec)
            else:
                grouped["other"].append(rec)
        
        # Calcular ahorro total
        total_savings = sum(r.get("monthly_savings", 0) for r in cost_recs)
        
        return {
            "recommendations": grouped,
            "total_monthly_savings": total_savings,
            "recommendation_count": len(cost_recs)
        }
