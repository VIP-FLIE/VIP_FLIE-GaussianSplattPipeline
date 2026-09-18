from typing import List
import tkinter as tk
import sys
from .base_section import PipelineSection

class ExampleSection(PipelineSection):
    """
    A specific implementation of a pipeline step.
    Simulates a time-consuming task.
    """
    def __init__(self, name: str, config):
        super().__init__(name, config)
        
    def render_options(self, parent: tk.Frame):
        # Section title or description
        self._add_subtitle(parent, text="This is a dummy section for verification.")
        
        # Add some configurable inputs
        self._add_entry(parent, "Sleep Duration (s):", "duration", default_val="2")
        self._add_entry(parent, "Echo Message:", "message", default_val="Hello World")
        self._add_checkbox(parent, "Force Error?", "should_fail", default_val=False)
        self._add_float_spinbox(parent, "Float Test:", "test_float", 0.0, 10.0, 0.5, 5.0)

    def build_command(self, settings: dict) -> List[str]:
        # Read values from config
        cfg = self.config.get_section_config(self.name)
        duration = cfg.get("duration", "2")
        message = cfg.get("message", "Hello")
        fail = cfg.get("should_fail", False)
        
        # In a real scenario, this would call your python script.
        # Here we use python -c to simulate work.
        
        code = f"""
import time, sys
print('Dummy Script Started...')
print('Input Path: {self.input_path}')
print('Output Path: {self.output_path}')
print('Message: {message}')
time.sleep({duration})
if {str(fail)}:
    print('Simulated Failure!', file=sys.stderr)
    sys.exit(1)
print('Dummy Script Finished.')
"""
        return [sys.executable, "-c", code]
    
    def validate(self) -> bool:
        # Example validation
        cfg = self.config.get_section_config(self.name)
        try:
            d = float(cfg.get("duration", 0))
            if d < 0:
                print("Duration must be positive")
                return False
        except ValueError:
            return False
            
        return True
