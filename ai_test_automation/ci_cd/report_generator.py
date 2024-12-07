import json
import os
from datetime import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

class ReportGenerator:
    def __init__(self):
        self.test_results_dir = 'test_results'
        self.execution_results = self._load_json('execution_results.json')
        self.anomaly_results = self._load_json('anomaly_analysis.json')
        self.report_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    def _load_json(self, filename: str) -> Dict:
        """Load JSON file from test results directory"""
        filepath = os.path.join(self.test_results_dir, filename)
        with open(filepath, 'r') as f:
            return json.load(f)

    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generate summary statistics from test results"""
        total_tests = len(self.execution_results)
        passed_tests = sum(1 for test in self.execution_results if test['passed'])
        failed_tests = total_tests - passed_tests
        
        total_anomalies = self.anomaly_results['summary']['total_anomalies']
        
        avg_response_time = sum(test['response_time'] for test in self.execution_results) / total_tests
        
        return {
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'failed_tests': failed_tests,
            'pass_rate': (passed_tests / total_tests) * 100,
            'total_anomalies': total_anomalies,
            'average_response_time': avg_response_time
        }

    def generate_response_time_plot(self):
        """Generate response time distribution plot"""
        response_times = [test['response_time'] for test in self.execution_results]
        plt.figure(figsize=(10, 6))
        sns.histplot(response_times, bins=30)
        plt.title('Response Time Distribution')
        plt.xlabel('Response Time (seconds)')
        plt.ylabel('Count')
        plt.savefig(os.path.join(self.test_results_dir, 'response_time_dist.png'))
        plt.close()

    def generate_endpoint_stats(self) -> pd.DataFrame:
        """Generate statistics per endpoint"""
        endpoint_stats = {}
        
        for test in self.execution_results:
            endpoint = test['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'avg_response_time': 0.0
                }
            
            stats = endpoint_stats[endpoint]
            stats['total'] += 1
            stats['passed'] += 1 if test['passed'] else 0
            stats['failed'] += 0 if test['passed'] else 1
            stats['avg_response_time'] += test['response_time']
        
        # Calculate averages
        for stats in endpoint_stats.values():
            stats['avg_response_time'] /= stats['total']
            stats['pass_rate'] = (stats['passed'] / stats['total']) * 100
        
        return pd.DataFrame.from_dict(endpoint_stats, orient='index')

    def generate_markdown_report(self):
        """Generate comprehensive markdown report"""
        stats = self.generate_summary_stats()
        endpoint_stats = self.generate_endpoint_stats()
        
        report = f"""# Test Automation Report
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary Statistics
- Total Tests Executed: {stats['total_tests']}
- Tests Passed: {stats['passed_tests']}
- Tests Failed: {stats['failed_tests']}
- Pass Rate: {stats['pass_rate']:.2f}%
- Average Response Time: {stats['average_response_time']:.3f}s

## Anomaly Detection Results
- Total Anomalies Found: {stats['total_anomalies']}
- Response Time Anomalies: {self.anomaly_results['summary']['response_time_anomalies']}
- Status Code Anomalies: {self.anomaly_results['summary']['status_code_anomalies']}
- Pattern Anomalies: {self.anomaly_results['summary']['pattern_anomalies']}

## Endpoint Performance

{endpoint_stats.to_markdown()}

## Anomaly Details
"""
        
        # Add anomaly details
        for anomaly_type, anomalies in self.anomaly_results['anomalies'].items():
            report += f"\n### {anomaly_type.replace('_', ' ').title()} Anomalies\n"
            for anomaly in anomalies:
                report += f"- Endpoint: {anomaly['endpoint']}\n"
                report += f"  - Method: {anomaly['method']}\n"
                report += f"  - Response Time: {anomaly.get('response_time', 'N/A')}s\n"
        
        # Save report
        report_path = os.path.join(self.test_results_dir, f'test_report_{self.report_time}.md')
        with open(report_path, 'w') as f:
            f.write(report)

    def generate_html_dashboard(self):
        """Generate HTML dashboard with interactive visualizations"""
        stats = self.generate_summary_stats()
        endpoint_stats = self.generate_endpoint_stats()
        
        html_template = f"""
        <html>
        <head>
            <title>Test Automation Dashboard</title>
            <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
            <style>
                .card {{ margin: 15px; }}
                .stats-card {{ text-align: center; padding: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="text-center my-4">Test Automation Dashboard</h1>
                
                <div class="row">
                    <div class="col-md-3">
                        <div class="card stats-card">
                            <h3>Pass Rate</h3>
                            <h4>{stats['pass_rate']:.1f}%</h4>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stats-card">
                            <h3>Total Tests</h3>
                            <h4>{stats['total_tests']}</h4>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stats-card">
                            <h3>Anomalies</h3>
                            <h4>{stats['total_anomalies']}</h4>
                        </div>
                    </div>
                    <div class="col-md-3">
                        <div class="card stats-card">
                            <h3>Avg Response</h3>
                            <h4>{stats['average_response_time']:.3f}s</h4>
                        </div>
                    </div>
                </div>
                
                <div class="row">
                    <div class="col-12">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">Endpoint Performance</h5>
                                <div id="endpoint-plot"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <script>
                // Create endpoint performance plot
                const endpointData = {endpoint_stats.to_dict(orient='records')};
                Plotly.newPlot('endpoint-plot', [{{
                    x: Object.keys(endpointData),
                    y: Object.values(endpointData).map(d => d.pass_rate),
                    type: 'bar',
                    name: 'Pass Rate'
                }}]);
            </script>
        </body>
        </html>
        """
        
        dashboard_path = os.path.join(self.test_results_dir, f'dashboard_{self.report_time}.html')
        with open(dashboard_path, 'w') as f:
            f.write(html_template)

def main():
    generator = ReportGenerator()
    generator.generate_response_time_plot()
    generator.generate_markdown_report()
    generator.generate_html_dashboard()

if __name__ == "__main__":
    main()