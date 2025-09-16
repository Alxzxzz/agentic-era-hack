#!/bin/bash

# Configuración
PROJECT="gauss--core--dev--af"
OUTPUT_DIR="recommender_complete_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$OUTPUT_DIR"
LOG_FILE="$OUTPUT_DIR/test_log.txt"

# Colores
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Lista OFICIAL de recommenders según la documentación
declare -a RECOMMENDERS=(
    # IAM & Security
    "google.iam.policy.Recommender:global"
    "google.iam.serviceAccount.ChangeRiskRecommender:global"
    "google.iam.policy.ChangeRiskRecommender:global"
    
    # Compute - VMs e Instancias
    "google.compute.instance.IdleResourceRecommender:ZONES"
    "google.compute.instance.MachineTypeRecommender:ZONES"
    "google.compute.instanceGroupManager.MachineTypeRecommender:ZONES"
    
    # Compute - Recursos
    "google.compute.commitment.UsageCommitmentRecommender:REGIONS"
    "google.compute.disk.IdleResourceRecommender:ZONES"
    "google.compute.address.IdleResourceRecommender:REGIONS"
    "google.compute.image.IdleResourceRecommender:global"
    "google.compute.IdleResourceRecommender:ZONES"
    "google.compute.RightSizeResourceRecommender:ZONES"
    
    # Storage
    "google.storage.bucket.SoftDeleteRecommender:global"
    "google.storage.bucket.AnywhereCacheRecommender:global"
    
    # Cloud SQL
    "google.cloudsql.instance.IdleRecommender:REGIONS"
    "google.cloudsql.instance.OverprovisionedRecommender:REGIONS"
    "google.cloudsql.instance.UnderprovisionedRecommender:REGIONS"
    "google.cloudsql.instance.SecurityRecommender:REGIONS"
    "google.cloudsql.instance.PerformanceRecommender:REGIONS"
    "google.cloudsql.instance.ReliabilityRecommender:REGIONS"
    "google.cloudsql.instance.OutOfDiskRecommender:REGIONS"
    
    # Cloud Run
    "google.run.service.CostRecommender:REGIONS"
    "google.run.service.SecurityRecommender:REGIONS"
    "google.run.service.IdentityRecommender:REGIONS"
    
    # BigQuery
    "google.bigquery.table.PartitionClusterRecommender:global"
    "google.bigquery.capacityCommitments.Recommender:REGIONS"
    
    # Containers/GKE
    "google.container.DiagnosisRecommender:ZONES"
    
    # Logging
    "google.logging.productSuggestion.ContainerRecommender:global"
    
    # Resource Manager
    "google.resourcemanager.projectUtilization.Recommender:global"
    "google.resourcemanager.serviceLimit.Recommender:global"
    "google.resourcemanager.project.ChangeRiskRecommender:global"
    
    # Cloud Functions
    "google.cloudfunctions.PerformanceRecommender:REGIONS"
    
    # Firestore
    "google.firestore.database.FirebaseRulesRecommender:global"
    "google.firestore.database.ReliabilityRecommender:global"
    
    # General
    "google.cloud.security.GeneralRecommender:global"
    "google.cloud.RecentChangeRecommender:global"
    "google.cloud.deprecation.GeneralRecommender:global"
    "google.clouderrorreporting.Recommender:global"
    "google.gmp.project.ManagementRecommender:global"
)

# Obtener zonas y regiones
echo -e "${YELLOW}Obteniendo zonas y regiones activas...${NC}"
ZONES=$(gcloud compute instances list --project=$PROJECT --format="value(zone)" 2>/dev/null | sort -u)
REGIONS=$(echo "$ZONES" | sed 's/-[a-z]$//' | sort -u)

if [ -z "$ZONES" ]; then
    ZONES="europe-west1-b"
    REGIONS="europe-west1"
fi

echo "Zonas: $ZONES"
echo "Regiones: $REGIONS"
echo "---"

# Función para probar
test_recommender() {
    local recommender=$1
    local location=$2
    local output_file="$OUTPUT_DIR/${recommender//\./_}_${location//\//_}.json"
    
    echo -n "Testing $recommender in $location... "
    
    result=$(gcloud recommender recommendations list \
        --project=$PROJECT \
        --location=$location \
        --recommender=$recommender \
        --format=json 2>&1)
    
    exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        count=$(echo "$result" | jq '. | length' 2>/dev/null || echo "0")
        
        if [ "$count" != "0" ] && [ "$count" != "null" ]; then
            echo -e "${GREEN}✓ Found $count recommendations${NC}"
            echo "$result" > "$output_file"
            echo "$(date): SUCCESS - $recommender in $location - $count recommendations" >> "$LOG_FILE"
        else
            echo -e "${YELLOW}○ No recommendations${NC}"
            echo "$(date): EMPTY - $recommender in $location" >> "$LOG_FILE"
        fi
    else
        if echo "$result" | grep -q "Permission denied\|403\|does not have"; then
            echo -e "${RED}✗ Permission denied${NC}"
            echo "$(date): PERMISSION_ERROR - $recommender in $location" >> "$LOG_FILE"
        elif echo "$result" | grep -q "INVALID_ARGUMENT"; then
            echo -e "${RED}✗ Invalid recommender${NC}"
            echo "$(date): INVALID - $recommender in $location" >> "$LOG_FILE"
        else
            echo -e "${RED}✗ Error${NC}"
            echo "$(date): ERROR - $recommender in $location - ${result:0:100}" >> "$LOG_FILE"
        fi
    fi
}

# Probar cada recommender
echo -e "${YELLOW}=== Testing Official Recommenders ===${NC}\n"

for item in "${RECOMMENDERS[@]}"; do
    IFS=':' read -r recommender location_type <<< "$item"
    
    echo -e "\n${YELLOW}Testing: $recommender${NC}"
    
    case $location_type in
        "global")
            test_recommender "$recommender" "global"
            ;;
        "ZONES")
            for zone in $ZONES; do
                test_recommender "$recommender" "$zone"
            done
            ;;
        "REGIONS")
            for region in $REGIONS; do
                test_recommender "$recommender" "$region"
            done
            ;;
    esac
done

# Resumen
echo -e "\n${YELLOW}=== Resumen Final ===${NC}"
echo "Resultados en: $OUTPUT_DIR"
echo "Log: $LOG_FILE"

success_count=$(grep -c "SUCCESS" "$LOG_FILE" 2>/dev/null || echo "0")
empty_count=$(grep -c "EMPTY" "$LOG_FILE" 2>/dev/null || echo "0")
permission_count=$(grep -c "PERMISSION_ERROR" "$LOG_FILE" 2>/dev/null || echo "0")
invalid_count=$(grep -c "INVALID" "$LOG_FILE" 2>/dev/null || echo "0")
error_count=$(grep -c "ERROR" "$LOG_FILE" 2>/dev/null || echo "0")

echo -e "${GREEN}Con recomendaciones: $success_count${NC}"
echo -e "${YELLOW}Sin recomendaciones: $empty_count${NC}"
echo -e "${RED}Errores de permisos: $permission_count${NC}"
echo -e "${RED}Recommenders inválidos: $invalid_count${NC}"
echo -e "${RED}Otros errores: $error_count${NC}"

# Listar los que tienen datos
echo -e "\n${GREEN}Recommenders con datos:${NC}"
grep "SUCCESS" "$LOG_FILE" 2>/dev/null | cut -d' ' -f4-7 | sort -u