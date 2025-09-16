# app/monitoring_analyzer.py
import datetime
from typing import Dict, List, Optional, Any
from google.cloud import monitoring_v3
from google.cloud.monitoring_v3 import query
import statistics

class MonitoringAnalyzer:
    """Analyzes Cloud Monitoring metrics for cost optimization."""
    
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.client = monitoring_v3.MetricServiceClient()
        self.project_name = f"projects/{project_id}"
    
    def get_vm_utilization_metrics(self, instance_name: str, zone: str, days_back: int = 30) -> Dict[str, Any]:
        """Get CPU, memory, and network utilization for a specific VM instance."""
        
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=days_back)
        
        metrics = {
            'cpu_utilization': self._get_cpu_utilization(instance_name, zone, start_time, end_time),
            'memory_utilization': self._get_memory_utilization(instance_name, zone, start_time, end_time),
            'network_bytes_in': self._get_network_metrics(instance_name, zone, start_time, end_time, 'received'),
            'network_bytes_out': self._get_network_metrics(instance_name, zone, start_time, end_time, 'sent'),
            'disk_read_bytes': self._get_disk_metrics(instance_name, zone, start_time, end_time, 'read'),
            'disk_write_bytes': self._get_disk_metrics(instance_name, zone, start_time, end_time, 'write')
        }
        
        return self._analyze_utilization(metrics, instance_name)
    
    def _get_cpu_utilization(self, instance_name: str, zone: str, start_time: datetime.datetime, end_time: datetime.datetime) -> List[float]:
        """Get CPU utilization metrics."""
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(end_time.timestamp())},
            "start_time": {"seconds": int(start_time.timestamp())},
        })
        
        results = self.client.list_time_series(
            request={
                "name": self.project_name,
                "filter": f'metric.type="compute.googleapis.com/instance/cpu/utilization" '
                         f'AND resource.labels.instance_name="{instance_name}" '
                         f'AND resource.labels.zone="{zone}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        
        values = []
        for result in results:
            for point in result.points:
                values.append(point.value.double_value * 100)  # Convert to percentage
        
        return values
    
    def _get_memory_utilization(self, instance_name: str, zone: str, start_time: datetime.datetime, end_time: datetime.datetime) -> List[float]:
        """Get memory utilization metrics."""
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(end_time.timestamp())},
            "start_time": {"seconds": int(start_time.timestamp())},
        })
        
        # Memory utilization requires the monitoring agent
        results = self.client.list_time_series(
            request={
                "name": self.project_name,
                "filter": f'metric.type="agent.googleapis.com/memory/percent_used" '
                         f'AND resource.labels.instance_id="{instance_name}" '
                         f'AND resource.labels.zone="{zone}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        
        values = []
        for result in results:
            for point in result.points:
                values.append(point.value.double_value)
        
        return values
    
    def _get_network_metrics(self, instance_name: str, zone: str, start_time: datetime.datetime, 
                           end_time: datetime.datetime, direction: str) -> List[float]:
        """Get network bytes sent/received metrics."""
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(end_time.timestamp())},
            "start_time": {"seconds": int(start_time.timestamp())},
        })
        
        metric_type = f"compute.googleapis.com/instance/network/bytes_{direction}"
        
        results = self.client.list_time_series(
            request={
                "name": self.project_name,
                "filter": f'metric.type="{metric_type}" '
                         f'AND resource.labels.instance_name="{instance_name}" '
                         f'AND resource.labels.zone="{zone}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        
        values = []
        for result in results:
            for point in result.points:
                values.append(point.value.int64_value)
        
        return values
    
    def _get_disk_metrics(self, instance_name: str, zone: str, start_time: datetime.datetime, 
                         end_time: datetime.datetime, operation: str) -> List[float]:
        """Get disk read/write metrics."""
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(end_time.timestamp())},
            "start_time": {"seconds": int(start_time.timestamp())},
        })
        
        metric_type = f"compute.googleapis.com/instance/disk/{operation}_bytes_count"
        
        results = self.client.list_time_series(
            request={
                "name": self.project_name,
                "filter": f'metric.type="{metric_type}" '
                         f'AND resource.labels.instance_name="{instance_name}" '
                         f'AND resource.labels.zone="{zone}"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        
        values = []
        for result in results:
            for point in result.points:
                values.append(point.value.int64_value)
        
        return values
    
    def _analyze_utilization(self, metrics: Dict[str, List[float]], instance_name: str) -> Dict[str, Any]:
        """Analyze metrics and generate optimization recommendations."""
        
        analysis = {
            'instance_name': instance_name,
            'metrics_summary': {},
            'recommendations': [],
            'optimization_potential': 'none'
        }
        
        for metric_name, values in metrics.items():
            if not values:
                analysis['metrics_summary'][metric_name] = {
                    'status': 'no_data',
                    'message': 'No monitoring data available. Consider installing Cloud Monitoring agent.'
                }
                continue
            
            avg_value = statistics.mean(values)
            max_value = max(values)
            p95_value = statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max_value
            
            analysis['metrics_summary'][metric_name] = {
                'average': round(avg_value, 2),
                'maximum': round(max_value, 2),
                'p95': round(p95_value, 2),
                'data_points': len(values)
            }
            
            # Generate specific recommendations based on metrics
            if metric_name == 'cpu_utilization':
                if avg_value < 20 and p95_value < 50:
                    analysis['recommendations'].append({
                        'type': 'right_sizing',
                        'priority': 'high',
                        'message': f'CPU utilization very low (avg: {avg_value:.1f}%, p95: {p95_value:.1f}%). Consider downsizing instance type.',
                        'potential_savings_pct': 30
                    })
                    analysis['optimization_potential'] = 'high'
                elif avg_value < 35 and p95_value < 70:
                    analysis['recommendations'].append({
                        'type': 'right_sizing',
                        'priority': 'medium',
                        'message': f'CPU utilization moderate (avg: {avg_value:.1f}%, p95: {p95_value:.1f}%). Could benefit from smaller instance.',
                        'potential_savings_pct': 15
                    })
                    if analysis['optimization_potential'] == 'none':
                        analysis['optimization_potential'] = 'medium'
            
            elif metric_name == 'memory_utilization':
                if avg_value < 30 and p95_value < 60:
                    analysis['recommendations'].append({
                        'type': 'memory_optimization',
                        'priority': 'medium',
                        'message': f'Memory utilization low (avg: {avg_value:.1f}%, p95: {p95_value:.1f}%). Consider memory-optimized instance.',
                        'potential_savings_pct': 20
                    })
        
        return analysis
    
    def get_all_instances_analysis(self) -> List[Dict[str, Any]]:
        """Get utilization analysis for all compute instances in the project."""
        
        from google.cloud import compute_v1
        
        compute_client = compute_v1.InstancesClient()
        zones_client = compute_v1.ZonesClient()
        
        # Get all zones
        zones = zones_client.list(project=self.project_id)
        
        all_instances_analysis = []
        
        for zone in zones:
            zone_name = zone.name
            
            try:
                instances = compute_client.list(project=self.project_id, zone=zone_name)
                
                for instance in instances:
                    if instance.status == "RUNNING":
                        print(f"Analyzing instance: {instance.name} in zone: {zone_name}")
                        analysis = self.get_vm_utilization_metrics(instance.name, zone_name)
                        analysis['zone'] = zone_name
                        analysis['machine_type'] = instance.machine_type.split('/')[-1]
                        all_instances_analysis.append(analysis)
            
            except Exception as e:
                print(f"Error analyzing zone {zone_name}: {e}")
                continue
        
        return all_instances_analysis
    
    def get_project_wide_metrics_summary(self, days_back: int = 30) -> Dict[str, Any]:
        """Get project-wide metrics summary including network costs."""
        
        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days=days_back)
        
        # Get total network egress (expensive!)
        network_egress = self._get_total_network_egress(start_time, end_time)
        
        # Get Cloud SQL metrics if any
        sql_metrics = self._get_cloud_sql_metrics(start_time, end_time)
        
        # Get Load Balancer metrics
        lb_metrics = self._get_load_balancer_metrics(start_time, end_time)
        
        return {
            'network_egress_gb': network_egress,
            'cloud_sql_metrics': sql_metrics,
            'load_balancer_metrics': lb_metrics,
            'period_analyzed_days': days_back
        }
    
    def _get_total_network_egress(self, start_time: datetime.datetime, end_time: datetime.datetime) -> float:
        """Get total network egress in GB (important for cost optimization)."""
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(end_time.timestamp())},
            "start_time": {"seconds": int(start_time.timestamp())},
        })
        
        results = self.client.list_time_series(
            request={
                "name": self.project_name,
                "filter": 'metric.type="compute.googleapis.com/instance/network/sent_bytes_count"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        
        total_bytes = 0
        for result in results:
            for point in result.points:
                total_bytes += point.value.int64_value
        
        return total_bytes / (1024**3)  # Convert to GB
    
    def _get_cloud_sql_metrics(self, start_time: datetime.datetime, end_time: datetime.datetime) -> Dict[str, Any]:
        """Get Cloud SQL performance metrics."""
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(end_time.timestamp())},
            "start_time": {"seconds": int(start_time.timestamp())},
        })
        
        # CPU utilization for Cloud SQL
        cpu_results = self.client.list_time_series(
            request={
                "name": self.project_name,
                "filter": 'metric.type="cloudsql.googleapis.com/database/cpu/utilization"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        
        cpu_values = []
        for result in cpu_results:
            for point in result.points:
                cpu_values.append(point.value.double_value * 100)
        
        if cpu_values:
            return {
                'cpu_avg': statistics.mean(cpu_values),
                'cpu_max': max(cpu_values),
                'recommendations': self._generate_sql_recommendations(statistics.mean(cpu_values))
            }
        
        return {'status': 'no_cloud_sql_instances'}
    
    def _get_load_balancer_metrics(self, start_time: datetime.datetime, end_time: datetime.datetime) -> Dict[str, Any]:
        """Get Load Balancer metrics for cost optimization."""
        
        interval = monitoring_v3.TimeInterval({
            "end_time": {"seconds": int(end_time.timestamp())},
            "start_time": {"seconds": int(start_time.timestamp())},
        })
        
        # Request count for load balancers
        results = self.client.list_time_series(
            request={
                "name": self.project_name,
                "filter": 'metric.type="loadbalancing.googleapis.com/https/request_count"',
                "interval": interval,
                "view": monitoring_v3.ListTimeSeriesRequest.TimeSeriesView.FULL,
            }
        )
        
        request_counts = []
        for result in results:
            for point in result.points:
                request_counts.append(point.value.int64_value)
        
        if request_counts:
            total_requests = sum(request_counts)
            return {
                'total_requests': total_requests,
                'avg_requests_per_day': total_requests / 30,
                'recommendations': self._generate_lb_recommendations(total_requests)
            }
        
        return {'status': 'no_load_balancers'}
    
    def _generate_sql_recommendations(self, avg_cpu: float) -> List[Dict[str, Any]]:
        """Generate Cloud SQL optimization recommendations."""
        recommendations = []
        
        if avg_cpu < 20:
            recommendations.append({
                'type': 'cloud_sql_right_sizing',
                'priority': 'high',
                'message': f'Cloud SQL CPU utilization very low ({avg_cpu:.1f}%). Consider smaller machine type.',
                'potential_savings_pct': 25
            })
        
        return recommendations
    
    def _generate_lb_recommendations(self, total_requests: int) -> List[Dict[str, Any]]:
        """Generate Load Balancer optimization recommendations."""
        recommendations = []
        
        if total_requests < 10000:  # Very low traffic
            recommendations.append({
                'type': 'load_balancer_optimization',
                'priority': 'medium',
                'message': f'Low request volume ({total_requests} requests/month). Consider if LB is necessary.',
                'potential_savings_pct': 100
            })
        
        return recommendations