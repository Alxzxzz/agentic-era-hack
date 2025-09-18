from typing import Dict

class GCPBillingCalculator:
    def __init__(self, project_id: str):
        self.project_id = project_id
        
        # PRECIOS REALES GCP (us-central1, 2024)
        self.VM_PRICES = {
            "e2-micro": 6.11,
            "e2-small": 12.23,
            "e2-medium": 24.46,
            "e2-standard-2": 48.92,
            "n1-standard-1": 34.78,
            "n2-standard-2": 48.92,
            "n2-standard-4": 97.84
        }
        
        # PRECIOS REALES STORAGE (por GB-mes)
        self.STORAGE_PRICES = {
            "standard": 0.020,      # Single-region
            "standard_multi": 0.026, # Multi-region US
            "nearline": 0.010,
            "coldline": 0.004,
            "archive": 0.0012
        }
    
    def calculate_vm_cost(self, machine_type: str) -> float:
        """Retorna costo mensual de una VM"""
        return self.VM_PRICES.get(machine_type, 24.46)
    
    def calculate_storage_cost(self, gb: float, storage_class: str = "standard", multi_region: bool = False) -> float:
        """Calcula costo mensual de storage con precios correctos"""
        
        if multi_region and storage_class == "standard":
            price_per_gb = 0.026
        else:
            price_per_gb = self.STORAGE_PRICES.get(storage_class, 0.020)
        
        return round(gb * price_per_gb, 2)
    
    def get_real_costs_from_billing(self) -> Dict:
        return None