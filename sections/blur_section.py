from typing import List
import tkinter as tk
import sys
import os
from .base_section import PipelineSection

class BlurSection(PipelineSection):
    """
    A specific implementation of a pipeline step.
    Groups frames and removes % of blurry frames from group
    """
    def __init__(self, name: str, config):
        super().__init__(name, config)
        
    def render_options(self, parent: tk.Frame):
        # Section title or description
        #tk.Label(parent, text="This is a dummy section for verification.", fg="gray").pack(pady=5)
        self._add_subtitle(parent, text="This is a dummy section for verification.")
        # Add some configurable inputs
        self._add_int_spinbox(parent, "Target Count (0=Auto):", "target_count", 0, 10000, 1, 0)
        self._add_float_spinbox(parent, "Keep %(0-1):", "target_percentage", 0.00, 1.00, 0.01, 0.95)
        self._add_int_spinbox(parent, "Groups", "groups", 0, 10000, 1, 10) # max/default groups is arbitrary

        self._add_checkbox(parent, "Dry Run (Simulate)", "dry_run", default_val=False)

    def build_command(self, settings: dict) -> List[str]:
        # Delegate command building to the specialized builder
        # ensuring we pass the section config (which includes the injected paths)
        from core.command_builders import BlurCommandBuilder
        return BlurCommandBuilder.build(self.config.get_section_config(self.name))
