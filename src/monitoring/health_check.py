#!/usr/bin/env python3
"""Health Check Endpoint for AI Employee Cloud Services"""

import json
import os
import subprocess
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check requests."""
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/health':
            health = get_health_status()
            status_code = 200 if health.get('status') == 'healthy' else 503
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(health, indent=2).encode())
        elif self.path == '/ready':
            ready = get_readiness_status()
            status_code = 200 if ready.get('ready') else 503
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(ready, indent=2).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def get_health_status() -> dict:
    """Get current health status of all services."""
    return {
        "status": get_overall_status(),
        "timestamp": datetime.now().isoformat(),
        "uptime": get_uptime(),
        "services": {
            "watchers": check_service("ai-employee-cloud"),
            "orchestrator": check_service("ai-employee-orchestrator"),
            "health": check_service("ai-employee-health"),
            "odoo": check_odoo(),
            "nginx": check_nginx(),
        }
    }


def get_readiness_status() -> dict:
    """Check if service is ready to accept traffic."""
    odoo_ok = check_odoo().get('status') == 'healthy'
    return {
        "ready": odoo_ok,
        "checks": {
            "odoo": odoo_ok,
        }
    }


def get_overall_status() -> str:
    """Determine overall health status."""
    services = [
        check_service("ai-employee-cloud"),
        check_service("ai-employee-orchestrator"),
        check_odoo(),
    ]
    
    critical_count = sum(1 for s in services if s.get('status') == 'failed')
    
    if critical_count == 0:
        return "healthy"
    elif critical_count <= 1:
        return "degraded"
    else:
        return "failed"


def get_uptime() -> str:
    """Get system uptime."""
    try:
        result = subprocess.run(['uptime', '-p'], capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"


def check_service(service_name: str) -> dict:
    """Check if systemd service is running."""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', service_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        status = "healthy" if result.stdout.strip() == "active" else "failed"
        return {
            "status": status,
            "details": result.stdout.strip(),
        }
    except Exception as e:
        return {
            "status": "failed",
            "details": str(e),
        }


def check_odoo() -> dict:
    """Check if Odoo is accessible."""
    import requests
    try:
        odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
        response = requests.get(odoo_url, timeout=5)
        if response.status_code == 200:
            return {
                "status": "healthy",
                "url": odoo_url,
            }
        else:
            return {
                "status": "degraded",
                "url": odoo_url,
                "details": f"HTTP {response.status_code}",
            }
    except Exception as e:
        return {
            "status": "failed",
            "details": str(e),
        }


def check_nginx() -> dict:
    """Check if Nginx is running."""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', 'nginx'],
            capture_output=True,
            text=True,
            timeout=5
        )
        status = "healthy" if result.stdout.strip() == "active" else "failed"
        return {
            "status": status,
            "details": result.stdout.strip(),
        }
    except Exception as e:
        return {
            "status": "failed",
            "details": str(e),
        }


def main():
    """Start health check server."""
    port = int(os.getenv('HEALTH_CHECK_PORT', 8080))
    server = HTTPServer(('0.0.0.0', port), HealthHandler)
    logger.info(f"Health check server running on port {port}")
    print(f"Health check endpoint: http://localhost:{port}/health")
    print(f"Readiness endpoint: http://localhost:{port}/ready")
    server.serve_forever()


if __name__ == '__main__':
    main()
