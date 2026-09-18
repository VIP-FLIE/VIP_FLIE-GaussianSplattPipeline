from .base_section import PipelineSection
import tkinter as tk
from typing import List


class Newline_Test(PipelineSection):
    
    def __init__(self, name: str, config):
        super().__init__(name, config)
        
    def render_options(self, parent: tk.Frame):
        # Section title or description
        self._add_subtitle(parent, text="This is a dummy script for newline testing.") 

    def build_command(self, settings: dict) -> List[str]:
        # Delegate command building to the specialized builder
        from core.command_builders import Newline_Test
        return Newline_Test.build(self.config.get_section_config(self.name))

