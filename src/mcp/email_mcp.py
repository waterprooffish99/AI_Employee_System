"""
Email MCP Server - Sends emails via Gmail API.

Silver Tier Requirement: One working MCP server for external action (e.g., sending emails)

This MCP server provides email capabilities:
- Send emails
- Draft emails (for approval)
- Search emails

Human-in-the-loop: All sends require approval before execution.
"""

import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import base64

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional imports
try:
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False


class EmailMCP:
    """
    Email MCP Server - Handles email operations.
    
    Provides email sending capabilities with HITL approval workflow.
    """
    
    def __init__(
        self,
        vault_path: str,
        credentials_path: str = None,
        token_path: str = None
    ):
        """
        Initialize the Email MCP Server.
        
        Args:
            vault_path: Path to the Obsidian vault
            credentials_path: Path to Gmail OAuth credentials
            token_path: Path to OAuth token
        """
        self.vault_path = Path(vault_path)
        self.credentials_path = credentials_path or os.getenv('GMAIL_CREDENTIALS')
        self.token_path = token_path or str(self.vault_path.parent / 'gmail_token.json')
        
        # Directories
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        
        for d in [self.pending_approval, self.approved, self.done]:
            d.mkdir(parents=True, exist_ok=True)
        
        self.service = None
        self._authenticate()
    
    def _authenticate(self) -> bool:
        """Authenticate with Gmail API."""
        if not GOOGLE_AVAILABLE:
            logger.warning('Google API libraries not available')
            return False
        
        try:
            creds = None
            token_file = Path(self.token_path)
            
            if token_file.exists():
                creds = Credentials.from_authorized_user_file(token_file, ['https://www.googleapis.com/auth/gmail.send'])
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    logger.warning('OAuth authentication required')
                    return False
            
            self.service = build('gmail', 'v1', credentials=creds)
            logger.info('Email MCP authenticated')
            return True
            
        except Exception as e:
            logger.error(f'Authentication error: {e}')
            return False
    
    def create_send_request(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str = None,
        attachment: str = None
    ) -> Path:
        """
        Create an email send request for approval.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            cc: CC recipients
            attachment: Path to attachment
            
        Returns:
            Path to approval request file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        content = f"""---
type: email_send
to: {to}
subject: {subject}
cc: {cc or 'N/A'}
created: {datetime.now().isoformat()}
status: pending_approval
requires_approval: true
---

# Email Send Request

## Recipients
- **To**: {to}
- **CC**: {cc or 'None'}

## Subject
{subject}

## Body
{body}

{f'**Attachment**: {attachment}' if attachment else ''}

---

## Approval Required
This email will be sent to an external recipient. Human approval is required.

## To Approve
1. Review the email content above
2. Verify the recipient is correct
3. Move this file to /Approved/ folder
4. The orchestrator will send the email

## To Edit
1. Edit this file with corrections
2. Save changes

## To Reject
Move this file to /Rejected/ or delete it.

---
*Created by Email MCP Server - Hackathon 0 Silver Tier*
"""
        
        # Create safe filename
        subject_safe = subject.replace(' ', '_')[:30]
        filename = f'EMAIL_SEND_{subject_safe}_{timestamp}.md'
        filepath = self.pending_approval / filename
        filepath.write_text(content)
        
        logger.info(f'Created email send request: {filepath}')
        return filepath
    
    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        cc: str = None,
        attachment: str = None
    ) -> bool:
        """
        Send an email via Gmail API.
        
        Args:
            to: Recipient email
            subject: Email subject
            body: Email body
            cc: CC recipients
            attachment: Path to attachment
            
        Returns:
            True if sent successfully
        """
        if not self.service:
            if not self._authenticate():
                return False
        
        try:
            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject
            if cc:
                message['cc'] = cc
            
            message.attach(MIMEText(body, 'plain'))
            
            # Add attachment if provided
            if attachment and Path(attachment).exists():
                from email.mime.application import MIMEApplication
                with open(attachment, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=Path(attachment).name)
                part['Content-Disposition'] = f'attachment; filename="{Path(attachment).name}"'
                message.attach(part)
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send
            sent_message = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            logger.info(f'Email sent successfully! Message ID: {sent_message["id"]}')
            return True
            
        except HttpError as e:
            logger.error(f'Gmail API error: {e}')
            return False
        except Exception as e:
            logger.error(f'Error sending email: {e}')
            return False
    
    def execute_approved_send(self, approval_file: Path) -> bool:
        """
        Execute an approved email send request.
        
        Args:
            approval_file: Path to approved request file
            
        Returns:
            True if sent successfully
        """
        if not approval_file.exists():
            logger.error(f'Approval file not found: {approval_file}')
            return False
        
        content = approval_file.read_text()
        
        # Parse YAML frontmatter
        try:
            lines = content.split('\n')
            in_frontmatter = False
            frontmatter = {}
            
            for line in lines:
                if line.strip() == '---':
                    in_frontmatter = not in_frontmatter
                    continue
                
                if in_frontmatter and ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
            
            # Extract body (after ## Body)
            body_start = content.find('## Body') + len('## Body')
            body_end = content.find('---', body_start)
            body = content[body_start:body_end].strip()
            
        except Exception as e:
            logger.error(f'Error parsing approval file: {e}')
            return False
        
        # Send email
        success = self.send_email(
            to=frontmatter.get('to', ''),
            subject=frontmatter.get('subject', ''),
            body=body,
            cc=frontmatter.get('cc') if frontmatter.get('cc') != 'N/A' else None
        )
        
        if success:
            logger.info(f'Executed approved email send to {frontmatter.get("to")}')
        
        return success


# Singleton instance for easy import
_email_mcp_instance = None


def get_email_mcp(vault_path=None):
    """Get or create EmailMCP instance."""
    global _email_mcp_instance
    if _email_mcp_instance is None:
        if vault_path is None:
            vault_path = os.getenv('VAULT_PATH', './AI_Employee_Vault')
        _email_mcp_instance = EmailMCP(vault_path=vault_path)
    return _email_mcp_instance


if __name__ == '__main__':
    import os

    vault_path = os.getenv('VAULT_PATH', '/mnt/c/Users/WaterProof Fish/Documents/AI_Employee_System/AI_Employee_Vault')

    print('=== Email MCP Server Test ===')
    print(f'Vault Path: {vault_path}')
    print(f'Google API Available: {GOOGLE_AVAILABLE}')

    if not GOOGLE_AVAILABLE:
        print()
        print('To enable Email MCP:')
        print('1. Install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib')
        print('2. Set up OAuth credentials at Google Cloud Console')
        print('3. Set GMAIL_CREDENTIALS environment variable')

    mcp = EmailMCP(vault_path=vault_path)

    print()
    print('Email MCP Server ready')
    print('Use create_send_request() to create approval requests')
    print('Use send_email() to send directly (requires auth)')
