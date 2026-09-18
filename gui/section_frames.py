import tkinter as tk
from sections.base_section import PipelineSection
from .style import bgColor, normalTextColor

class SectionFrame(tk.Frame):
    """
    The Parent frame for the settings(middle) pane.
    It simply calls `section.render_options(self)`.
    """
    def __init__(self, parent: tk.Widget, section: PipelineSection):
        super().__init__(parent)
        self.section = section
        self.config(background=bgColor)
        
        # Title of the section (optional visual header)
        header = tk.Label(self, text=f"Configure: {section.name}", font=("Helvetica", 14, "bold"), 
                          background=bgColor, foreground=normalTextColor)
        header.pack(pady=(0, 10))
        
        # Render the specific widgets for this section
        self.section.render_options(self)
