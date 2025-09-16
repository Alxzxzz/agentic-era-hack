# Enhanced main.py with Cloud Monitoring integration
import datetime
import os
from zoneinfo import ZoneInfo
import json

import google.auth
from google.adk.agents import Agent
from app.infrastructure_analyzer import InfrastructureAnalyzer
from app.monitoring_analyzer import MonitoringAnalyzer  # New import
from app.state_manager import get_project_id, set_project_id

_, default_project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", default_project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


def analyze_infrastructure_with_monitoring(query: str) -> str:
    """Enhanced infrastructure analysis including Cloud Monitoring metrics.
    
    Args:
        query: User query about infrastructure analysis
    
    Returns:
        Comprehensive infrastructure and utilization analysis with actionable recommendations
    """
    project_id = get_project_id() or default_project_id
    
    # Get basic infrastructure info
    infrastructure_analyzer = InfrastructureAnalyzer(project_id=project_id)
    resources = infrastructure_analyzer.get_infrastructure_summary()
    
    # Get monitoring metrics
    monitoring_analyzer = MonitoringAnalyzer(project_id=project_id)
    
    response = f"""🔍 **Enhanced Infrastructure Analysis for project `{project_id}`**

📊 **Current Infrastructure Status:**
- Total Monthly Cost: ${resources['total_monthly_cost']}
"""

    if resources['vms']:
        response += f"- Virtual Machines: {len(resources['vms'])} instances\n"
    if resources['databases']:
        response += f"- Databases: {len(resources['databases'])} Cloud SQL instances\n"
    if resources['storage']:
        response += f"- Storage: {len(resources['storage'])} buckets\n"

    response += "\n💰 **Cost Breakdown with Utilization Analysis:**\n"
    
    # Enhanced VM analysis with monitoring data
    if resources['vms']:
        response += "**Virtual Machines:**\n"
        
        # Get utilization for all VMs
        vm_analyses = monitoring_analyzer.get_all_instances_analysis()
        
        for vm in resources['vms']:
            response += f"  • **{vm['name']}**: ${vm['monthly_cost']}/month ({vm['type']})\n"
            
            # Find matching monitoring analysis
            vm_analysis = next((analysis for analysis in vm_analyses 
                              if analysis['instance_name'] == vm['name']), None)
            
            if vm_analysis:
                metrics = vm_analysis['metrics_summary']
                
                if 'cpu_utilization' in metrics and metrics['cpu_utilization']['status'] != 'no_data':
                    cpu_avg = metrics['cpu_utilization']['average']
                    cpu_p95 = metrics['cpu_utilization']['p95']
                    response += f"    📈 CPU: {cpu_avg:.1f}% avg, {cpu_p95:.1f}% p95\n"
                
                if 'memory_utilization' in metrics and metrics['memory_utilization']['status'] != 'no_data':
                    mem_avg = metrics['memory_utilization']['average']
                    mem_p95 = metrics['memory_utilization']['p95']
                    response += f"    🧠 Memory: {mem_avg:.1f}% avg, {mem_p95:.1f}% p95\n"
                
                # Show optimization potential
                if vm_analysis['optimization_potential'] != 'none':
                    response += f"    🎯 Optimization Potential: {vm_analysis['optimization_potential'].upper()}\n"
                
                response += "\n"
            else:
                response += "    ⚠️ No monitoring data available (install Cloud Monitoring agent)\n\n"

    # Database analysis
    if resources['databases']:
        response += "**Databases:**\n"
        project_metrics = monitoring_analyzer.get_project_wide_metrics_summary()
        
        for db in resources['databases']:
            response += f"  • **{db['name']}**: ${db['monthly_cost']}/month\n"
        
        if 'cloud_sql_metrics' in project_metrics and project_metrics['cloud_sql_metrics']['status'] != 'no_cloud_sql_instances':
            sql_metrics = project_metrics['cloud_sql_metrics']
            response += f"    📈 Average CPU: {sql_metrics['cpu_avg']:.1f}%\n"
            response += f"    📈 Peak CPU: {sql_metrics['cpu_max']:.1f}%\n"
        
        response += "\n"

    # Storage analysis
    if resources['storage']:
        response += "**Storage:**\n"
        for bucket in resources['storage']:
            response += f"  • **{bucket['name']}**: ${bucket['monthly_cost']}/month ({bucket['size_gb']}GB)\n"
        response += "\n"

    # Network cost analysis
    project_metrics = monitoring_analyzer.get_project_wide_metrics_summary()
    if project_metrics['network_egress_gb'] > 0:
        estimated_egress_cost = project_metrics['network_egress_gb'] * 0.12  # Approx $0.12/GB
        response += f"**Network Usage (Last 30 days):**\n"
        response += f"  • Egress: {project_metrics['network_egress_gb']:.2f} GB (~${estimated_egress_cost:.2f})\n\n"

    # Comprehensive recommendations
    response += "🎯 **Optimization Recommendations:**\n"
    
    total_potential_savings = resources['potential_savings']
    high_priority_recommendations = []
    medium_priority_recommendations = []
    
    # Collect all recommendations from monitoring analysis
    for vm_analysis in vm_analyses:
        for rec in vm_analysis.get('recommendations', []):
            if rec['priority'] == 'high':
                high_priority_recommendations.append(rec)
            else:
                medium_priority_recommendations.append(rec)
    
    # Add SQL and LB recommendations
    if 'cloud_sql_metrics' in project_metrics and 'recommendations' in project_metrics['cloud_sql_metrics']:
        for rec in project_metrics['cloud_sql_metrics']['recommendations']:
            if rec['priority'] == 'high':
                high_priority_recommendations.append(rec)
            else:
                medium_priority_recommendations.append(rec)

    if high_priority_recommendations:
        response += "**🔴 High Priority:**\n"
        for rec in high_priority_recommendations:
            response += f"  • {rec['message']}\n"
            if 'potential_savings_pct' in rec:
                response += f"    💰 Potential savings: ~{rec['potential_savings_pct']}%\n"
        response += "\n"
    
    if medium_priority_recommendations:
        response += "**🟡 Medium Priority:**\n"
        for rec in medium_priority_recommendations:
            response += f"  • {rec['message']}\n"
            if 'potential_savings_pct' in rec:
                response += f"    💰 Potential savings: ~{rec['potential_savings_pct']}%\n"
        response += "\n"

    if total_potential_savings > 0:
        response += f"💡 **Total Estimated Monthly Savings: ${total_potential_savings:.2f}**\n"
        response += f"📈 **Annual Savings Potential: ${total_potential_savings * 12:.2f}**\n\n"

    response += "📊 *Analysis based on 30-day historical data. Install Cloud Monitoring agent for more detailed metrics.*"
    
    return response


