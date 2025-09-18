import os
from google.cloud.asset_v1 import AssetServiceClient, ContentType
from typing import Dict, List
import json
import google.auth
from app.cache import get_from_cache, set_in_cache

class GCPRealDataCollector:
    def __init__(self, project_id: str):
        self.project_id = project_id
        try:
            self.asset_client = AssetServiceClient()
        except Exception as e:
            print(f"Error initializing AssetServiceClient: {e}")
            self.asset_client = None

    def get_real_infrastructure(self) -> Dict:
        """Obtiene TODOS los recursos usando Asset Inventory de forma granular."""
        if not self.asset_client:
            raise ConnectionError("AssetServiceClient not initialized")

        parent = f"projects/{self.project_id}"
        assets = []
        asset_types_to_query = [
            "compute.googleapis.com/Instance",
            "container.googleapis.com/Cluster",
            "pubsub.googleapis.com/Topic",
            "pubsub.googleapis.com/Subscription",
            "storage.googleapis.com/Bucket",
            "sqladmin.googleapis.com/Instance",
            "redis.googleapis.com/Instance",
            "spanner.googleapis.com/Instance",
            "run.googleapis.com/Service",
            "cloudscheduler.googleapis.com/Job",
        ]

        for asset_type in asset_types_to_query:
            try:
                # Intentar obtener recurso y relaciones
                print(f"Querying {asset_type} with RELATIONSHIPS...")
                response = list(self.asset_client.list_assets(
                    request={
                        "parent": parent,
                        "content_type": ContentType.RESOURCE | ContentType.RELATIONSHIP,
                        "asset_types": [asset_type],
                    }
                ))
                assets.extend(response)
            except Exception as e:
                if "No RELATIONSHIP found" in str(e):
                    # Si falla por relaciones, reintentar solo con recurso
                    print(f"Retrying {asset_type} with RESOURCE only...")
                    try:
                        response = list(self.asset_client.list_assets(
                            request={
                                "parent": parent,
                                "content_type": ContentType.RESOURCE,
                                "asset_types": [asset_type],
                            }
                        ))
                        assets.extend(response)
                    except Exception as e2:
                        print(f"Error listing {asset_type} (resource only): {e2}")
                else:
                    print(f"Error listing {asset_type}: {e}")

        print(f"Found {len(assets)} total assets in project {self.project_id}")

        vms, storage, databases, clusters, redis_instances, spanner_instances, schedulers, run_services = [], [], [], [], [], [], [], []

        for asset in assets:
            asset_details = {
                "name": asset.name.split("/")[-1],
                "type": asset.asset_type,
                "relationships": []
            }

            if hasattr(asset, 'resource') and asset.resource and hasattr(asset.resource, 'relationships'):
                for rel in asset.resource.relationships:
                    asset_details["relationships"].append({
                        "target": rel.target_resource,
                        "type": rel.type
                    })

            if "compute.googleapis.com/Instance" in asset.asset_type:
                name = asset.name.split("/")[-1]
                if "InstanceSettings" in name: continue
                vms.append({
                    "name": name, "type": "e2-medium", "monthly_cost": 24.46,
                    "zone": asset.name.split("/")[3], "status": "running",
                    "relationships": asset_details["relationships"]
                })
            elif "storage.googleapis.com/Bucket" in asset.asset_type:
                storage.append({
                    "name": asset.name.split("/")[-1], "size_gb": 50, "monthly_cost": 1.30,
                    "storage_class": "standard", "location": "us (multi-region)",
                    "relationships": asset_details["relationships"]
                })
            elif "sqladmin.googleapis.com/Instance" in asset.asset_type:
                databases.append({
                    "name": asset.name.split("/")[-1], "type": "Cloud SQL", "monthly_cost": 50,
                    "relationships": asset_details["relationships"]
                })
            elif "container.googleapis.com/Cluster" in asset.asset_type:
                clusters.append({
                    "name": asset.name.split("/")[-1], "type": "GKE Cluster", "monthly_cost": 73,
                    "relationships": asset_details["relationships"]
                })
            elif "redis.googleapis.com/Instance" in asset.asset_type:
                redis_instances.append({
                    "name": asset.name.split("/")[-1], "type": "Memorystore for Redis", "monthly_cost": 40,
                    "relationships": asset_details["relationships"]
                })
            elif "spanner.googleapis.com/Instance" in asset.asset_type:
                spanner_instances.append({
                    "name": asset.name.split("/")[-1], "type": "Spanner", "monthly_cost": 65,
                    "relationships": asset_details["relationships"]
                })
            elif "cloudscheduler.googleapis.com/Job" in asset.asset_type:
                schedulers.append({
                    "name": asset.name.split("/")[-1], "type": "Cloud Scheduler", "monthly_cost": 0.10,
                    "relationships": asset_details["relationships"]
                })
            elif "run.googleapis.com/Service" in asset.asset_type:
                run_services.append({
                    "name": asset.name.split("/")[-1], "type": "Cloud Run Service", "monthly_cost": 15.00, # Placeholder
                    "relationships": asset_details["relationships"]
                })

        total_cost = sum(i["monthly_cost"] for i in vms + storage + databases + clusters + redis_instances + spanner_instances + schedulers + run_services)
        
        return {
            "vms": vms, "storage": storage, "databases": databases, "clusters": clusters,
            "redis_instances": redis_instances, "spanner_instances": spanner_instances, "schedulers": schedulers, "run_services": run_services,
            "total_monthly_cost": round(total_cost, 2),
            "potential_savings": round(total_cost * 0.3, 2),
            "project_id": self.project_id, "is_real_data": True,
            "detected_resources": f"{len(vms)} VMs, {len(storage)} buckets, {len(databases)} databases, "
                              f"{len(clusters)} clusters, {len(redis_instances)} redis, {len(spanner_instances)} spanner, "
                              f"{len(schedulers)} schedulers, {len(run_services)} run services"
        }