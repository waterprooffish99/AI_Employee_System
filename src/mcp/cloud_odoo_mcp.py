"""
Cloud Odoo MCP - Draft-Only Odoo Operations

Cloud agent can only create Odoo action drafts.
Local agent handles actual posting after approval.
"""

import logging
from pathlib import Path
from typing import Any, Optional

from src.utils.audit_logger import get_audit_logger


logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


class CloudOdooMCP:
    """
    Cloud Odoo MCP - Draft-only Odoo operations.
    
    This MCP server can ONLY create drafts.
    It cannot post invoices or payments directly.
    """
    
    def __init__(self, vault_path: Optional[str | Path] = None):
        """
        Initialize cloud Odoo MCP.
        
        Args:
            vault_path: Path to Obsidian vault
        """
        self.vault_path = Path(vault_path) if vault_path else Path.cwd() / "AI_Employee_Vault"
        self.updates_dir = self.vault_path / "Updates" / "odoo_drafts"
        self.updates_dir.mkdir(parents=True, exist_ok=True)
        self.audit_logger = get_audit_logger()
        
        logger.info("Cloud Odoo MCP initialized (draft-only mode)")
    
    def create_invoice_draft(
        self,
        partner_name: str,
        partner_email: str,
        lines: list[dict],
        payment_terms: str = "Net 30",
    ) -> Path:
        """
        Create invoice draft for local approval.
        
        Args:
            partner_name: Customer name
            partner_email: Customer email
            lines: Line items [{name, quantity, price}]
            payment_terms: Payment terms
            
        Returns:
            Path to draft file
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.updates_dir / f"invoice_draft_{timestamp}.md"
        
        # Calculate total
        total = sum(line.get('quantity', 1) * line.get('price', 0) for line in lines)
        
        lines_md = "\n".join([
            f"- {line.get('name', 'Item')}: {line.get('quantity', 1)} x ${line.get('price', 0):.2f} = ${line.get('quantity', 1) * line.get('price', 0):.2f}"
            for line in lines
        ])
        
        content = f"""---
type: odoo_invoice_draft
created: {datetime.now().isoformat()}
partner_name: {partner_name}
partner_email: {partner_email}
total: {total:.2f}
payment_terms: {payment_terms}
status: pending_approval
draft_mode: true
---

# Invoice Draft

**Customer**: {partner_name}
**Email**: {partner_email}
**Payment Terms**: {payment_terms}
**Total**: ${total:.2f}
**Created**: {datetime.now().isoformat()}

---

## Line Items

{lines_md}

---

## To Post

1. Review the invoice details above
2. Move this file to `/Pending_Approval/local/`
3. Local agent will create and send the invoice via Odoo MCP after approval

---

**Cloud Draft** - Requires Local Approval

