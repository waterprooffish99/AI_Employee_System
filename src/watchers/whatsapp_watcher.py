"""
WhatsApp Watcher - Monitors WhatsApp Web for new messages with keywords.

Following the Hackathon-0 specification for the WhatsApp Watcher implementation.
Uses Playwright for browser automation to monitor WhatsApp Web.
Creates action files in Needs_Action/ folder for Claude Code to process.

Silver Tier Requirement: Two or more Watcher scripts

Note: Be aware of WhatsApp's terms of service when using automation.
"""

import time
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

from .base_watcher import BaseWatcher

# Optional imports - will fail gracefully if not installed
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WhatsAppWatcher(BaseWatcher):
    """
    WhatsApp Watcher - Monitors WhatsApp Web for new messages.
    
    Uses Playwright to automate WhatsApp Web and detect messages
    containing specific keywords. Creates .md action files in Needs_Action/ folder.
    """
    
    # Default keywords to monitor for
    DEFAULT_KEYWORDS = ['urgent', 'asap', 'invoice', 'payment', 'help', 'pricing', 'order']
    
    def __init__(
        self,
        vault_path: str,
        session_path: str = None,
        check_interval: int = 60,
        keywords: List[str] = None,
        headless: bool = True
    ):
        """
        Initialize the WhatsApp Watcher.
        
        Args:
            vault_path: Path to the Obsidian vault
            session_path: Path to store browser session data
            check_interval: Seconds between checks
            keywords: List of keywords to monitor for
            headless: Run browser in headless mode
        """
        super().__init__(vault_path, check_interval)
        
        self.session_path = Path(session_path) if session_path else self.vault_path.parent / '.whatsapp_session'
        self.keywords = keywords or self.DEFAULT_KEYWORDS
        self.headless = headless
        self.processed_messages = set()
        
        # Ensure session path exists
        self.session_path.mkdir(parents=True, exist_ok=True)
        
        logger.info(f'WhatsApp Watcher initialized')
        logger.info(f'  Keywords: {self.keywords}')
        logger.info(f'  Session: {self.session_path}')
    
    def check_for_updates(self) -> List[Dict[str, Any]]:
        """
        Check WhatsApp Web for new messages with keywords.
        
        Returns:
            List of new messages to process
        """
        if not PLAYWRIGHT_AVAILABLE:
            logger.error('Playwright not installed. Run: playwright install')
            return []
        
        messages = []
        
        try:
            with sync_playwright() as p:
                # Launch browser with persistent context
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=self.headless,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--no-sandbox'
                    ]
                )
                
                page = browser.pages[0] if browser.pages else browser.new_page()
                
                # Navigate to WhatsApp Web
                logger.debug('Navigating to WhatsApp Web...')
                page.goto('https://web.whatsapp.com', timeout=60000)
                
                # Wait for chat list to load
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                    logger.debug('Chat list loaded')
                except PlaywrightTimeout:
                    logger.warning('WhatsApp Web not loaded. May need QR code scan.')
                    browser.close()
                    return []
                
                # Give it a moment to fully load
                time.sleep(2)
                
                # Find unread messages
                # Note: WhatsApp Web selectors may change, this is based on current structure
                unread_chats = page.query_selector_all('[aria-label*="unread"]')
                
                logger.debug(f'Found {len(unread_chats)} unread chats')
                
                for chat in unread_chats:
                    try:
                        # Extract chat info
                        chat_text = chat.inner_text()
                        
                        # Check for keywords
                        chat_text_lower = chat_text.lower()
                        matched_keywords = [kw for kw in self.keywords if kw in chat_text_lower]
                        
                        if matched_keywords:
                            # Extract chat name/number
                            name_element = chat.query_selector('[dir="auto"]')
                            chat_name = name_element.inner_text() if name_element else 'Unknown'
                            
                            messages.append({
                                'text': chat_text,
                                'chat_name': chat_name,
                                'keywords': matched_keywords,
                                'timestamp': datetime.now().isoformat()
                            })
                            
                            logger.info(f'Matched message from {chat_name}: {matched_keywords}')
                    
                    except Exception as e:
                        logger.debug(f'Error processing chat: {e}')
                        continue
                
                browser.close()
                
        except Exception as e:
            logger.error(f'Error checking WhatsApp: {e}')
        
        # Filter out already processed
        new_messages = []
        for msg in messages:
            msg_id = hash(f"{msg['chat_name']}:{msg['text'][:50]}")
            if msg_id not in self.processed_messages:
                new_messages.append(msg)
                self.processed_messages.add(msg_id)
        
        return new_messages
    
    def create_action_file(self, message: Dict[str, Any]) -> Path:
        """
        Create an action file in Needs_Action folder for a WhatsApp message.
        
        Args:
            message: WhatsApp message dict
            
        Returns:
            Path to created action file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create safe filename
        chat_name_safe = message['chat_name'].replace('/', '_').replace('\\', '_')[:30]
        
        content = f"""---