def get_detailed_vm_analysis(query: str) -> str:
    """Get detailed analysis for a specific VM instance.
    
    Args:
        query: Should contain the VM instance name
    
    Returns:
        Detailed utilization analysis and recommendations for specific VM
    """
    project_id = get_project_id() or default_project_id
    monitoring_analyzer = MonitoringAnalyzer(project_id=project_id)
    
    # Extract instance name from query (simple approach - could be enhanced)
    instance_name = query.replace("analyze vm ", "").replace("vm analysis ", "").strip()
    
    if not instance_name:
        return "Please specify the VM instance name. Example: 'analyze vm instance-20250916-103223'"
    
    try:
        # Get all instances to find the correct zone
        vm_analyses = monitoring_analyzer.get_all_instances_analysis()
        vm_analysis = next((analysis for analysis in vm_analyses 
                           if analysis['instance_name'] == instance_name), None)
        
        if not vm_analysis:
            return f"❌ Instance '{instance_name}' not found or not running."
        
        response = f"""🔍 **Detailed Analysis for VM: {instance_name}**

📋 **Instance Details:**
- Zone: {vm_analysis['zone']}
- Machine Type: {vm_analysis['machine_type']}
- Optimization Potential: {vm_analysis['optimization_potential'].upper()}

📊 **Utilization Metrics (30-day average):**
"""
        
        metrics = vm_analysis['metrics_summary']
        
        for metric_name, metric_data in metrics.items():
            if metric_data['status'] == 'no_data':
                response += f"- **{metric_name.replace('_', ' ').title()}**: {metric_data['message']}\n"
            else:
                response += f"- **{metric_name.replace('_', ' ').title()}**: {metric_data['average']:.1f}% avg, {metric_data['maximum']:.1f}% max, {metric_data['p95']:.1f}% p95\n"
        
        response += "\n🎯 **Specific Recommendations:**\n"
        
        if vm_analysis['recommendations']:
            for rec in vm_analysis['recommendations']:
                priority_icon = "🔴" if rec['priority'] == 'high' else "🟡"
                response += f"{priority_icon} **{rec['type'].replace('_', ' ').title()}**: {rec['message']}\n"
                if 'potential_savings_pct' in rec:
                    response += f"   💰 Estimated savings: {rec['potential_savings_pct']}%\n"
                response += "\n"
        else:
            response += "✅ No optimization recommendations at this time.\n"
        
        return response
        
    except Exception as e:
        return f"❌ Error analyzing VM: {str(e)}"


