# Copyright 2025 Google LLC
import datetime
import os
from zoneinfo import ZoneInfo
import json
import base64
import google.generativeai as genai

import google.auth
from google.adk.agents import Agent
from app.infrastructure_analyzer import InfrastructureAnalyzer
from app.state_manager import get_project_id, set_project_id

_, default_project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", default_project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


def analyze_infrastructure(query: str) -> str:
    """Analyzes GCP infrastructure and returns cost analysis.
    
    Args:
        query: User query about infrastructure analysis
    
    Returns:
        Detailed infrastructure and cost analysis
    """
    project_id = get_project_id() or default_project_id
    analyzer = InfrastructureAnalyzer(project_id=project_id)
    resources = analyzer.get_infrastructure_summary()
    
    response = f"""🔍 **Infrastructure Analysis Complete for project {project_id}!**

📊 **Current Infrastructure Status:**
- Total Monthly Cost: ${resources['total_monthly_cost']}
"""

    if resources.get('vms'):
        response += f"- Virtual Machines: {len(resources['vms'])} instances\n"
    if resources.get('databases'):
        response += f"- Databases: {len(resources['databases'])} Cloud SQL instances\n"
    if resources.get('storage'):
        response += f"- Storage: {len(resources['storage'])} buckets\n"
    if resources.get('clusters'):
        response += f"- GKE Clusters: {len(resources['clusters'])} clusters\n"
    if resources.get('redis_instances'):
        response += f"- Memorystore for Redis: {len(resources['redis_instances'])} instances\n"
    if resources.get('spanner_instances'):
        response += f"- Spanner: {len(resources['spanner_instances'])} instances\n"
    if resources.get('schedulers'):
        response += f"- Cloud Schedulers: {len(resources['schedulers'])} jobs\n"
    if resources.get('run_services'):
        response += f"- Cloud Run Services: {len(resources['run_services'])} services\n"

    response += "\n💰 **Cost Breakdown:**\n"
    if resources.get('vms'):
        response += "VMs:\n" + "\n".join([f"  • {vm['name']}: ${vm['monthly_cost']}/month ({vm['type']})" for vm in resources['vms']]) + "\n"
    if resources.get('databases'):
        response += "Databases:\n" + "\n".join([f"  • {db['name']}: ${db['monthly_cost']}/month" for db in resources['databases']]) + "\n"
    if resources.get('storage'):
        response += f"Storage: {len(resources['storage'])} buckets totaling ${sum(b['monthly_cost'] for b in resources['storage']):.2f}/month.\n"
    if resources.get('clusters'):
        response += "GKE Clusters:\n" + "\n".join([f"  • {c['name']}: ${c['monthly_cost']}/month" for c in resources['clusters']]) + "\n"
    if resources.get('redis_instances'):
        response += "Memorystore for Redis:\n" + "\n".join([f"  • {r['name']}: ${r['monthly_cost']}/month" for r in resources['redis_instances']]) + "\n"
    if resources.get('spanner_instances'):
        response += "Spanner:\n" + "\n".join([f"  • {s['name']}: ${s['monthly_cost']}/month" for s in resources['spanner_instances']]) + "\n"
    if resources.get('schedulers'):
        response += "Cloud Schedulers:\n" + "\n".join([f"  • {s['name']}: ${s['monthly_cost']}/month" for s in resources['schedulers']]) + "\n"
    if resources.get('run_services'):
        response += "Cloud Run Services:\n" + "\n".join([f"  • {s['name']}: ${s['monthly_cost']}/month" for s in resources['run_services']]) + "\n"

    response += "\n🔗 **Interconnectivity:**\n"
    all_resources = (resources.get('vms', []) + resources.get('databases', []) + 
                     resources.get('storage', []) + resources.get('clusters', []) + 
                     resources.get('redis_instances', []) + resources.get('spanner_instances', []) + 
                     resources.get('schedulers', []) + resources.get('run_services', []))
    for resource in all_resources:
        if resource.get('relationships'):
            response += f"  • {resource['name']} relationships:\n"
            for rel in resource['relationships']:
                response += f"    - {rel['type']} -> {rel['target']}\n"

    return response

def generate_infrastructure_image(query: str) -> str:
    """Generates an image of the infrastructure based on the analysis and saves it to a file."""
    try:
        # 1. Get infrastructure data and generate the detailed prompt
        project_id = get_project_id() or default_project_id
        analyzer = InfrastructureAnalyzer(project_id=project_id)
        resources = analyzer.get_infrastructure_summary()
        prompt = analyzer.generate_cost_prompt(resources)

        # 2. Configure the Gemini image generation model
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

        # 3. Generate the image content
        print("Generating infrastructure image with Gemini...")
        response = model.generate_content([prompt])
        
        # 4. Decode the base64 image data and save it to a file
        image_data = base64.b64decode(response.parts[0].inline_data.data)
        file_path = 'infrastructure_diagram.png'
        with open(file_path, 'wb') as out:
            out.write(image_data)
        
        return f"🖼️ ¡Éxito! He generado el diagrama de la infraestructura y lo he guardado en el fichero '{file_path}'."

    except Exception as e:
        return f"Error al generar la imagen: {e}"

def get_google_cloud_recommendations(query: str) -> str:
    """Gets official Google Cloud optimization recommendations."""
    project_id = get_project_id() or default_project_id
    analyzer = InfrastructureAnalyzer(project_id=project_id)
    data = analyzer.get_google_recommendations()
    
    response = f"""💡 **Google Cloud Optimization Recommendations for {project_id}**

Found {data['recommendation_count']} total recommendations.
💰 **Potential Monthly Savings:** ${data['total_monthly_savings']:.2f}

"""
    
    for category, recs in data['recommendations'].items():
        if recs:
            response += f"**{category.capitalize()} Recommendations ({len(recs)}):**\n"
            response += format_recommendations(recs)
            
    return response

def format_recommendations(recs: list) -> str:
    """Formats a list of recommendations into a string."""
    formatted_string = ""
    for rec in recs:
        savings = f" (Est. Savings: ${rec['monthly_cost']}/month)" if rec['monthly_cost'] > 0 else ""
        formatted_string += f"- **{rec['type']}** on `{rec['resource']}`: {rec['description']}{savings}\n"
    return formatted_string + "\n"

root_agent = Agent(
    name="infrastructure_vision_agent",
    model="gemini-2.5-flash",
    instruction="""You are an Infrastructure Cost Optimization Agent specializing in Google Cloud Platform. 
    Your primary functions are:
    1. Analyze GCP infrastructure and identify cost optimization opportunities.
    2. Generate a visual diagram of the infrastructure using the `generate_infrastructure_image` tool.
    3. Provide actionable recommendations to reduce cloud costs.
    4. Set the project to analyze using the `set_project_id` tool.
    
    When a user asks for an image, diagram, or visualization, you must use the `generate_infrastructure_image` tool.
    For general analysis, use `analyze_infrastructure`.
    For recommendations, use `get_google_cloud_recommendations`. """,
    tools=[set_project_id, analyze_infrastructure, get_google_cloud_recommendations, generate_infrastructure_image],
)
