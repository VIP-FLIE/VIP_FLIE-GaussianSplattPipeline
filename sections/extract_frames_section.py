from typing import List
import tkinter as tk
import sys
import os
from .base_section import PipelineSection

class ExtractFramesSection(PipelineSection):
    """
    A specific implementation of a pipeline step.
    Extracts frames from video files.
    """
    def __init__(self, name: str, config):
        super().__init__(name, config)
        
    def render_options(self, parent: tk.Frame):
        # Section title or description
        self._add_subtitle(parent, text="Extract frames from video files.")
        
        # Add some configurable inputs
        self._add_dropdown(parent, "Output Format", "format", ["png", "jpg"], default_val="png")
        self._add_int_spinbox(parent, "Extract Every Nth Frame", "every_n", 1, 1000, 1, 1)
        self._add_checkbox(parent, "Dry Run (Simulate)", "dry_run", default_val=False)

    def build_command(self, settings: dict) -> List[str]:
        # Delegate command building to the specialized builder
        from core.command_builders import ExtractFramesCommandBuilder
        return ExtractFramesCommandBuilder.build(self.config.get_section_config(self.name))