def analyze_infrastructure(query: str) -> str:
    """Original function maintained for backward compatibility."""
    return analyze_infrastructure_with_monitoring(query)


def generate_cost_visualization(query: str) -> str:
    """Generates a prompt for creating infrastructure cost visualization.
    
    Args:
        query: Request for visualization
    
    Returns:
        Detailed prompt for image generation
    """
    project_id = get_project_id() or default_project_id
    analyzer = InfrastructureAnalyzer(project_id=project_id)
    resources = analyzer.get_infrastructure_summary()
    prompt = analyzer.generate_cost_prompt(resources)
    
    return f"""
🎨 **Visualization Prompt Generated for project {project_id}!**

I've created a detailed prompt for generating your infrastructure diagram:

{prompt}

📊 This visualization will show:
- All your GCP resources with cost indicators
- Red highlights for expensive items (>${100}/month)
- Green indicators for optimization opportunities
- Professional cloud architecture diagram style

To generate the actual image, this prompt can be used with Vertex AI's Imagen model.
"""


def get_google_cloud_recommendations(query: str) -> str:
    """Obtiene recomendaciones oficiales de optimización de Google Cloud en formato JSON."""
    project_id = get_project_id() or default_project_id
    analyzer = InfrastructureAnalyzer(project_id=project_id)
    recommendations = analyzer.get_google_recommendations()
    return json.dumps(recommendations, indent=2)


# Keep existing utility functions
def get_weather(query: str) -> str:
    """Simulates a web search. Use it get information on weather."""
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."

def get_current_time(query: str) -> str:
    """Simulates getting the current time for a city."""
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
    instruction="""You are an Enhanced Infrastructure Cost Optimization Agent specializing in Google Cloud Platform. 
    Your primary functions are:
    
    1. Analyze GCP infrastructure with real utilization metrics from Cloud Monitoring
    2. Identify cost optimization opportunities based on actual resource usage
    3. Provide specific, actionable recommendations with estimated savings
    4. Generate visualization prompts for infrastructure diagrams
    5. Set the project to analyze using the set_project_id tool
    6. Perform detailed analysis of specific VMs when requested
    
    Key capabilities:
    - Real-time CPU, memory, network, and disk utilization analysis
    - Historical pattern analysis (30-day default)
    - Right-sizing recommendations based on actual usage
    - Network cost optimization
    - Cloud SQL performance analysis
    - Load balancer usage optimization
    
    When users ask about infrastructure, costs, or optimization, use the analyze_infrastructure_with_monitoring 
    function for comprehensive analysis. For detailed VM analysis, use get_detailed_vm_analysis.
    
    Be specific in recommendations and always include estimated savings percentages when available.
    Proactively suggest installing Cloud Monitoring agent if metrics are missing.""",
    tools=[
        set_project_id, 
        analyze_infrastructure_with_monitoring, 
        get_detailed_vm_analysis,
        get_google_cloud_recommendations, 
        generate_cost_visualization, 
        get_weather, 
        get_current_time
    ],
)