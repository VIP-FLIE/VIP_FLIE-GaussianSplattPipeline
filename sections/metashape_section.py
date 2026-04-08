from typing import List
import tkinter as tk
import sys
from .base_section import PipelineSection

class MetashapeSection(PipelineSection):
    """
    Passes the dataset to metashape for colmap data
    """
    def __init__(self, name: str, config):
        super().__init__(name, config, settings_key="metashape")
        
    def render_options(self, parent: tk.Frame):
        # Passes options for the section using the abstract base options
        self._add_entry(parent, "Metashape File Name:", "metashape_name")
        self._add_checkbox(parent, "Save Metashape File in a Seperate Directory?", "separateDirFlag", default_val=False)
        self._add_folder_selector(parent, "Select Seperate Metashape File Directory (optional):", "metashape_output")
        

    def build_command(self, settings: dict) -> List[str]:
        metashape_path = settings["settings"][self.settings_key]["path"]     
        from core.command_builders import MetashapeCommandBuilder
        return MetashapeCommandBuilder.build(self.config.get_section_config(self.name), settings)
    
    def validate(self) -> bool:
        #TODO: create validation
        cfg = self.config.get_section_config(self.name)
        try:
            d = float(cfg.get("duration", 0))
            if d < 0:
                print("Duration must be positive")
                return False
        except ValueError:
            return False
            
        return True
    
    
