"""
Odoo MCP Server for AI Employee System - Gold Tier

Integrates with Odoo Community 19+ via JSON-RPC API for accounting operations.
"""

import json
import logging
import os
import requests
from typing import Any, Optional
from pathlib import Path

from src.utils.audit_logger import get_audit_logger
from src.utils.error_handler import ErrorHandler, with_error_handling
from src.utils.retry_manager import retryable


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class OdooClient:
    """
    Odoo JSON-RPC client for Community 19+.
    
    Features:
    - JSON-RPC 2.0 communication
    - Session management
    - Authentication handling
    - Error handling with retry
    """
    
    def __init__(
        self,
        url: Optional[str] = None,
        db: Optional[str] = None,
        username: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Odoo client.
        
        Args:
            url: Odoo server URL
            db: Database name
            username: Username
            api_key: API key
        """
        self.url = url or os.getenv("ODOO_URL", "http://localhost:8069")
        self.db = db or os.getenv("ODOO_DB", "odoo_db")
        self.username = username or os.getenv("ODOO_USERNAME", "admin")
        self.api_key = api_key or os.getenv("ODOO_API_KEY", "")
        
        self.uid = None
        self.error_handler = ErrorHandler()
        
        # Authenticate
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Odoo."""
        endpoint = f"{self.url}/jsonrpc"
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "common",
                "method": "authenticate",
                "args": [self.db, self.username, self.api_key, {}]
            },
            "id": 1
        }
        
        try:
            response = requests.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result:
                self.uid = result["result"]
                logger.info(f"Authenticated with Odoo as user {self.uid}")
            else:
                raise Exception(f"Authentication failed: {result}")
        except Exception as e:
            logger.error(f"Odoo authentication failed: {e}")
            audit_logger.log_error(
                action_type="odoo_authenticate",
                actor="odoo_mcp",
                error=str(e),
                target=self.url,
            )
            raise
    
    def _jsonrpc_call(
        self,
        model: str,
        method: str,
        args: list | None = None,
        kwargs: dict | None = None,
    ) -> Any:
        """
        Make a JSON-RPC call to Odoo.
        
        Args:
            model: Odoo model name
            method: Method to call
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Method result
        """
        endpoint = f"{self.url}/jsonrpc"
        
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "service": "object",
                "method": "execute_kwargs",
                "args": [self.db, self.uid, self.api_key, model, method]
            },
            "id": 2
        }
        
        if args:
            payload["params"]["args"].append(args)
        else:
            payload["params"]["args"].append([])
        
        if kwargs:
            payload["params"]["kwargs"] = kwargs
        else:
            payload["params"]["kwargs"] = {}
        
        try:
            response = requests.post(endpoint, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if "result" in result:
                return result["result"]
            else:
                raise Exception(f"Odoo error: {result}")
        except Exception as e:
            logger.error(f"Odoo JSON-RPC call failed: {e}")
            raise

    @retryable(max_retries=3)
    def search_read(
        self,
        model: str,
        domain: list | None = None,
        fields: list | None = None,
        limit: int = 80,
    ) -> list[dict]:
        """
        Search and read records from Odoo.
        
        Args:
            model: Model name
            domain: Search domain
            fields: Fields to return
            limit: Maximum records
            
        Returns:
            List of records
        """
        return self._jsonrpc_call(
            model=model,
            method="search_read",
            args=[domain or [], fields or []],
            kwargs={"limit": limit},
        )

    @retryable(max_retries=3)
    def create(self, model: str, values: dict) -> int:
        """
        Create a record in Odoo.
        
        Args:
            model: Model name
            values: Field values
            
        Returns:
            Record ID
        """
        return self._jsonrpc_call(
            model=model,
            method="create",
            args=[values],
        )

    @retryable(max_retries=3)
    def write(self, model: str, ids: list, values: dict) -> bool:
        """
        Update records in Odoo.
        
        Args:
            model: Model name
            ids: Record IDs
            values: Field values
            
        Returns:
            True if successful
        """
        return self._jsonrpc_call(
            model=model,
            method="write",
            args=[ids, values],
        )

    @retryable(max_retries=3)
    def unlink(self, model: str, ids: list) -> bool:
        """
        Delete records from Odoo.
        
        Args:
            model: Model name
            ids: Record IDs
            
        Returns:
            True if successful
        """
        return self._jsonrpc_call(
            model=model,
            method="unlink",
            args=[ids],
        )


class OdooMCP:
    """
    Odoo MCP server for accounting operations.
    
    Features:
    - Invoice management
    - Payment tracking
    - Financial reporting
    - Customer/Vendor management
    """
    
    def __init__(self, client: Optional[OdooClient] = None):
        """
        Initialize Odoo MCP.
        
        Args:
            client: OdooClient instance (creates new if None)
        """
        self.client = client or OdooClient()
        self.audit_logger = get_audit_logger()
    
    # Invoice Management
    
    def create_invoice(
        self,
        partner_id: int,
        invoice_lines: list[dict],
        invoice_type: str = "out_invoice",
        payment_term: str | None = None,
    ) -> dict:
        """
        Create an invoice in Odoo.
        
        Args:
            partner_id: Customer/partner ID
            invoice_lines: List of line items
            invoice_type: Type (out_invoice, in_invoice, etc.)
            payment_term: Payment term reference
            
        Returns:
            Invoice details
        """
        try:
            # Create invoice
            invoice_vals = {
                "move_type": invoice_type,
                "partner_id": partner_id,
                "invoice_line_ids": [
                    (0, 0, line) for line in invoice_lines
                ],
            }
            
            if payment_term:
                invoice_vals["invoice_payment_term_id"] = payment_term
            
            invoice_id = self.client.create("account.move", invoice_vals)
            
            # Get invoice details
            invoice = self.client.search_read(
                model="account.move",
                domain=[["id", "=", invoice_id]],
                fields=["name", "partner_id", "amount_total", "amount_due", "state"],
                limit=1,
            )
            
            self.audit_logger.log_action(
                action_type="odoo_create_invoice",
                actor="odoo_mcp",
                details={
                    "invoice_id": invoice_id,
                    "partner_id": partner_id,
                    "total": invoice[0]["amount_total"] if invoice else 0,
                },
            )
            
            return {
                "success": True,
                "invoice_id": invoice_id,
                "invoice": invoice[0] if invoice else None,
            }
        except Exception as e:
            self.audit_logger.log_error(
                action_type="odoo_create_invoice",
                actor="odoo_mcp",
                error=str(e),
                target=f"partner_{partner_id}",
            )
            return {"success": False, "error": str(e)}
    
    def send_invoice(self, invoice_id: int) -> dict:
        """
        Send invoice to customer.
        
        Args:
            invoice_id: Invoice ID
            
        Returns:
            Send result
        """
        try:
            # Use Odoo's invoice sending method
            result = self.client._jsonrpc_call(
                model="account.move",
                method="action_invoice_send",
                args=[[invoice_id]],
            )
            
            self.audit_logger.log_action(
                action_type="odoo_send_invoice",
                actor="odoo_mcp",
                details={"invoice_id": invoice_id},
            )
            
            return {"success": True, "result": result}
        except Exception as e:
            self.audit_logger.log_error(
                action_type="odoo_send_invoice",
                actor="odoo_mcp",
                error=str(e),
                target=f"invoice_{invoice_id}",
            )
            return {"success": False, "error": str(e)}
    
    def get_invoices(
        self,
        partner_id: int | None = None,
        state: str | None = None,
        limit: int = 50,
    ) -> list[dict]:
        """
        Get invoices from Odoo.
        
        Args:
            partner_id: Filter by partner
            state: Filter by state (draft, posted, paid, etc.)
            limit: Maximum records
            
        Returns:
            List of invoices
        """
        domain = []
        
        if partner_id:
            domain.append(["partner_id", "=", partner_id])
        
        if state:
            domain.append(["state", "=", state])
        
        invoices = self.client.search_read(
            model="account.move",
            domain=domain,
            fields=[
                "name", "partner_id", "invoice_date", "invoice_date_due",
                "amount_total", "amount_due", "state", "payment_state"
            ],
            limit=limit,
        )
        
        return invoices
    
    def get_outstanding_invoices(self, partner_id: int | None = None) -> list[dict]:
        """
        Get outstanding (unpaid) invoices.
        
        Args:
            partner_id: Filter by partner
            
        Returns:
            List of outstanding invoices
        """
        return self.get_invoices(
            partner_id=partner_id,
            state="posted",
            limit=100,
        )
    
    # Payment Tracking
    
    def register_payment(
        self,
        invoice_id: int,
        amount: float,
        payment_date: str | None = None,
        payment_method: str | None = None,
    ) -> dict:
        """
        Register a payment for an invoice.
        
        Args:
            invoice_id: Invoice ID
            amount: Payment amount
            payment_date: Payment date
            payment_method: Payment method
            
        Returns:
            Payment result
        """
        try:
            payment_vals = {
                "amount": amount,
                "payment_date": payment_date or None,
                "payment_method_id": payment_method,
            }
            
            # Create payment registration
            payment_id = self.client.create("account.payment.registration", payment_vals)
            
            self.audit_logger.log_action(
                action_type="odoo_register_payment",
                actor="odoo_mcp",
                details={
                    "invoice_id": invoice_id,
                    "amount": amount,
                    "payment_id": payment_id,
                },
            )
            
            return {"success": True, "payment_id": payment_id}
        except Exception as e:
            self.audit_logger.log_error(
                action_type="odoo_register_payment",
                actor="odoo_mcp",
                error=str(e),
                target=f"invoice_{invoice_id}",
            )
            return {"success": False, "error": str(e)}
    
    # Financial Reporting
    
    def get_profit_loss(
        self,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> dict:
        """
        Get Profit & Loss report.
        
        Args:
            date_from: Start date
            date_to: End date
            
        Returns:
            P&L data
        """
        # This would typically use Odoo's accounting reports
        # Simplified version for now
        return {
            "success": True,
            "report": "profit_loss",
            "period": f"{date_from} to {date_to}",
            "data": {},  # Would be populated from Odoo
        }
    
    def get_balance_sheet(
        self,
        date: str | None = None,
    ) -> dict:
        """
        Get Balance Sheet.
        
        Args:
            date: Report date
            
        Returns:
            Balance sheet data
        """
        return {
            "success": True,
            "report": "balance_sheet",
            "date": date,
            "data": {},
        }
    
    # Customer/Vendor Management
    
    def create_partner(
        self,
        name: str,
        partner_type: str = "customer",
        email: str | None = None,
        phone: str | None = None,
    ) -> dict:
        """
        Create a customer or vendor.
        
        Args:
            name: Partner name
            partner_type: customer or supplier
            email: Email address
            phone: Phone number
            
        Returns:
            Partner details
        """
        try:
            partner_vals = {
                "name": name,
                "supplier": partner_type == "supplier",
                "customer": partner_type == "customer",
            }
            
            if email:
                partner_vals["email"] = email
            if phone:
                partner_vals["phone"] = phone
            
            partner_id = self.client.create("res.partner", partner_vals)
            
            self.audit_logger.log_action(
                action_type="odoo_create_partner",
                actor="odoo_mcp",
                details={
                    "partner_id": partner_id,
                    "name": name,
                    "type": partner_type,
                },
            )
            
            return {
                "success": True,
                "partner_id": partner_id,
            }
        except Exception as e:
            self.audit_logger.log_error(
                action_type="odoo_create_partner",
                actor="odoo_mcp",
                error=str(e),
                target=name,
            )
            return {"success": False, "error": str(e)}
    
    def get_partners(
        self,
        partner_type: str | None = None,
        search: str | None = None,
    ) -> list[dict]:
        """
        Get customers/vendors.
        
        Args:
            partner_type: Filter by type
            search: Search term
            
        Returns:
            List of partners
        """
        domain = []
        
        if partner_type == "customer":
            domain.append(["customer", "=", True])
        elif partner_type == "supplier":
            domain.append(["supplier", "=", True])
        
        if search:
            domain.append(["name", "ilike", search])
        
        return self.client.search_read(
            model="res.partner",
            domain=domain,
            fields=["name", "email", "phone", "customer", "supplier"],
            limit=100,
        )


# Singleton instance
_odoo_mcp: Optional[OdooMCP] = None


def get_odoo_mcp() -> OdooMCP:
    """Get or create Odoo MCP instance."""
    global _odoo_mcp
    if _odoo_mcp is None:
        try:
            _odoo_mcp = OdooMCP()
        except Exception as e:
            logger.error(f"Failed to initialize Odoo MCP: {e}")
            raise
    return _odoo_mcp
