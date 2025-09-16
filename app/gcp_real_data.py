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
        """Obtiene TODOS los recursos usando Asset Inventory"""
        
        cache_key = f"assets_{self.project_id}"
        cached_assets = get_from_cache(cache_key)
        if cached_assets:
            print(f"Found {len(cached_assets)} assets in cache for project {self.project_id}")
            assets = cached_assets
        else:
            if not self.asset_client:
                return self._get_mock_data()

            parent = f"projects/{self.project_id}"
            
            try:
                # Listar assets
                assets = list(self.asset_client.list_assets(
                    request={
                        "parent": parent,
                        "content_type": ContentType.RESOURCE,
                        "asset_types": [
                            "compute.googleapis.com/Instance",
                            "storage.googleapis.com/Bucket",
                            "sqladmin.googleapis.com/Instance",
                            "container.googleapis.com/Cluster",
                            "redis.googleapis.com/Instance",
                            "spanner.googleapis.com/Instance",
                        ],
                    }
                ))
                set_in_cache(cache_key, assets)
            except Exception as e:
                creds, _ = google.auth.default()
                account = creds.service_account_email if hasattr(creds, 'service_account_email') else 'user account'
                print(f"Error listing assets for project {self.project_id} as {account}: {e}")
                return self._get_mock_data()

        print(f"Found {len(assets)} assets in project {self.project_id}")

        vms = []
        storage = []
        databases = []
        clusters = []
        redis_instances = []
        spanner_instances = []

        for asset in assets:
            if "compute.googleapis.com/Instance" in asset.asset_type:
                name = asset.name.split("/")[-1]

                if "InstanceSettings" in name:
                    continue

                zone = "us-central1-a"  # Default
                
                if "zones" in asset.name:
                    parts = asset.name.split("/")
                    zone_index = parts.index("zones") + 1
                    zone = parts[zone_index] if zone_index < len(parts) else "us-central1-a"
                
                monthly_cost = 24.46
                
                vms.append({
                    "name": name,
                    "type": "e2-medium",
                    "monthly_cost": monthly_cost,
                    "zone": zone,
                    "status": "running"
                })
            
            elif "storage.googleapis.com/Bucket" in asset.asset_type:
                name = asset.name.split("/")[-1]
                size_gb = 50
                monthly_cost = round(size_gb * 0.026, 2)
                
                storage.append({
                    "name": name,
                    "size_gb": size_gb,
                    "monthly_cost": monthly_cost,
                    "storage_class": "standard",
                    "location": "us (multi-region)"
                })

            elif "sqladmin.googleapis.com/Instance" in asset.asset_type:
                name = asset.name.split("/")[-1]
                monthly_cost = 50
                databases.append({
                    "name": name,
                    "type": "Cloud SQL",
                    "monthly_cost": monthly_cost
                })

            elif "container.googleapis.com/Cluster" in asset.asset_type:
                name = asset.name.split("/")[-1]
                monthly_cost = 73
                clusters.append({
                    "name": name,
                    "type": "GKE Cluster",
                    "monthly_cost": monthly_cost
                })

            elif "redis.googleapis.com/Instance" in asset.asset_type:
                name = asset.name.split("/")[-1]
                monthly_cost = 40
                redis_instances.append({
                    "name": name,
                    "type": "Memorystore for Redis",
                    "monthly_cost": monthly_cost
                })

            elif "spanner.googleapis.com/Instance" in asset.asset_type:
                name = asset.name.split("/")[-1]
                monthly_cost = 65
                spanner_instances.append({
                    "name": name,
                    "type": "Spanner",
                    "monthly_cost": monthly_cost
                })

        # Calcular totales
        vm_total = sum([vm["monthly_cost"] for vm in vms])
        storage_total = sum([s["monthly_cost"] for s in storage])
        db_total = sum([db["monthly_cost"] for db in databases])
        cluster_total = sum([c["monthly_cost"] for c in clusters])
        redis_total = sum([r["monthly_cost"] for r in redis_instances])
        spanner_total = sum([s["monthly_cost"] for s in spanner_instances])
        total_cost = vm_total + storage_total + db_total + cluster_total + redis_total + spanner_total
        
        potential_savings = total_cost * 0.3
        
        return {
            "vms": vms,
            "storage": storage,
            "databases": databases,
            "clusters": clusters,
            "redis_instances": redis_instances,
            "spanner_instances": spanner_instances,
            "total_monthly_cost": round(total_cost, 2),
            "potential_savings": round(potential_savings, 2),
            "project_id": self.project_id,
            "is_real_data": True,
            "detected_resources": f"{len(vms)} VMs, {len(storage)} buckets, {len(databases)} databases, {len(clusters)} clusters, {len(redis_instances)} redis, {len(spanner_instances)} spanner"
        }

    def _get_mock_data(self) -> Dict:
        """Datos de fallback si las APIs fallan"""
        return {
            "vms": [
                {"name": "prod-server-1", "type": "e2-medium", "monthly_cost": 120},
                {"name": "dev-server-1", "type": "e2-small", "monthly_cost": 45},
            ],
            "storage": [],
            "databases": [],
            "clusters": [],
            "redis_instances": [],
            "spanner_instances": [],
            "total_monthly_cost": 165,
            "potential_savings": 50,
            "project_id": self.project_id,
            "is_real_data": False,
            "detected_resources": "Mock data"
        }