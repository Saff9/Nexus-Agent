#!/usr/bin/env python3
"""Discord Gateway for Nexus Agent."""

import asyncio
import logging
from typing import Optional, Callable, Dict, Any

logger = logging.getLogger(__name__)

class DiscordGateway:
    """Discord bot gateway for Nexus Agent."""
    
    def __init__(self, token: str, agent_factory: Callable):
        self.token = token
        self.agent_factory = agent_factory
        self.client = None
        self.sessions: Dict[int, Any] = {}
        self.allowed_channels: set = set()
    
    async def start(self):
        """Start the Discord bot."""
        try:
            import discord
            from discord.ext import commands
            
            intents = discord.Intents.default()
            intents.message_content = True
            intents.messages = True
            
            self.client = commands.Bot(command_prefix='!', intents=intents)
            
            @self.client.event
            async def on_ready():
                logger.info(f"✓ Discord gateway logged in as {self.client.user}")
            
            @self.client.event
            async def on_message(message):
                if message.author == self.client.user:
                    return
                
                # Only respond in allowed channels or DMs
                if isinstance(message.channel, discord.DMChannel) or \
                   message.channel.id in self.allowed_channels:
                    await self._handle_message(message)
                
                await self.client.process_commands(message)
            
            @self.client.command(name='new')
            async def new_command(ctx):
                """Start new conversation."""
                self.sessions[ctx.channel.id] = self.agent_factory()
                await ctx.send("✓ New conversation started")
            
            @self.client.command(name='status')
            async def status_command(ctx):
                """Show agent status."""
                if ctx.channel.id in self.sessions:
                    agent = self.sessions[ctx.channel.id]
                    status = agent.get_status()
                    embed = discord.Embed(
                        title="⚡ Nexus Agent Status",
                        color=discord.Color.blue()
                    )
                    embed.add_field(name="Provider", value=status['provider'])
                    embed.add_field(name="Model", value=status['model'])
                    embed.add_field(name="Messages", value=status['message_count'])
                    embed.add_field(name="Tools", value=status['tools_available'])
                    await ctx.send(embed=embed)
            
            await self.client.start(self.token)
            
        except ImportError:
            logger.error("discord.py not installed. Run: pip install discord.py")
            raise
        except Exception as e:
            logger.error(f"Discord gateway error: {e}")
            raise
    
    async def stop(self):
        """Stop the Discord bot."""
        if self.client:
            await self.client.close()
            logger.info("Discord gateway stopped")
    
    async def _handle_message(self, message):
        """Handle incoming message."""
        channel_id = message.channel.id
        
        # Get or create agent
        if channel_id not in self.sessions:
            self.sessions[channel_id] = self.agent_factory()
        
        agent = self.sessions[channel_id]
        
        # Send typing indicator
        async with message.channel.typing():
            # Process directly since agent is async
            response = await agent.run_conversation(message.content)
            
            # Split and send
            for chunk in self._split_message(response):
                await message.channel.send(chunk)
    
    def _split_message(self, text: str, max_len: int = 2000) -> list:
        """Split long messages for Discord."""
        if len(text) <= max_len:
            return [text]
        
        chunks = []
        while len(text) > max_len:
            split_point = text.rfind('\n', 0, max_len)
            if split_point == -1:
                split_point = max_len
            chunks.append(text[:split_point])
            text = text[split_point:].lstrip()
        
        if text:
            chunks.append(text)
        
        return chunks
    
    def allow_channel(self, channel_id: int):
        """Allow a channel for bot responses."""
        self.allowed_channels.add(channel_id)
    
    @classmethod
    def from_config(cls, config: dict, agent_factory: Callable) -> 'DiscordGateway':
        """Create gateway from config."""
        token = config.get('discord_token') or config.get('token')
        if not token:
            raise ValueError("Discord token required")
        return cls(token, agent_factory)
