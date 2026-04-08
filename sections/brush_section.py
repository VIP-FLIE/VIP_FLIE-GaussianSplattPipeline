import tkinter as tk
from .base_section import PipelineSection
from typing import List

class BrushSection(PipelineSection):
    """
    Passes the colmap data to brush for splat training
    """
    def __init__(self, name: str, config):
        super().__init__(name, config, settings_key="brush")

    def render_options(self, parent: tk.Frame):
        # Passes options for the section using the abstract base options
        self._add_entry(parent, "Finished Splat Name:", "brush_name", default_val=r"export_{iter}.ply")
        self._add_checkbox(parent, "Show GUI Viewer?", "brush_GUI_Flag", default_val=False)
        self._add_int_spinbox(parent, "Total Training Steps:", "brush_steps", min_val=0, max_val=1000000, step=1000 ,default_val=30000)
        self._add_int_spinbox(parent, "Total Splats:", "brush_splats", min_val=0, max_val=1000000000, step=10000,default_val=10000000)
        self._add_int_spinbox(parent, "Spherical Harmonics:", "brush_SH", min_val=0, max_val=10, step=1,default_val=3)


    def build_command(self, settings: dict) -> List[str]:    
        
        from core.command_builders import BrushCommandBuilder
        return BrushCommandBuilder.build(self.config.get_section_config(self.name), settings)