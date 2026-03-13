"""Watchers module - Monitors external systems for changes.

Silver Tier Watchers:
- GmailWatcher: Monitors Gmail for new important/unread messages
- WhatsAppWatcher: Monitors WhatsApp Web for messages with keywords
- FileSystemWatcher: Monitors drop folder for new files
"""

from .base_watcher import BaseWatcher
from .filesystem_watcher import FileSystemWatcher

# Silver Tier watchers (import directly when needed)
# from .gmail_watcher import GmailWatcher
# from .whatsapp_watcher import WhatsAppWatcher

__all__ = ['BaseWatcher', 'FileSystemWatcher']