This invoice draft was created by the Cloud Agent in draft-only mode.
Cloud cannot post invoices directly - local approval required.
"""
        
        draft_file.write_text(content)
        
        self.audit_logger.log_action(
            action_type="cloud_odoo_invoice_draft_created",
            actor="cloud_odoo_mcp",
            details={
                "draft_file": str(draft_file),
                "partner_name": partner_name,
                "total": total,
                "line_count": len(lines),
            },
        )
        
        logger.info(f"Created Odoo invoice draft: {draft_file}")
        return draft_file
    
    def create_payment_draft(
        self,
        vendor_name: str,
        amount: float,
        invoice_reference: str,
        payment_method: str = "Bank Transfer",
    ) -> Path:
        """
        Create payment draft for local approval.
        
        Args:
            vendor_name: Vendor name
            amount: Payment amount
            invoice_reference: Invoice reference
            payment_method: Payment method
            
        Returns:
            Path to draft file
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.updates_dir / f"payment_draft_{timestamp}.md"
        
        content = f"""---
type: odoo_payment_draft
created: {datetime.now().isoformat()}
vendor_name: {vendor_name}
amount: {amount:.2f}
invoice_reference: {invoice_reference}
payment_method: {payment_method}
status: pending_approval
draft_mode: true
---

# Payment Draft

**Vendor**: {vendor_name}
**Amount**: ${amount:.2f}
**Invoice Reference**: {invoice_reference}
**Payment Method**: {payment_method}
**Created**: {datetime.now().isoformat()}

---

## Payment Details

- Pay to: {vendor_name}
- Amount: ${amount:.2f}
- Reference: {invoice_reference}
- Method: {payment_method}

---

## To Execute

1. Review the payment details above
2. Move this file to `/Pending_Approval/local/`
3. Local agent will register the payment via Odoo MCP after approval

---

**Cloud Draft** - Requires Local Approval

This payment draft was created by the Cloud Agent in draft-only mode.
Cloud cannot execute payments directly - local approval required.
"""
        
        draft_file.write_text(content)
        
        self.audit_logger.log_action(
            action_type="cloud_odoo_payment_draft_created",
            actor="cloud_odoo_mcp",
            details={
                "draft_file": str(draft_file),
                "vendor_name": vendor_name,
                "amount": amount,
                "payment_method": payment_method,
            },
        )
        
        logger.info(f"Created Odoo payment draft: {draft_file}")
        return draft_file
    
    def create_journal_entry_draft(
        self,
        name: str,
        lines: list[dict],
        description: str = "",
    ) -> Path:
        """
        Create journal entry draft for local approval.
        
        Args:
            name: Entry name
            lines: Journal lines [{account, debit, credit}]
            description: Entry description
            
        Returns:
            Path to draft file
        """
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        draft_file = self.updates_dir / f"journal_draft_{timestamp}.md"
        
        lines_md = "\n".join([
            f"- {line.get('account', 'Account')}: Debit ${line.get('debit', 0):.2f} | Credit ${line.get('credit', 0):.2f}"
            for line in lines
        ])
        
        content = f"""---
type: odoo_journal_draft
created: {datetime.now().isoformat()}
name: {name}
status: pending_approval
draft_mode: true
---

# Journal Entry Draft

**Name**: {name}
**Created**: {datetime.now().isoformat()}

---

## Journal Lines

{lines_md}

## Description

{description}

---

## To Post

1. Review the journal entry above
2. Move this file to `/Pending_Approval/local/`
3. Local agent will post the entry via Odoo MCP after approval

---

**Cloud Draft** - Requires Local Approval

This journal entry draft was created by the Cloud Agent in draft-only mode.
Cloud cannot post entries directly - local approval required.
"""
        
        draft_file.write_text(content)
        
        self.audit_logger.log_action(
            action_type="cloud_odoo_journal_draft_created",
            actor="cloud_odoo_mcp",
            details={
                "draft_file": str(draft_file),
                "name": name,
                "line_count": len(lines),
            },
        )
        
        logger.info(f"Created Odoo journal entry draft: {draft_file}")
        return draft_file
    
    def post_invoice(self, *args, **kwargs) -> dict:
        """Post invoice - DISABLED in cloud mode."""
        return {
            "success": False,
            "error": "post_invoice() is disabled in cloud mode. Use create_invoice_draft() instead.",
            "mode": "draft_only",
        }
    
    def register_payment(self, *args, **kwargs) -> dict:
        """Register payment - DISABLED in cloud mode."""
        return {
            "success": False,
            "error": "register_payment() is disabled in cloud mode. Use create_payment_draft() instead.",
            "mode": "draft_only",
        }


# Singleton instance
_cloud_odoo_mcp: Optional[CloudOdooMCP] = None


def get_cloud_odoo_mcp(vault_path: Optional[str | Path] = None) -> CloudOdooMCP:
    """Get or create cloud Odoo MCP instance."""
    global _cloud_odoo_mcp
    if _cloud_odoo_mcp is None:
        _cloud_odoo_mcp = CloudOdooMCP(vault_path)
    return _cloud_odoo_mcp
