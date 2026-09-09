import tkinter as tk
from core.pipeline_manager import PipelineManager
from .style import bgColor, sectionBorderColor, toolbarColor, normalTextColor
class PreviewWidget(tk.Frame):
    """
    Right Sidebar.
    Shows the 'Staged' pipeline sequence.
    Allows reordering.
    """
    def __init__(self, parent, manager: PipelineManager):
        super().__init__(parent)
        self.manager = manager
        self.configure(background=bgColor, highlightbackground=sectionBorderColor, bd=1)
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self, text="Pipeline Preview", font=("Helvetica", 12, "bold"), foreground=normalTextColor, background=bgColor).pack(pady=5)
        
        self.listbox = tk.Listbox(self, background=toolbarColor, foreground=normalTextColor, selectmode=tk.SINGLE, relief="flat")
        self.listbox.pack(side="top", fill="both", expand=True, padx=5)
        
        btn_frame = tk.Frame(self, background=bgColor, bd=1)
        btn_frame.pack(fill='x', pady=5)
        
        tk.Button(btn_frame, text="▲", command=self._move_up, background=bgColor, foreground=normalTextColor, 
                relief="flat").pack(side='left', padx=5, expand=True)
        tk.Button(btn_frame, text="▼", command=self._move_down, background=bgColor, foreground=normalTextColor,
                relief="flat").pack(side='left', padx=5, expand=True)
        
        self.warning_lbl = tk.Label(self, text="", foreground="red", wraplength=180, background=bgColor)
        self.warning_lbl.pack(pady=5)

        # Bottom Status
        self.path_status_lbl = tk.Label(self, text="Paths Missing", foreground="red", font=("Helvetica", 10), background=bgColor)
        self.path_status_lbl.pack(side='bottom', pady=10)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        last_stage_index = -1
        has_warning = False
        
        for idx, section in enumerate(self.manager.staged_sections):
            cat = self.manager._find_category_for_section(section)
            cat_name = cat.name if cat else "?"
            
            # Simple Display
            self.listbox.insert(tk.END, f"{idx+1}. [{cat_name}] {section.name}")
            
        # Update Path Status
        ctx = self.manager.config.global_context
        if ctx.input_dir and ctx.output_dir:
            self.path_status_lbl.config(text="Paths Configured", foreground="lime")
        else:
            self.path_status_lbl.config(text="Paths Missing", foreground="red")
            
    def _move_up(self):
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            if self.manager._validate_movement( idx, -1):
                if self.manager.move_staged_item(idx, -1):
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(idx - 1)

    def _move_down(self):
        sel = self.listbox.curselection()
        if sel:
            idx = sel[0]
            if self.manager._validate_movement( idx, 1):
                if self.manager.move_staged_item(idx, 1):
                    self.listbox.selection_clear(0, tk.END)
                    self.listbox.selection_set(idx + 1)
