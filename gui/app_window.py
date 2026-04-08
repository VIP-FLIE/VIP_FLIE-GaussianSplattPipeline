"""
Controls the Main GUI for the Application 
"""

import tkinter as tk
import queue
import os
import json
from .style import bgColor, normalTextColor, toolbarColor
from core.pipeline_manager import PipelineManager
from core.executor import AsyncExecutor
from .console_widget import ConsoleWidget
from .section_frames import SectionFrame
from .library_widget import LibraryWidget
from .preview_widget import PreviewWidget
from .path_selection_window import PathSelectionWindow
from .settings import SettingsWindow, settings_outline

class AppWindow(tk.Tk):
    """
    Main Object for the app layout
    
    GUI V2: 3-Panel Layout.
    [Library (Tree) | Settings (Forms) | Preview (List)]
    [               Console                            ]
    """
    def __init__(self, manager: PipelineManager, executor: AsyncExecutor, output_queue: queue.Queue):
        super().__init__()
        self.title("Gaussian Splatting Pipeline V2")
        self.geometry("1400x800")
        current_dir = os.getcwd()
        img1 = tk.PhotoImage(file=current_dir+"\\gui\\images\\icon128x128.png")
        img2 = tk.PhotoImage(file=current_dir+"\\gui\\images\\icon256x256.png")
        self.iconphoto(True, img1, img2)
        self.manager = manager
        self.executor = executor
        self.output_queue = output_queue
        self.window_manager_open = False
        self.settings_manager_open = False
        self.pathsWin = None
        self.settingsWin = None
        self.configure(background=bgColor)
        # Event wiring
        self.manager.add_staging_listener(self._on_global_staging_change)

        self.load_settings()
        
        self._setup_ui()

    def _on_global_staging_change(self):
        # Update Preview Widget
        self.preview_widget.refresh()
        # Update Library Toggles (handled by its own listener, but safe to keep decoupling if needed)

    def _setup_ui(self):
        """
        Sets up the main GUI after the main window is created
        """
        self.mainGUI = tk.Frame(self, background=bgColor, padx=0, pady=0)
        self.mainGUI.pack(fill="both", ipadx=0, ipady=0, expand=True)
        # Toolbar
        toolbar = tk.Frame(self.mainGUI, bd=0, background=toolbarColor)
        toolbar.pack(side='top', fill='x', padx=0, pady=0)
        
    
        
        # NOTE: Removed 'bg' kwarg which causes empty buttons on Mac
        runButton = tk.Button(toolbar, text="Run-Pipeline", command=self._run_sequence, bd=0)
        runButton.pack(side='left', padx=(10,0), pady=5, ipadx=1, ipady=1)
        
        estopButton = tk.Button(toolbar, text="E-Stop", command=lambda: self.manager.stop_sequence(), bd=0)
        estopButton.pack(side='left', padx=(10,0), pady=5, ipadx=1, ipady=1)
        estopButton.configure(background=toolbarColor, foreground=normalTextColor, font=("Consolas", 10))
        runButton.configure(background=toolbarColor, foreground=normalTextColor, font=("Consolas", 10))
        
        self.pathsbutton = tk.Button(toolbar, text="Set-Paths", command=self._open_path_selection, bd=0)
        self.pathsbutton.pack(side='left', padx=(10,0), pady=5, ipadx=1, ipady=1)
        self.pathsbutton.configure(background=toolbarColor, foreground=normalTextColor, font=("Consolas", 10))
        
        self.settingsbutton = tk.Button(toolbar, text="Settings", command=self._open_settings_window, bd=0)
        self.settingsbutton.pack(side='left', padx=(10,0), pady=5, ipadx=1, ipady=1)
        self.settingsbutton.configure(background=toolbarColor, foreground=normalTextColor, font=("Consolas", 10))

        # Main Paned Window (Horizontal split: Left, Middle, Right)
        main_pane = tk.PanedWindow(self.mainGUI, orient=tk.HORIZONTAL, opaqueresize=False, bd=0)
        main_pane.pack(fill='both', expand=True, padx=0, pady=0)
        main_pane.configure(background=normalTextColor, relief="flat", sashrelief='raised')

        # 1. Left: Library
        self.library_widget = LibraryWidget(main_pane, self.manager, on_view_section=self._show_section_options, settings=self.global_settings)
        main_pane.add(self.library_widget, minsize=240, width=250)
        self.library_widget.configure(borderwidth=0)
        
        
        # 2. Middle: Options
        self.options_container = tk.Frame(main_pane, background=bgColor)
        main_pane.add(self.options_container, minsize=400)

        # 3. Right: Preview
        self.preview_widget = PreviewWidget(main_pane, self.manager)
        main_pane.add(self.preview_widget, minsize=250)

        # Bottom: Console
        bottom_frame = tk.Frame(self.mainGUI, height=150)
        bottom_frame.pack(side='bottom', fill='x')
        self.console = ConsoleWidget(bottom_frame, self.output_queue)
        self.console.pack(fill='both', expand=True)    

    def _show_section_options(self, section):
        """
        Renders the config for each section when its clicked on
        """ 
        # Clear container
        for widget in self.options_container.winfo_children():
            widget.destroy()
        
        # Render
        frame = SectionFrame(self.options_container, section)
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        section.on_show()

    def _window_mamager_open(self) -> bool:
        return self.window_manager_open

    def _open_path_selection(self):
        """
        Opens the window to select input output folders
        Also checks to see if the window is already open and if so,
        brings it to the front
        """
        if self.window_manager_open and self.pathsWin:
            self.pathsWin.lift()
        else:
            self.window_manager_open = True
            self.pathsWin = PathSelectionWindow(self, self.manager.config)
            self.pathsWin.set_callback(self.preview_widget.refresh)
            self.pathsWin.protocol("WM_DELETE_WINDOW", self._on_path_selection_closing)
        # Optional: Make it modal
        # win.transient(self)
        # win.grab_set()
    
    def _on_path_selection_closing(self):
        """
        Destroys the path selection window object on close and 
        sets the flag back to false so a new window can open
        """
        self.window_manager_open = False
        if self.pathsWin:
            self.pathsWin.destroy()

        self.pathsWin = None
        
    def _open_settings_window(self, firstTimeStartup:bool = False):
        """
        Opens the global settings window
        Also checks to see if the window is already open and if so,
        brings it to the front
        """
        if self.settings_manager_open and self.settingsWin:
            self.settingsWin.lift()
        else:
            saveSettings = [False, False]
            self.settings_manager_open = True
            self.settingsWin = SettingsWindow(self, self.global_settings, firstTimeStartup, saveSettings)
            if firstTimeStartup:
                self.wait_window(self.settingsWin)
                self._on_settings_closing([True, False])
                self.update()
                self.deiconify()
            else:
                self.wait_window(self.settingsWin)
                self._on_settings_closing(saveSettings)                   

    def _on_settings_closing(self, saveSettings: list[bool]):
        """
        Destroys the settings window object on close and 
        sets the flag back to false so a new window can open.
        Also handels the processing for saving changes and restarting the ui if needed
        """
        self.settings_manager_open = False
        try:
            if self.settingsWin:
                self.settingsWin.destroy()
            
            if saveSettings[0]:
                self.save_settings()
                if saveSettings[1]:
                    self.mainGUI.destroy()
                    self._setup_ui()
                    for stage in self.manager.staged_sections:
                        if stage.settings_key and not self.global_settings["settings"][stage.settings_key]:
                            self.manager.toggle_section_stage(stage, False)
                            
                    self._on_global_staging_change()
                    self.library_widget._refresh_toggles()
            else:
                self.load_settings()

        except:pass
        self.settingsWin = None

    def load_settings(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_path = os.path.join(base_dir, "settings.json")
        if os.path.isfile(settings_path):
            with open(settings_path, "r") as f:
                try:self.global_settings = json.load(f)
                except:self.global_settings=settings_outline
        else: 
            self.withdraw()
            self.global_settings = settings_outline
            self._open_settings_window(firstTimeStartup=True)
            self.save_settings()
            self.load_settings

    def save_settings(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_path = os.path.join(base_dir, "settings.json")
        settings_file = open(settings_path, "w")
        json.dump(self.global_settings, settings_file, sort_keys=False, indent=4)
    
    def _run_sequence(self):
        self.pathsbutton.configure(state="disabled")
        self.settingsbutton.configure(state="disabled")
        
        self.manager.run_sequence(self.global_settings)
        
        self.pathsbutton.configure(state="normal")
        self.settingsbutton.config(state="normal")