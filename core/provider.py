#!/usr/bin/env python3
"""Provider registry and abstraction for multiple LLM backends."""

import json
import os
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class Provider(ABC):
    """Abstract base class for LLM providers."""
    
    def __init__(self, config: dict):
        self.config = config
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "")
        self.model = config.get("model", "")
    
    @abstractmethod
    async def chat(self, messages: List[dict], tools: Optional[Dict[str, dict]] = None) -> dict:
        """Send chat request and return response."""
        pass
    
    def _get_headers(self) -> Dict[str, str]:
        """Get common headers for API requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers


class OpenAIProvider(Provider):
    """OpenAI-compatible API provider."""
    
    async def chat(self, messages: List[dict], tools: Optional[Dict[str, dict]] = None) -> dict:
        import httpx
        
        url = self.base_url or "https://api.openai.com/v1/chat/completions"
        
        payload = {
            "model": self.model or "gpt-4o-mini",
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 4096),
        }
        
        if tools:
            payload["tools"] = [
                {"type": "function", "function": schema}
                for schema in tools.values()
            ]
            payload["tool_choice"] = "auto"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=self._get_headers(), json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()
            
            choice = data["choices"][0]
            message = choice.get("message", {})
            
            result = {
                "content": message.get("content", ""),
                "tool_calls": []
            }
            
            if "tool_calls" in message:
                for tc in message["tool_calls"]:
                    result["tool_calls"].append({
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "arguments": json.loads(tc["function"]["arguments"])
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return {"content": f"API Error: {str(e)}", "tool_calls": []}


class AnthropicProvider(Provider):
    """Anthropic Claude API provider."""
    
    async def chat(self, messages: List[dict], tools: Optional[Dict[str, dict]] = None) -> dict:
        import httpx
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        # Convert messages to Anthropic format
        system_msg = ""
        anthropic_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_msg = msg["content"]
            else:
                anthropic_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "model": self.model or "claude-sonnet-4-20250514",
            "max_tokens": self.config.get("max_tokens", 4096),
            "system": system_msg,
            "messages": anthropic_messages,
        }
        
        if tools:
            payload["tools"] = [
                {"name": k, "description": v.get("description", ""), "input_schema": v}
                for k, v in tools.items()
            ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()
            
            content = ""
            tool_calls = []
            
            for block in data.get("content", []):
                if block["type"] == "text":
                    content += block.get("text", "")
                elif block["type"] == "tool_use":
                    tool_calls.append({
                        "id": block["id"],
                        "name": block["name"],
                        "arguments": block.get("input", {})
                    })
            
            return {"content": content, "tool_calls": tool_calls}
            
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return {"content": f"API Error: {str(e)}", "tool_calls": []}


class OllamaProvider(Provider):
    """Local Ollama provider for self-hosted models."""
    
    async def chat(self, messages: List[dict], tools: Optional[Dict[str, dict]] = None) -> dict:
        import httpx
        
        url = self.base_url or "http://localhost:11434/api/chat"
        
        payload = {
            "model": self.model or "llama3.1",
            "messages": messages,
            "stream": False,
        }
        
        if tools:
            payload["tools"] = [
                {"type": "function", "function": schema}
                for schema in tools.values()
            ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, timeout=300)
                response.raise_for_status()
                data = response.json()
            
            message = data.get("message", {})
            return {
                "content": message.get("content", ""),
                "tool_calls": []  # Ollama tool calling varies by model
            }
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            return {"content": f"API Error: {str(e)}", "tool_calls": []}


class OpenRouterProvider(Provider):
    """OpenRouter provider for 200+ models."""
    
    async def chat(self, messages: List[dict], tools: Optional[Dict[str, dict]] = None) -> dict:
        import httpx
        
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://nexus-agent.io",
            "X-Title": "Nexus Agent"
        }
        
        payload = {
            "model": self.model or "google/gemini-2.0-flash-001",
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 4096),
        }
        
        if tools:
            payload["tools"] = [
                {"type": "function", "function": schema}
                for schema in tools.values()
            ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()
            
            choice = data["choices"][0]
            message = choice.get("message", {})
            
            result = {
                "content": message.get("content", ""),
                "tool_calls": []
            }
            
            if "tool_calls" in message:
                for tc in message["tool_calls"]:
                    result["tool_calls"].append({
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "arguments": json.loads(tc["function"]["arguments"])
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"OpenRouter API error: {e}")
            return {"content": f"API Error: {str(e)}", "tool_calls": []}


class OpenClawProvider(Provider):
    """OpenClaw API provider."""
    
    async def chat(self, messages: List[dict], tools: Optional[Dict[str, dict]] = None) -> dict:
        import httpx
        
        url = self.base_url or "https://api.openclaw.ai/v1/chat/completions"
        headers = self._get_headers()
        
        payload = {
            "model": self.model or "openclaw-default",
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 4096),
        }
        
        if tools:
            payload["tools"] = [
                {"type": "function", "function": schema}
                for schema in tools.values()
            ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()
            
            choice = data["choices"][0]
            message = choice.get("message", {})
            
            result = {
                "content": message.get("content", ""),
                "tool_calls": []
            }
            
            if "tool_calls" in message:
                for tc in message["tool_calls"]:
                    result["tool_calls"].append({
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "arguments": json.loads(tc["function"]["arguments"])
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"OpenClaw API error: {e}")
            return {"content": f"API Error: {str(e)}", "tool_calls": []}


class HarmesProvider(Provider):
    """Harmes Agent Architecture API provider."""
    
    async def chat(self, messages: List[dict], tools: Optional[Dict[str, dict]] = None) -> dict:
        import httpx
        
        url = self.base_url or "https://api.harmes.ai/v1/chat/completions"
        headers = self._get_headers()
        
        payload = {
            "model": self.model or "harmes-advanced",
            "messages": messages,
            "temperature": self.config.get("temperature", 0.7),
            "max_tokens": self.config.get("max_tokens", 4096),
        }
        
        if tools:
            payload["tools"] = [
                {"type": "function", "function": schema}
                for schema in tools.values()
            ]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, headers=headers, json=payload, timeout=120)
                response.raise_for_status()
                data = response.json()
            
            choice = data["choices"][0]
            message = choice.get("message", {})
            
            result = {
                "content": message.get("content", ""),
                "tool_calls": []
            }
            
            if "tool_calls" in message:
                for tc in message["tool_calls"]:
                    result["tool_calls"].append({
                        "id": tc["id"],
                        "name": tc["function"]["name"],
                        "arguments": json.loads(tc["function"]["arguments"])
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Harmes API error: {e}")
            return {"content": f"API Error: {str(e)}", "tool_calls": []}


class ProviderRegistry:
    """Registry for managing multiple LLM providers."""
    
    PROVIDERS = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "ollama": OllamaProvider,
        "openrouter": OpenRouterProvider,
        "openclaw": OpenClawProvider,
        "harmes": HarmesProvider,
    }
    
    def __init__(self, config):
        self.config = config
        self._providers: Dict[str, Provider] = {}
        self._load_env_keys()
    
    def _load_env_keys(self):
        """Load API keys from environment."""
        self.env_keys = {
            "openai": os.environ.get("OPENAI_API_KEY", ""),
            "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
            "openrouter": os.environ.get("OPENROUTER_API_KEY", ""),
            "openclaw": os.environ.get("OPENCLAW_API_KEY", ""),
            "harmes": os.environ.get("HARMES_API_KEY", ""),
        }
    
    def get_provider(self, provider_name: str) -> Provider:
        """Get or create a provider instance."""
        if provider_name in self._providers:
            return self._providers[provider_name]
        
        provider_class = self.PROVIDERS.get(provider_name)
        if not provider_class:
            # Default to OpenAI-compatible for unknown providers
            provider_class = OpenAIProvider
        
        provider_config = {
            "api_key": self.env_keys.get(provider_name, ""),
            "model": self.config.model,
            "temperature": self.config.get("temperature"),
            "max_tokens": self.config.get("max_tokens"),
        }
        
        # Handle provider-specific base URLs
        if provider_name == "ollama":
            provider_config["base_url"] = "http://localhost:11434/api"
        elif provider_name == "openrouter":
            provider_config["base_url"] = "https://openrouter.ai/api/v1"
        
        provider = provider_class(provider_config)
        self._providers[provider_name] = provider
        return provider
    
    def list_providers(self) -> List[str]:
        """List available providers."""
        return list(self.PROVIDERS.keys())
    
    def list_models(self, provider_name: str) -> List[str]:
        """List available models for a provider."""
        # Static model lists - could be fetched dynamically
        models = {
            "openai": ["gpt-4o", "gpt-4o-mini", "o1-preview", "o1-mini"],
            "anthropic": ["claude-sonnet-4-20250514", "claude-opus-4-20250514", "claude-3-5-sonnet-20241022"],
            "ollama": ["llama3.1", "mistral", "gemma2", "qwen2.5"],
            "openrouter": ["google/gemini-2.0-flash-001", "meta-llama/llama-3.1-405b-instruct", "anthropic/claude-3.5-sonnet"],
            "openclaw": ["openclaw-default", "openclaw-pro", "openclaw-fast"],
            "harmes": ["harmes-base", "harmes-advanced", "harmes-fast"],
        }
        return models.get(provider_name, [])
