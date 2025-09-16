# Copyright 2025 Google LLC
import datetime
import os
from zoneinfo import ZoneInfo

import google.auth
from google.adk.agents import Agent
from app.infrastructure_analyzer import InfrastructureAnalyzer

_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


def analyze_infrastructure(query: str) -> str:
    """Analyzes GCP infrastructure and returns cost analysis.
    
    Args:
        query: User query about infrastructure analysis
    
    Returns:
        Detailed infrastructure and cost analysis
    """
    analyzer = InfrastructureAnalyzer(project_id=project_id)
    resources = analyzer.get_infrastructure_summary()
    
    return f"""
🔍 **Infrastructure Analysis Complete!**

📊 **Current Infrastructure Status:**
- Total Monthly Cost: ${resources['total_monthly_cost']}
- Virtual Machines: {len(resources['vms'])} instances
- Databases: {len(resources['databases'])} Cloud SQL instances  
- Storage: {len(resources['storage'])} buckets

💰 **Cost Breakdown:**
VMs:
{chr(10).join([f"  • {vm['name']}: ${vm['monthly_cost']}/month ({vm['type']})" for vm in resources['vms']])}

Databases:
{chr(10).join([f"  • {db['name']}: ${db['monthly_cost']}/month" for db in resources['databases']])}

Storage:
{chr(10).join([f"  • {bucket['name']}: ${bucket['monthly_cost']}/month ({bucket['size_gb']}GB)" for bucket in resources['storage']])}

💡 **Optimization Opportunities:**
- Potential monthly savings: ${resources['potential_savings']}
- Recommendations:
  1. Rightsize overprovisioned VMs
  2. Enable auto-shutdown for dev/test environments
  3. Use committed use discounts for predictable workloads
"""


def generate_cost_visualization(query: str) -> str:
    """Generates a prompt for creating infrastructure cost visualization.
    
    Args:
        query: Request for visualization
    
    Returns:
        Detailed prompt for image generation
    """
    analyzer = InfrastructureAnalyzer(project_id=project_id)
    resources = analyzer.get_infrastructure_summary()
    prompt = analyzer.generate_cost_prompt(resources)
    
    return f"""
🎨 **Visualization Prompt Generated!**

I've created a detailed prompt for generating your infrastructure diagram:

{prompt}

📊 This visualization will show:
- All your GCP resources with cost indicators
- Red highlights for expensive items (>${100}/month)
- Green indicators for optimization opportunities
- Professional cloud architecture diagram style

To generate the actual image, this prompt can be used with Vertex AI's Imagen model.
"""


def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with the simulated weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city.

    Args:
        city: The name of the city to get the current time for.

    Returns:
        A string with the current time information.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        tz_identifier = "America/Los_Angeles"
    else:
        return f"Sorry, I don't have timezone information for query: {query}."

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    return f"The current time for query {query} is {now.strftime('%Y-%m-%d %H:%M:%S %Z%z')}"


root_agent = Agent(
    name="infrastructure_vision_agent",
    model="gemini-2.5-flash",
    instruction="""You are an Infrastructure Cost Optimization Agent specializing in Google Cloud Platform. 
    Your primary functions are:
    1. Analyze GCP infrastructure and identify cost optimization opportunities
    2. Generate visualization prompts for infrastructure diagrams
    3. Provide actionable recommendations to reduce cloud costs
    
    When users ask about infrastructure, costs, or optimization, use the analyze_infrastructure 
    and generate_cost_visualization tools. Be helpful and proactive in suggesting cost savings.""",
    tools=[analyze_infrastructure, generate_cost_visualization, get_weather, get_current_time],
)
