from typing import List
import tkinter as tk
from .base_section import PipelineSection

class DeduplicateSection(PipelineSection):
    """
    A specific implementation of a pipeline step.
    Removes Frames with high levels of simalarity
    """
    def __init__(self, name: str, config):
        super().__init__(name, config)
        
    def render_options(self, parent: tk.Frame):
        # Section title or description
        self._add_subtitle(parent, text="This is a dummy section for verification.")
        
        # Add some configurable inputs
        self._add_float_spinbox(parent, "Target Count (0=Auto):", "threshold", 0.00, 1.00, 0.01, 0.92)
        self._add_dropdown(parent, "What Resolution to Scale to (512=Auto)", "resolution", ['256','512','1024'], default_val='512', width=10)
        self._add_checkbox(parent, "Dry Run (Simulate)", "dry_run", default_val=False)

    def build_command(self, settings: dict) -> List[str]:
        # Delegate command building to the specialized builder
        from core.command_builders import DeduplicateCommandBuilder
        return DeduplicateCommandBuilder.build(self.config.get_section_config(self.name))
