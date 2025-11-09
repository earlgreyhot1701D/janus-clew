#!/usr/bin/env python3
"""Minimal server that works with Python 3.13."""

import sys
import os
import json
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    import urllib.parse as urlparse
    
    class JanusHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith('/api/'):
                self.handle_api()
            else:
                # Always serve the dashboard HTML
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'''
                <html><body>
                <h1>🧵 Janus Clew Dashboard</h1>
                <p><strong>Server Status:</strong> Running</p>
                <h2>API Endpoints:</h2>
                <ul>
                    <li><a href="/api/health">Health Check</a></li>
                    <li><a href="/api/analyses">All Analyses</a></li>
                    <li><a href="/api/timeline">Timeline Data</a></li>
                    <li><a href="/api/skills">Skills Data</a></li>
                </ul>
                <h2>Demo Data Available</h2>
                <p>The server is running with mock data. Click the API links above to see the JSON responses.</p>
                </body></html>
                ''')
        
        def handle_api(self):
            # Mock API responses
            mock_data = {
                '/api/health': {
                    'status': 'ok',
                    'version': '0.2.0',
                    'analyses_stored': 1
                },
                '/api/analyses': {
                    'status': 'success',
                    'count': 1,
                    'analyses': [{
                        'timestamp': '2025-11-08_10-30-00',
                        'projects': [
                            {
                                'name': 'Demo-Project',
                                'complexity_score': 7.5,
                                'technologies': ['Python', 'FastAPI']
                            }
                        ],
                        'overall': {
                            'avg_complexity': 7.5,
                            'total_projects': 1,
                            'growth_rate': 25.0
                        }
                    }]
                },
                '/api/timeline': {
                    'status': 'success',
                    'timeline': [{
                        'date': '2025-11-08_10-30-00',
                        'project_name': 'Demo-Project',
                        'complexity': 7.5,
                        'skills': ['Python', 'FastAPI']
                    }]
                },
                '/api/skills': {
                    'status': 'success',
                    'skills': [
                        {'name': 'Python', 'confidence': 0.9, 'projects': ['Demo-Project']},
                        {'name': 'FastAPI', 'confidence': 0.8, 'projects': ['Demo-Project']}
                    ]
                }
            }
            
            response_data = mock_data.get(self.path, {'error': 'Not found'})
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode())

    if __name__ == '__main__':
        port = 8000
        server = HTTPServer(('127.0.0.1', port), JanusHandler)
        print(f"Janus Clew server running on http://127.0.0.1:{port}")
        print("Press Ctrl+C to stop")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped")
            server.shutdown()

except ImportError as e:
    print(f"Import error: {e}")
    print("Using basic HTTP server...")