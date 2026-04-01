"""
Health Check Endpoint for AI Employee System - Platinum Tier

Provides /health endpoint that checks:
- Watchers alive (Gmail, WhatsApp, Filesystem)
- Ralph loop not stuck
- Odoo pingable
- Twilio credentials present
- Overall system health

Usage:
  python -m src.monitoring.health_check
"""

import json
import logging
import os
import socket
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class HealthChecker:
    """
    Comprehensive health checker for AI Employee system.
    """
    
    def __init__(self, vault_path: str = None):
        """
        Initialize health checker.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path) if vault_path else Path.cwd() / "AI_Employee_Vault"
        self.logs_dir = self.vault_path / "Logs"
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)
    
    def check_watcher_process(self, name: str) -> bool:
        """
        Check if watcher process is running.
        
        Args:
            name: Watcher name (gmail, whatsapp, filesystem)
            
        Returns:
            True if running
        """
        try:
            # Check PID file if exists
            pid_file = Path(f"/tmp/{name}_watcher.pid")
            if pid_file.exists():
                pid = int(pid_file.read_text())
                try:
                    os.kill(pid, 0)  # Check if process exists
                    return True
                except ProcessLookupError:
                    return False
            
            # Alternative: Check if process running by name
            result = subprocess.run(
                ['pgrep', '-f', f'{name}_watcher'],
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except Exception as e:
            logger.debug(f"Could not check {name} watcher: {e}")
            return False
    
    def check_ralph_loop(self) -> Dict[str, Any]:
        """
        Check if Ralph Wiggum loop is stuck.
        
        Returns:
            Dict with status and details
        """
        try:
            # Check state file
            state_file = self.vault_path / "Plans" / "ralph_state.json"
            if not state_file.exists():
                return {
                    "status": "not_running",
                    "details": "No Ralph loop state file found"
                }
            
            state = json.loads(state_file.read_text())
            last_update = datetime.fromisoformat(state.get('last_update', '1970-01-01'))
            iterations = state.get('iterations', 0)
            max_iterations = state.get('max_iterations', 10)
            
            # Check if stuck (no update in 1 hour)
            time_since_update = (datetime.now() - last_update).total_seconds()
            
            if time_since_update > 3600:
                return {
                    "status": "stuck",
                    "details": f"No update in {time_since_update/3600:.1f} hours",
                    "iterations": iterations,
                    "max_iterations": max_iterations
                }
            
            if iterations >= max_iterations:
                return {
                    "status": "max_iterations_reached",
                    "details": f"Reached max iterations ({max_iterations})",
                    "iterations": iterations
                }
            
            return {
                "status": "healthy",
                "details": f"Running: {iterations}/{max_iterations} iterations",
                "iterations": iterations,
                "last_update": last_update.isoformat()
            }
        except Exception as e:
            logger.debug(f"Could not check Ralph loop: {e}")
            return {
                "status": "unknown",
                "details": str(e)
            }
    
    def check_odoo_connection(self) -> bool:
        """
        Check if Odoo is reachable.
        
        Returns:
            True if connection successful
        """
        try:
            odoo_url = os.getenv('ODOO_URL', 'http://localhost:8069')
            
            if not REQUESTS_AVAILABLE:
                logger.debug("requests library not available")
                return False
            
            response = requests.get(odoo_url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"Odoo connection failed: {e}")
            return False
    
    def check_twilio_credentials(self) -> bool:
        """
        Check if Twilio credentials are configured.
        
        Returns:
            True if credentials present
        """
        try:
            account_sid = os.getenv('TWILIO_ACCOUNT_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            
            return bool(account_sid and auth_token)
        except Exception as e:
            logger.debug(f"Could not check Twilio: {e}")
            return False
    
    def check_disk_space(self) -> Dict[str, Any]:
        """
        Check available disk space.
        
        Returns:
            Dict with status and details
        """
        try:
            stat = os.statvfs(self.vault_path)
            free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
            total_gb = (stat.f_blocks * stat.f_frsize) / (1024**3)
            percent_used = ((stat.f_blocks - stat.f_bfree) / stat.f_blocks) * 100
            
            if percent_used > 90:
                status = "critical"
            elif percent_used > 80:
                status = "warning"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "percent_used": round(percent_used, 1)
            }
        except Exception as e:
            return {
                "status": "unknown",
                "error": str(e)
            }
    
    def check_recent_logs(self) -> Dict[str, Any]:
        """
        Check for recent errors in logs.
        
        Returns:
            Dict with status and error count
        """
        try:
            error_count = 0
            warning_count = 0
            
            # Check logs from last 24 hours
            for log_file in self.logs_dir.glob("*.log"):
                try:
                    content = log_file.read_text()
                    lines = content.split('\n')[-100:]  # Last 100 lines
                    
                    for line in lines:
                        if 'ERROR' in line:
                            error_count += 1
                        elif 'WARNING' in line:
                            warning_count += 1
                except Exception:
                    pass
            
            if error_count > 10:
                status = "critical"
            elif error_count > 0:
                status = "warning"
            else:
                status = "healthy"
            
            return {
                "status": status,
                "errors": error_count,
                "warnings": warning_count
            }
        except Exception as e:
            return {
                "status": "unknown",
                "error": str(e)
            }
    
    def get_health(self) -> Dict[str, Any]:
        """
        Get comprehensive health status.
        
        Returns:
            Dict with overall status and component details
        """
        components = {
            "gmail_watcher": self.check_watcher_process("gmail"),
            "whatsapp_watcher": self.check_watcher_process("whatsapp"),
            "filesystem_watcher": self.check_watcher_process("filesystem"),
            "ralph_loop": self.check_ralph_loop(),
            "odoo_connection": self.check_odoo_connection(),
            "twilio_configured": self.check_twilio_credentials(),
            "disk_space": self.check_disk_space(),
            "recent_logs": self.check_recent_logs()
        }
        
        # Determine overall status
        critical_count = 0
        warning_count = 0
        
        for name, status in components.items():
            if isinstance(status, dict):
                if status.get('status') == 'critical':
                    critical_count += 1
                elif status.get('status') == 'warning':
                    warning_count += 1
            elif not status:
                warning_count += 1
        
        if critical_count > 0:
            overall_status = "critical"
        elif warning_count > 0:
            overall_status = "warning"
        else:
            overall_status = "healthy"
        
        return {
            "status": overall_status,
            "timestamp": datetime.now().isoformat(),
            "components": components,
            "critical_count": critical_count,
            "warning_count": warning_count
        }
    
    def run_health_server(self, port: int = 8080):
        """
        Run health check as HTTP server.
        
        Args:
            port: Port to listen on
        """
        from http.server import HTTPServer, BaseHTTPRequestHandler
        
        class HealthHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/health':
                    health = self.server.health_checker.get_health()
                    self.send_response(200 if health['status'] == 'healthy' else 503)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(health, indent=2).encode())
                else:
                    self.send_response(404)
                    self.end_headers()
            
            def log_message(self, format, *args):
                logger.info(f"Health check: {args[0]}")
        
        server = HTTPServer(('0.0.0.0', port), HealthHandler)
        server.health_checker = self
        
        logger.info(f"Health check server running on port {port}")
        logger.info(f"Endpoint: http://localhost:{port}/health")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            logger.info("Health check server stopped")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Health Check for AI Employee System')
    parser.add_argument('--vault-path', type=str, default=None,
                       help='Path to Obsidian vault')
    parser.add_argument('--server', action='store_true',
                       help='Run as HTTP server')
    parser.add_argument('--port', type=int, default=8080,
                       help='HTTP server port (default: 8080)')
    parser.add_argument('--json', action='store_true',
                       help='Output as JSON')
    
    args = parser.parse_args()
    
    checker = HealthChecker(vault_path=args.vault_path)
    
    if args.server:
        checker.run_health_server(port=args.port)
    else:
        health = checker.get_health()
        
        if args.json:
            print(json.dumps(health, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"AI Employee System Health Check")
            print(f"{'='*60}")
            print(f"Timestamp: {health['timestamp']}")
            print(f"Overall Status: {health['status'].upper()}")
            print(f"Critical: {health['critical_count']}, Warnings: {health['warning_count']}")
            print(f"\n{'='*60}")
            print(f"Components:")
            print(f"{'='*60}")
            
            for name, status in health['components'].items():
                if isinstance(status, bool):
                    icon = "✓" if status else "✗"
                    print(f"  {icon} {name}: {'OK' if status else 'FAIL'}")
                elif isinstance(status, dict):
                    s = status.get('status', 'unknown')
                    icon = "✓" if s == 'healthy' else ("⚠" if s == 'warning' else "✗")
                    print(f"  {icon} {name}: {s}")
                    
                    # Show details
                    if 'details' in status:
                        print(f"      {status['details']}")
                    if 'iterations' in status:
                        print(f"      Iterations: {status['iterations']}")
            
            print(f"\n{'='*60}")


if __name__ == '__main__':
    main()
