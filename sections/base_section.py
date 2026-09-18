from abc import ABC, abstractmethod
import tkinter as tk
from tkinter import Misc, filedialog
from typing import List, Any, Dict, Optional
from core.state_models import PipelineConfiguration
from gui.style import bgColor, normalTextColor

class PipelineSection(ABC):
    """
    Abstract Base Class for a single step in the pipeline.
    Enforces the interface for Rendering Options and Building Commands.
    """
    def __init__(self, name: str, config: PipelineConfiguration, settings_key: None | str = None):
        self.name = name
        self.config = config
        self.settings_key = settings_key
        # Internal storage for widgets so we can read them later
        # Key = Config Key, Value = Tkinter Variable (StringVar, IntVar, etc.)
        self.widget_vars: Dict[str, tk.Variable] = {}
        
        # Chaining paths
        self.input_path: str = ""
        self.output_path: str = ""

    @abstractmethod
    def render_options(self, parent: tk.Frame):
        """
        Draw the configuration widgets for this section into `parent`.
        Should verify if config keys exist, if not, set defaults.
        """
        pass

    def set_paths(self, input_path: str, output_path: str):
        """Called by PipelineManager to inject chained paths."""
        """TODO: Look into the above"""
        self.input_path = input_path
        self.output_path = output_path
        
        # We also update the config so the GUI (if open) reflects this, 
        # or at least so the build_command can find it.
        self.config.update_section_config(self.name, "input_dir", input_path)
        self.config.update_section_config(self.name, "output_dir", output_path)

    @abstractmethod
    def build_command(self, settings: dict) -> List[str]:
        """
        Constructs the strict command line arguments string list.
        e.g., ['python', 'script.py', '--input', '...']
        Requires reading from self.config (or self.widget_vars if they are synced).
        """
        pass

    def validate(self) -> bool:
        """
        Override this to check if necessary inputs exist (files, paths)
        before running.
        """
        return True

    def on_show(self):
        """Called when this section is selected in the UI sidebar."""
        pass

    # --- Helper methods for Widgets ---
    def _add_subtitle(self, parent: tk.Frame, text: str = "This is a dummy title", background = bgColor, textcolor = normalTextColor, padyVar=5):
        
        tk.Label(parent, text=text, fg=textcolor, background=background).pack(pady=padyVar)
    
    
    def _add_entry(self, parent: tk.Frame, label_text: str, config_key: str, default_val: str = ""):
        """
        Helper to create a Label + Entry row.
        Example:
                         ┌────────────┐
        Number of frames │             │
                         └────────────┘
        """
        frame = tk.Frame(parent, background=bgColor)
        frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(frame, text=label_text, width=20, anchor='w', bg=bgColor, fg=normalTextColor)
        lbl.pack(side='left', padx=5)
        
        # Load current value from config or default
        current_val = self.config.get_section_config(self.name).get(config_key, default_val)
        
        var = tk.StringVar(value=str(current_val))
        self.widget_vars[config_key] = var
        
        # Trace changes to update config immediately
        var.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, var.get()))
        
        entry = tk.Entry(frame, textvariable=var, bg=bgColor, fg=normalTextColor)
        entry.pack(side='right', fill='x', expand=False, padx=5)

    def _add_checkbox(self, parent: tk.Frame, label_text: str, config_key: str, default_val: bool = False):
        """
        Helper to create a Checkbox.
        Example:
        
        Enable Spherical frames ☑
        
        """
        frame = tk.Frame(parent, bg=bgColor)
        frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(frame, text=label_text, anchor='w', bg=bgColor, fg=normalTextColor)
        lbl.pack(side='left', padx=5)
        
        current_val = self.config.get_section_config(self.name).get(config_key, default_val)
        var = tk.BooleanVar(value=current_val)
        self.widget_vars[config_key] = var
        
        var.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, var.get()))
        
        chk = tk.Checkbutton(frame, variable=var, bg=bgColor, fg=normalTextColor,justify="center",activebackground=bgColor, activeforeground=normalTextColor, selectcolor=bgColor)
        chk.pack(side='right') # Offset to align somewhat with entries

    def _add_dropdown(self, parent: tk.Frame, label_text: str, config_key: str, options: List[str], default_val: str, width: int | None = 10):
        """
        Helper to create a Dropdown (OptionMenu).
        Example:
        
        Choose file type ┌────────────┐
                         │     PNG     │
                         │────────────│
                         │     Jpeg    │
                         └────────────┘
        
        """
        frame = tk.Frame(parent, background=bgColor)
        frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(frame, text=label_text, anchor='w', bg=bgColor, fg=normalTextColor)
        lbl.pack(side='left', padx=5)
        
        current_val = self.config.get_section_config(self.name).get(config_key, default_val)
        if current_val not in options and options:
             current_val = options[0]

        var = tk.StringVar(value=current_val)
        self.widget_vars[config_key] = var
        
        var.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, var.get()))
        
        menu = tk.OptionMenu(frame, var, *options)
        
        if width:
            menu.config(width=width, bg=bgColor, fg=normalTextColor, highlightbackground=bgColor, highlightcolor=bgColor)
            menu.pack(side='right', padx=5)
        else:
            menu.pack(side='right', fill='x', expand=False, padx=5)

    def _add_float_spinbox(self, parent: tk.Frame, label_text: str, config_key: str, 
                           min_val: float, max_val: float, step: float, default_val: float):
        """
        Helper to create a Float Spinbox (up/down arrows).
        Example:
                         ┌────────────┐
                         │           ▲ │        
        Number of seconds│    10.00    │
                         │           ▼ │
                         └────────────┘     
        """
        frame = tk.Frame(parent, bg=bgColor)
        frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(frame, text=label_text, width=20, anchor='w', bg=bgColor, fg=normalTextColor)
        lbl.pack(side='left', padx=5)
        
        current_val = self.config.get_section_config(self.name).get(config_key, default_val)
        
        # Ensure value is float for consistency
        try:
            current_val = float(current_val)
        except (ValueError, TypeError):
            current_val = float(default_val)

        var = tk.DoubleVar(value=current_val)
        self.widget_vars[config_key] = var
        
        var.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, var.get()))
        
        # width=10 is approx half of a typical entry that expands
        sb = tk.Spinbox(frame, from_=min_val, to=max_val, increment=step,
                        textvariable=var, format="%.2f", width=10, bg=bgColor,
                        fg=normalTextColor, buttonbackground=bgColor)
        sb.pack(side='right', padx=5)  # No expand=True, so it stays small

    def _add_int_spinbox(self, parent: tk.Frame, label_text: str, config_key: str, 
                         min_val: int, max_val: int, step: int, default_val: int):
        """
        Helper to create an Integer Spinbox.
        Example:
                         ┌────────────┐
                         │           ▲ │        
        Number of Frames │    1000     │
                         │           ▼ │
                         └────────────┘  
        """
        frame = tk.Frame(parent, bg=bgColor)
        frame.pack(fill='x', pady=2)
        
        lbl = tk.Label(frame, text=label_text, width=20, anchor='w', bg=bgColor, fg=normalTextColor)
        lbl.pack(side='left', padx=5)
        
        current_val = self.config.get_section_config(self.name).get(config_key, default_val)
        try:
            current_val = int(float(current_val))
        except (ValueError, TypeError):
            current_val = int(default_val)

        var = tk.IntVar(value=current_val)
        self.widget_vars[config_key] = var
        
        var.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, var.get()))
        
        sb = tk.Spinbox(frame, from_=min_val, to=max_val, increment=step,
                        textvariable=var, bg=bgColor,
                        fg=normalTextColor, buttonbackground=bgColor)
        sb.pack(side='right', padx=5)


    def _add_folder_selector(self, parent: tk.Frame, label_text: str, config_key: str): 
        """
        Helper to create a file selector box.
        Example:
                            ┌────────────┐
        Important file      │Select file │
                            └────────────┘  
        """
        topFrame = tk.Frame(parent, padx=0, pady=0, background=bgColor)
        topFrame.pack(fill='x', pady=2)
        
        frame1 = tk.Frame(topFrame, bg=bgColor)
        frame1.pack(fill='x', expand=True, anchor='n')
        
        lbl = tk.Label(frame1, text=label_text, anchor='w', bg=bgColor, fg=normalTextColor)
        lbl.pack(side='left', padx=5)

        current_val = self.config.get_section_config(self.name).get(config_key, "")
        textvar = tk.StringVar(value=current_val)
        textvar.trace_add("write", lambda *args: self.config.update_section_config(self.name, config_key, textvar.get()))

        tk.Button(frame1, text="Select...", anchor='e', command=lambda:self._select_input(parent, textvar), background=bgColor, foreground=normalTextColor
                  ).pack(side='right', padx=2)
        
        frame2 = tk.Frame(topFrame, bg=bgColor)
        frame2.pack(fill='x', expand=True, anchor='s', padx=(5.0,2.0))
        tk.Entry(frame2, textvariable=textvar, state='readonly',background=bgColor, foreground=normalTextColor,readonlybackground=bgColor
                 ).pack(fill='x', side='left', expand=True, padx=0)
    
    def _select_input(self, parent: Misc, textVar:tk.StringVar):    
        path = filedialog.askdirectory(parent=parent, title="Select Input Directory")
        textVar.set(path)