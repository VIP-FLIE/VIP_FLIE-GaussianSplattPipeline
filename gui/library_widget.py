import tkinter as tk
from typing import Callable
from core.pipeline_manager import PipelineManager
from sections.base_section import PipelineSection
from .style import bgColor, normalTextColor

class LibraryWidget(tk.Frame):
    """
    Left Sidebar.
    Displays categories and their sections.
    Handles 'Selection' (viewing options) and 'Staging' (adding to pipeline).
    """
    def __init__(self, parent, manager: PipelineManager, on_view_section: Callable, settings: dict):
        super().__init__(parent)
        self.manager = manager
        self.on_view_section = on_view_section # Callback when user clicks name to view options
        self.configure(border=0, width=200, background=bgColor)
        self.settings = settings
        self._setup_ui()
        # Listen for updates
        self.manager.add_staging_listener(self._refresh_toggles)

    def _setup_ui(self):
        # We use a Canvas+Frame to allow scrolling if list is long
        canvas = tk.Canvas(self, background=bgColor, highlightthickness=0)
        
        self.scrollable_frame = tk.Frame(canvas, background=bgColor)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas_window = canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        
        canvas.bind("<Configure>", lambda e: self.on_canvas_configure(e, canvas, canvas_window, self.scrollbar))
        
        canvas.pack(side="left", fill="both", expand=True)
        
        
        
        self.toggle_vars = {} # Map section.name -> tk.BooleanVar

        category_count = 1
        
        for category in self.manager.categories:
            """
            Sets up the category titles
            """
            toggledSections = []
            for section in category.sections:
                if (not section.settings_key) or (self.settings["settings"][section.settings_key]["enabled"]):
                        toggledSections.append(section)
                    
                    
                        
            if len(toggledSections):
                category_text = str(category_count) + ". " + category.name
                category_count += 1
                # Header
                cat_frame = tk.Frame(self.scrollable_frame, background='darkgray', pady=2, width=100)
                cat_frame.pack(fill='x', pady=2)
                tk.Label(cat_frame, text=category_text, background='darkgray', font=('Helvetica', 10, 'bold')).pack(anchor='w', ipadx=5, padx=0)
                
                # Items
                for section in toggledSections:
                    """
                    Sets up the individual options in each category
                    """
                    
                    row = tk.Frame(self.scrollable_frame, background=bgColor)
                    row.pack(anchor='w', padx=(10,0), pady=1)
                    
                    # Checkbox for Staging
                    var = tk.BooleanVar(value=False)
                    self.toggle_vars[section.name] = var
                    
                    # We need to capture 'section' in lambda properly
                    cmd = lambda s=section, v=var: self._on_toggle(s, v)
                    
                    chk = tk.Checkbutton(row, variable=var, command=cmd, background=bgColor, highlightthickness=0, foreground=normalTextColor,activebackground=bgColor, activeforeground=normalTextColor, selectcolor=bgColor)
                    chk.pack(side='left')
                    
                    # Clickable Label for Viewing
                    lbl = tk.Label(row, text=section.name, background=bgColor, foreground=normalTextColor, cursor="hand2")
                    lbl.pack(side='left', fill='x', expand=True, anchor='w')
                    lbl.bind("<Button-1>", lambda e, s=section: self.on_view_section(s))
        
        
        self.scrollbar = tk.Scrollbar(canvas, orient="vertical", command=canvas.yview, bd=0, background=bgColor, activerelief='flat')
        yview = canvas.yview()
        if yview == (0.0, 1.0):
            self.scrollbar.pack_forget()
            self.scrollable = False
        else:
            self.scrollable = True
            self.scrollbar.pack(side="right", fill="y", pady=2)
    
        canvas.configure(yscrollcommand=self.scrollbar.set)
        

    def _on_toggle(self, section, var):
        is_staged = var.get()
        self.manager.toggle_section_stage(section, is_staged)
        # Refresh is triggered by callback to handle Single-Select logic automatically updating UI

    def _refresh_toggles(self):
        """Update checkboxes based on actual staged status when clicked"""
        for section in self.manager.staged_sections:
            if section.name in self.toggle_vars:
                self.toggle_vars[section.name].set(True)
        
        # Also need to uncheck ones NOT in staged
        staged_names = [s.name for s in self.manager.staged_sections]
        for name, var in self.toggle_vars.items():
            if name not in staged_names:
                var.set(False)
    
                
    
    def on_canvas_configure(self, event, canvas, inner_frame_id, scrollbar):
        """
        Used as a callback for theconfigure event of the canvas object. 
        Forces the items inside the scrollable frame to fill
        the frame

        Args:
            event (event): the event data (adjusted width and height)
            canvas (tk.Canvas): the canvas that is used as the base of
                the scrollable frame
            inner_frame_id (tk.canvas.window): the window inside the canvas
                that gets adjusted based on the size of the window
            scrollbar (tk.Scrollbar): the scroll bar for the window
        """
        canvas_width = event.width - scrollbar.winfo_width() - 5
        canvas.itemconfigure(inner_frame_id, width=canvas_width)