type: whatsapp
chat_name: {message['chat_name']}
received: {message['timestamp']}
keywords: {', '.join(message['keywords'])}
priority: high
status: pending
---

# WhatsApp Message: {message['chat_name']}

**Received**: {message['timestamp']}  
**Keywords**: {', '.join(message['keywords'])}  
**Priority**: High

## Message Content
{message['text']}

## Why This Was Flagged
This message was flagged because it contains one or more of these keywords:
{', '.join([f'- `{kw}`' for kw in message['keywords']])}

## Suggested Actions
- [ ] Read full message
- [ ] Reply to sender
- [ ] Take required action
- [ ] Mark as complete

## Response Draft
*Draft your response here*

---
*Created by WhatsApp Watcher - Hackathon 0 Silver Tier*
"""
        
        # Write action file
        filepath = self.needs_action / f'WHATSAPP_{chat_name_safe}_{timestamp}.md'
        filepath.write_text(content)
        
        logger.info(f'Created action file: {filepath}')
        return filepath
    
    def run_once(self) -> int:
        """
        Run a single check cycle.
        
        Returns:
            Number of new messages processed
        """
        items = self.check_for_updates()
        count = 0
        
        for item in items:
            try:
                self.create_action_file(item)
                count += 1
            except Exception as e:
                logger.error(f'Error processing message: {e}')
        
        return count
    
    def run(self):
        """
        Main loop for the WhatsApp Watcher.
        
        Continuously checks WhatsApp Web for new messages.
        """
        logger.info(f'Starting WhatsAppWatcher (check interval: {self.check_interval}s)')
        logger.info(f'Monitoring keywords: {self.keywords}')
        
        if not PLAYWRIGHT_AVAILABLE:
            logger.error('Playwright not installed. Install with: playwright install')
            logger.info('Falling back to polling mode (no WhatsApp monitoring)')
            while True:
                time.sleep(self.check_interval)
            return
        
        while True:
            try:
                count = self.run_once()
                if count > 0:
                    logger.info(f'Processed {count} new messages')
            except Exception as e:
                logger.error(f'Error in watcher loop: {e}')
            
            time.sleep(self.check_interval)


if __name__ == '__main__':
    import os
    import sys
    
    # Get vault path from environment or use default
    vault_path = os.getenv('VAULT_PATH', '/mnt/c/Users/WaterProof Fish/Documents/AI_Employee_System/AI_Employee_Vault')
    
    print('=== WhatsApp Watcher Test ===')
    print(f'Vault Path: {vault_path}')
    print(f'Playwright Available: {PLAYWRIGHT_AVAILABLE}')
    
    if not PLAYWRIGHT_AVAILABLE:
        print()
        print('To configure WhatsApp Watcher:')
        print('1. Install Playwright: pip install playwright')
        print('2. Install browsers: playwright install chromium')
        print('3. Run: python -m src.watchers.whatsapp_watcher')
        print()
        print('Note: First run will require QR code scan to authenticate WhatsApp Web')
        sys.exit(0)
    
    watcher = WhatsAppWatcher(
        vault_path=vault_path,
        check_interval=30,  # Short interval for testing
        headless=False  # Show browser for first-time QR scan
    )
    
    print()
    print('Running single check...')
    count = watcher.run_once()
    print(f'Found {count} new messages')
    
    if count == 0:
        print('No new messages. Start watcher with: python -m src.watchers.whatsapp_watcher')
