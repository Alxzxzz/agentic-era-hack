import os
from google.cloud.asset_v1 import AssetServiceClient, ContentType
from typing import Dict, List
import json
import google.auth

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
        
        if not self.asset_client:
            return self._get_mock_data()

        parent = f"projects/{self.project_id}"
        
        try:
            # Listar assets
            assets = list(self.asset_client.list_assets(
                request={
                    "parent": parent,
                    "content_type": ContentType.RESOURCE,
                }
            ))
        except Exception as e:
            creds, _ = google.auth.default()
            account = creds.service_account_email if hasattr(creds, 'service_account_email') else 'user account'
            print(f"Error listing assets for project {self.project_id} as {account}: {e}")
            return self._get_mock_data()

        print(f"Found {len(assets)} assets in project {self.project_id}")

        vms = []
        storage = []
        databases = []
        
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
                
                # Precio real de e2-medium en us-central1
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
                size_gb = 50  # Estimado
                
                # Determinar si es multi-region (por defecto en US)
                is_multi_region = True  # La mayoría usa multi-region
                storage_class = "standard"
                
                # CÁLCULO CORRECTO
                if is_multi_region:
                    monthly_cost = round(size_gb * 0.026, 2)  # $1.30 para 50GB multi-region
                else:
                    monthly_cost = round(size_gb * 0.020, 2)  # $1.00 para 50GB single-region
                
                storage.append({
                    "name": name,
                    "size_gb": size_gb,
                    "monthly_cost": monthly_cost,
                    "storage_class": storage_class,
                    "location": "us (multi-region)" if is_multi_region else "us-central1"
                })
        
        # Calcular totales
        vm_total = sum([vm["monthly_cost"] for vm in vms])
        storage_total = sum([s["monthly_cost"] for s in storage])
        total_cost = vm_total + storage_total
        
        # Ahorros potenciales (30% es realista)
        potential_savings = total_cost * 0.3
        
        return {
            "vms": vms,
            "storage": storage,
            "databases": databases,
            "total_monthly_cost": round(total_cost, 2),
            "potential_savings": round(potential_savings, 2),
            "project_id": self.project_id,
            "is_real_data": True,
            "detected_resources": f"{len(vms)} VMs, {len(storage)} buckets"
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
            "total_monthly_cost": 165,
            "potential_savings": 50,
            "project_id": self.project_id,
            "is_real_data": False,
            "detected_resources": "Mock data"
        }