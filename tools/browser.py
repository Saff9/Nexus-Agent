#!/usr/bin/env python3
"""Browser automation tools for Nexus Agent."""

import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BrowserTool:
    """Browser automation using Playwright."""
    
    def __init__(self):
        self.browser = None
        self.context = None
        self.page = None
        self._initialized = False
    
    def _ensure_browser(self):
        """Initialize browser if not already done."""
        if self._initialized:
            return
        
        try:
            from playwright.sync_api import sync_playwright
            
            playwright = sync_playwright().start()
            self.browser = playwright.chromium.launch(headless=True)
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            self._initialized = True
            
        except ImportError:
            logger.warning("Playwright not installed. Run: pip install playwright && playwright install")
        except Exception as e:
            logger.error(f"Browser init error: {e}")
    
    def navigate(self, url: str) -> Dict[str, Any]:
        """Navigate to URL."""
        self._ensure_browser()
        
        if not self.page:
            return {"error": "Browser not available"}
        
        try:
            response = self.page.goto(url, timeout=30000)
            return {
                "success": True,
                "url": self.page.url,
                "title": self.page.title(),
                "status": response.status if response else 0
            }
        except Exception as e:
            return {"error": str(e)}
    
    def screenshot(self, path: str = "screenshot.png") -> Dict[str, Any]:
        """Take screenshot."""
        self._ensure_browser()
        
        if not self.page:
            return {"error": "Browser not available"}
        
        try:
            self.page.screenshot(path=path, full_page=True)
            return {"success": True, "path": path}
        except Exception as e:
            return {"error": str(e)}
    
    def click(self, selector: str) -> Dict[str, Any]:
        """Click element."""
        self._ensure_browser()
        
        if not self.page:
            return {"error": "Browser not available"}
        
        try:
            self.page.click(selector, timeout=5000)
            return {"success": True, "clicked": selector}
        except Exception as e:
            return {"error": str(e)}
    
    def fill(self, selector: str, value: str) -> Dict[str, Any]:
        """Fill input field."""
        self._ensure_browser()
        
        if not self.page:
            return {"error": "Browser not available"}
        
        try:
            self.page.fill(selector, value, timeout=5000)
            return {"success": True, "filled": selector}
        except Exception as e:
            return {"error": str(e)}
    
    def content(self) -> Dict[str, Any]:
        """Get page content as text."""
        self._ensure_browser()
        
        if not self.page:
            return {"error": "Browser not available"}
        
        try:
            text = self.page.content()
            # Extract visible text
            visible_text = self.page.evaluate("document.body.innerText")
            return {
                "success": True,
                "html_length": len(text),
                "text": visible_text[:5000],  # Limit length
                "title": self.page.title()
            }
        except Exception as e:
            return {"error": str(e)}
    
    def evaluate(self, javascript: str) -> Dict[str, Any]:
        """Execute JavaScript."""
        self._ensure_browser()
        
        if not self.page:
            return {"error": "Browser not available"}
        
        try:
            result = self.page.evaluate(javascript)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}
    
    def close(self):
        """Close browser."""
        if self.browser:
            self.browser.close()
            self._initialized = False


# Tool functions for registry

_browser_instance: Optional[BrowserTool] = None

def _get_browser() -> BrowserTool:
    """Get or create browser instance."""
    global _browser_instance
    if _browser_instance is None:
        _browser_instance = BrowserTool()
    return _browser_instance

def browser_navigate(url: str) -> Dict[str, Any]:
    """Navigate to URL."""
    return _get_browser().navigate(url)

def browser_screenshot(path: str = "screenshot.png") -> Dict[str, Any]:
    """Take screenshot."""
    return _get_browser().screenshot(path)

def browser_click(selector: str) -> Dict[str, Any]:
    """Click element."""
    return _get_browser().click(selector)

def browser_fill(selector: str, value: str) -> Dict[str, Any]:
    """Fill input."""
    return _get_browser().fill(selector, value)

def browser_content() -> Dict[str, Any]:
    """Get page content."""
    return _get_browser().content()

def browser_evaluate(javascript: str) -> Dict[str, Any]:
    """Execute JS."""
    return _get_browser().evaluate(javascript)
