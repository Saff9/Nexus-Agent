#!/usr/bin/env python3
"""Nexus Agent - Premium Kivy Mobile App for Android."""

import sys
import threading
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.graphics import Color, RoundedRectangle, Rectangle
from kivy.core.window import Window

from core import NexusAgent, Config

# No module-level Window calls to prevent Android startup crashes

class ChatMessage(BoxLayout):
    """Premium modern chat message with dynamic bubble sizing."""
    def __init__(self, text, is_user=True, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = [15, 10]
        self.spacing = 2
        self.size_hint_y = None
        self.bind(minimum_height=self.setter('height'))
        
        # Calculate alignment
        self.halign = 'right' if is_user else 'left'
        self.padding = [50, 5, 10, 5] if is_user else [10, 5, 50, 5]
        
        # Label for Sender Name
        sender_name = "YOU" if is_user else "NEXUS"
        name_label = Label(
            text=f"[b]{sender_name}[/b]",
            markup=True,
            size_hint=(1, None),
            height=20,
            halign=self.halign,
            color=(0.3, 0.6, 1, 1) if is_user else (0.7, 0.7, 0.8, 1),
            font_size='11sp'
        )
        name_label.bind(size=name_label.setter('text_size'))
        self.add_widget(name_label)

        # Bubble Layout
        self.bubble = BoxLayout(orientation='vertical', size_hint=(None, None), padding=[15, 12])
        self.bubble.bind(minimum_size=self.bubble.setter('size'))
        
        with self.bubble.canvas.before:
            if is_user:
                Color(0.12, 0.35, 0.7, 0.9)  # Deep Neon Blue
            else:
                Color(0.18, 0.18, 0.22, 0.9)  # Slate Glass
            self.rect = RoundedRectangle(pos=self.bubble.pos, size=self.bubble.size, radius=[18, 18, (2 if is_user else 18), (18 if is_user else 2)])
        
        self.bubble.bind(pos=self._update_rect, size=self._update_rect)
        
        content = Label(
            text=text,
            size_hint=(None, None),
            halign='left',
            valign='top',
            markup=True,
            color=(1, 1, 1, 1),
            font_size='14sp',
            line_height=1.2
        )
        # Ensure bubble doesn't exceed screen width
        max_width = Window.width * 0.75
        content.bind(texture_size=lambda instance, size: self._update_bubble_width(instance, size, max_width))
        
        self.bubble.add_widget(content)
        
        # Alignment wrapper
        wrapper = BoxLayout(size_hint_y=None, height=self.bubble.height)
        wrapper.bind(minimum_height=self.setter('height'))
        if is_user:
            wrapper.add_widget(BoxLayout(size_hint_x=1)) # Spacer
        wrapper.add_widget(self.bubble)
        if not is_user:
            wrapper.add_widget(BoxLayout(size_hint_x=1)) # Spacer
            
        self.add_widget(wrapper)

    def _update_bubble_width(self, instance, size, max_width):
        instance.width = min(size[0], max_width)
        instance.height = size[1]
        self.bubble.width = instance.width + 30
        self.bubble.height = instance.height + 24

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class ChatInterface(ScrollView):
    """Refined chat interface with smoother interaction."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.effect_cls = 'DampedScrollEffect'
        self.layout = BoxLayout(orientation='vertical', size_hint_y=None, padding=[10, 20], spacing=15)
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)
    
    def add_message(self, text, is_user=True):
        msg = ChatMessage(text, is_user)
        self.layout.add_widget(msg)
        # Smoother auto-scroll
        Clock.schedule_once(lambda dt: self.scroll_to(msg), 0.1)
        return msg

class PremiumInput(TextInput):
    """Sleek rounded input."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.foreground_color = (1, 1, 1, 1)
        self.cursor_color = (0.2, 0.6, 1, 1)
        self.padding = [15, 15]
        
        with self.canvas.before:
            Color(0.1, 0.1, 0.15, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
        self.bind(pos=self._update_rect, size=self._update_rect)
        
    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class NexusApp(App):
    """Nexus Agent Premium Kivy Application."""
    
    def build(self):
        """Build the UI."""
        # Set premium dark background safely here
        Window.clearcolor = (0.05, 0.05, 0.08, 1)
        
        self.title = "⚡ Nexus Agent"
        self.icon = 'icon.png'
        
        main_layout = BoxLayout(orientation='vertical')
        
        # Premium Header
        header_layout = BoxLayout(size_hint=(1, 0.12), padding=[10, 10])
        with header_layout.canvas.before:
            Color(0.08, 0.08, 0.12, 1)
            self.header_rect = Rectangle(pos=header_layout.pos, size=header_layout.size)
        header_layout.bind(pos=self._update_header_rect, size=self._update_header_rect)
        
        header = Label(
            text="[b][color=#3399FF]⚡ NEXUS AGENT[/color][/b]\nSelf-Improving AI Assistant",
            markup=True,
            font_size='18sp',
            halign='center'
        )
        header_layout.add_widget(header)
        main_layout.add_widget(header_layout)
        
        # Chat area
        self.chat = ChatInterface()
        main_layout.add_widget(self.chat)
        
        # Input area
        input_container = BoxLayout(orientation='horizontal', size_hint=(1, None), height=70, padding=[10, 10, 10, 10], spacing=10)
        with input_container.canvas.before:
            Color(0.05, 0.05, 0.08, 1)
            self.input_rect = Rectangle(pos=input_container.pos, size=input_container.size)
        input_container.bind(pos=self._update_input_rect, size=self._update_input_rect)
            
        self.input_field = PremiumInput(
            hint_text='Ask Nexus anything...',
            multiline=False,
            size_hint=(0.85, 1)
        )
        self.input_field.bind(on_text_validate=self.send_message)
        input_container.add_widget(self.input_field)
        
        send_btn = Button(
            text='⚡',
            size_hint=(0.15, 1),
            background_normal='',
            background_color=(0.2, 0.4, 0.8, 1),
            font_size='20sp'
        )
        send_btn.bind(on_press=self.send_message)
        input_container.add_widget(send_btn)
        
        main_layout.add_widget(input_container)
        
        self.agent = None
        self.is_thinking = False
        Clock.schedule_once(self.init_agent, 0.5)
        
        Clock.schedule_once(lambda dt: self.chat.add_message(
            "Welcome to [b]Nexus[/b]! ⚡\n\nI'm your highly autonomous AI assistant powered by the Harmes architecture.\n\nType a message to get started!",
            is_user=False
        ), 0.3)
        
        return main_layout

    def _update_header_rect(self, instance, value):
        self.header_rect.pos = instance.pos
        self.header_rect.size = instance.size
        
    def _update_input_rect(self, instance, value):
        self.input_rect.pos = instance.pos
        self.input_rect.size = instance.size
    
    def init_agent(self, dt):
        try:
            config = Config.load()
            self.agent = NexusAgent(config)
            Clock.schedule_once(lambda dt: self.chat.add_message(f"✓ Connected securely to {config.provider}/{config.model}", is_user=False), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.chat.add_message(f"⚠️ Initialization Error: {str(e)}", is_user=False), 0)
    
    def send_message(self, instance):
        text = self.input_field.text.strip()
        if not text or self.is_thinking:
            return
        
        self.is_thinking = True
        self.input_field.text = ''
        
        self.chat.add_message(text, is_user=True)
        thinking = ChatMessage("⚡ Nexus is analyzing...", is_user=False)
        self.chat.layout.add_widget(thinking)
        
        def process():
            if self.agent:
                try:
                    import asyncio
                    response = asyncio.run(self.agent.run_conversation(text))
                    Clock.schedule_once(lambda dt: self._show_response(response, thinking), 0)
                except Exception as e:
                    Clock.schedule_once(lambda dt: self._show_response(f"⚠️ Error: {str(e)}", thinking), 0)
            else:
                Clock.schedule_once(lambda dt: self._show_response("Agent not initialized.", thinking), 0)
            self.is_thinking = False
        
        threading.Thread(target=process, daemon=True).start()
    
    def _show_response(self, response, thinking_widget):
        self.chat.layout.remove_widget(thinking_widget)
        self.chat.add_message(response, is_user=False)

if __name__ == '__main__':
    NexusApp().run()
