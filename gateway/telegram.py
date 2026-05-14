#!/usr/bin/env python3
"""Telegram Gateway for Nexus Agent."""

import asyncio
import logging
from typing import Optional, Callable, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

class TelegramGateway:
    """Telegram bot gateway for Nexus Agent."""
    
    def __init__(self, token: str, agent_factory: Callable):
        """
        Initialize Telegram gateway.
        
        Args:
            token: Telegram bot token from @BotFather
            agent_factory: Function that creates NexusAgent instances
        """
        self.token = token
        self.agent_factory = agent_factory
        self.app = None
        self.sessions: Dict[int, Any] = {}
        self.allowed_users: set = set()
        self._setup_complete = False
    
    async def start(self):
        """Start the Telegram bot."""
        try:
            from telegram import Update
            from telegram.ext import Application, MessageHandler, filters, CommandHandler
            
            self.app = Application.builder().token(self.token).build()
            
            # Add handlers
            self.app.add_handler(CommandHandler("start", self._cmd_start))
            self.app.add_handler(CommandHandler("new", self._cmd_new))
            self.app.add_handler(CommandHandler("status", self._cmd_status))
            self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
            
            logger.info("Telegram gateway starting...")
            await self.app.initialize()
            await self.app.start()
            await self.app.updater.start_polling()
            logger.info("✓ Telegram gateway running")
            self._setup_complete = True
            
        except ImportError:
            logger.error("telegram-bot not installed. Run: pip install python-telegram-bot")
            raise
        except Exception as e:
            logger.error(f"Telegram gateway error: {e}")
            raise
    
    async def stop(self):
        """Stop the Telegram bot."""
        if self.app and self._setup_complete:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()
            logger.info("Telegram gateway stopped")
    
    async def _cmd_start(self, update: Update, context):
        """Handle /start command."""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Add to allowed users
        self.allowed_users.add(user.id)
        
        # Create agent for this user
        if chat_id not in self.sessions:
            self.sessions[chat_id] = self.agent_factory()
        
        await update.message.reply_text(
            f"⚡ *Nexus Agent*\n\n"
            f"Welcome @{user.username}!\n\n"
            f"I'm your self-improving AI assistant.\n"
            f"Send me any message and I'll help you.\n\n"
            f"*Commands:*\n"
            f"/new - Start new conversation\n"
            f"/status - Show agent status",
            parse_mode='Markdown'
        )
    
    async def _cmd_new(self, update: Update, context):
        """Handle /new command - new session."""
        chat_id = update.effective_chat.id
        self.sessions[chat_id] = self.agent_factory()
        await update.message.reply_text("✓ New conversation started")
    
    async def _cmd_status(self, update: Update, context):
        """Handle /status command."""
        chat_id = update.effective_chat.id
        if chat_id in self.sessions:
            agent = self.sessions[chat_id]
            status = agent.get_status()
            await update.message.reply_text(
                f"⚡ *Status*\n\n"
                f"Provider: `{status['provider']}`\n"
                f"Model: `{status['model']}`\n"
                f"Messages: `{status['message_count']}`\n"
                f"Tools: `{status['tools_available']}`",
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text("No active session. Send /start first.")
    
    async def _handle_message(self, update: Update, context):
        """Handle incoming messages."""
        if not self._setup_complete:
            return
        
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # Check if user is allowed
        if user_id not in self.allowed_users:
            await update.message.reply_text("⚠️ You're not authorized. Use /start first.")
            return
        
        # Get or create agent for this chat
        if chat_id not in self.sessions:
            self.sessions[chat_id] = self.agent_factory()
            await update.message.reply_text("⚡ Initializing...")
        
        agent = self.sessions[chat_id]
        user_message = update.message.text
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=chat_id, action='typing')
        
        # Process message
        try:
            response = await agent.run_conversation(user_message)
            
            # Split long messages
            for chunk in self._split_message(response):
                await update.message.reply_text(chunk)
                
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text(f"⚠️ Error: {str(e)}")
    
    def _split_message(self, text: str, max_len: int = 4000) -> list:
        """Split long messages for Telegram."""
        if len(text) <= max_len:
            return [text]
        
        chunks = []
        while len(text) > max_len:
            # Split at last newline or space
            split_point = text.rfind('\n', 0, max_len)
            if split_point == -1:
                split_point = text.rfind(' ', 0, max_len)
            if split_point == -1:
                split_point = max_len
            
            chunks.append(text[:split_point])
            text = text[split_point:].lstrip()
        
        if text:
            chunks.append(text)
        
        return chunks
    
    @classmethod
    def from_config(cls, config: dict, agent_factory: Callable) -> 'TelegramGateway':
        """Create gateway from config dict."""
        token = config.get('telegram_token') or config.get('token')
        if not token:
            raise ValueError("Telegram token required")
        return cls(token, agent_factory)
