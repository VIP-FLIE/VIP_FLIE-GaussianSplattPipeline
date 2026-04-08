import tkinter as tk
from tkinter import filedialog
from gui.style import bgColor, normalTextColor

class SettingsWindow(tk.Toplevel):
    """
        Class for opening and managing the settings window
        First time mode for initial settings config when you start up the procram without a settings file
    """
    def __init__(self, parent: tk.Tk, settings: dict, firstTimeStartup=False, restartBool : list[bool] = [False,False]):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("600x500")
        self.config(background=bgColor)
        self.settings = settings
        self.restartBool = restartBool
        if firstTimeStartup:
            self.firstTimeUI()
        else: self.settupUI()
        
    
    def firstTimeUI(self):
        tk.Frame(self, height=10, background=bgColor).pack()
        self.hellotext = tk.Label(self, text="Welcome to the Gaussian Splatt Pipeline!", font=("Consolas", 18), background=bgColor, foreground=normalTextColor)
        self.hellotext.pack(anchor="center")
        self.hellosubtext = tk.Label(self, text="Please configure the settings below for first time settup", font=("Consolas", 12), background=bgColor, foreground=normalTextColor)
        self.hellosubtext.pack(anchor="center")
        tk.Frame(self, height=20, background=bgColor).pack()
        self.loadSettingButtons()
        self.savebuttonholder = tk.Frame(self, background=bgColor)
        self.savebuttonholder.pack(side="bottom", fill="both")
        self.closebutton = tk.Button(self.savebuttonholder, text="Save", command=self.destroy, background=bgColor, foreground=normalTextColor)
        self.closebutton.pack(anchor='sw', padx=15, pady=15, side="right")


    def settupUI(self):
        tk.Frame(self, height=10, background=bgColor).pack()
        tk.Label(self, text="Settings", font=("Consolas", 18), background=bgColor, foreground=normalTextColor).pack(anchor="center")
        tk.Frame(self, height=10, background=bgColor).pack()
        self.loadSettingButtons()
        self.savebuttonholder = tk.Frame(self, background=bgColor)
        self.savebuttonholder.pack(side="bottom", fill="both")
        self.closebutton = tk.Button(self.savebuttonholder, text="Cancel", command=lambda *args: self.close_window([False, False]), background=bgColor, foreground=normalTextColor)
        self.closebutton.pack(anchor='sw', padx=(5,15), pady=15, side="right")
        self.savebutton = tk.Button(self.savebuttonholder, text="Save", command=lambda *args: self.close_window([True, False]), background=bgColor, foreground=normalTextColor)
        self.savebutton.pack(anchor='sw', padx=(5,15), pady=15, side="right")
        self.savebuttonrestart = tk.Button(self.savebuttonholder, text="Save and Restart", command=lambda *args: self.close_window([True, True]), background=bgColor, foreground=normalTextColor)
        self.savebuttonrestart.pack(anchor='sw', padx=(5,15), pady=15, side="right")

        

    def loadSettingButtons(self):  
        self._add_Label(self, 'Brush Settings:')
        self.brushFrame = tk.Frame(self, background=bgColor)
        self.brushFrame.pack(anchor="w", padx=10, pady=(0,5), fill='x')
        self._add_checkbox(self.brushFrame, "Enable Brush Support:", "brush", "enabled")
        self._add_folder_selector(self.brushFrame, "Set Path to Brush Executable:", "brush", "path", "Select the Brush Executable file")
        
        self._add_Label(self, "Metashape Settings:")
        self.metashapeFrame = tk.Frame(self, background=bgColor)
        self.metashapeFrame.pack(anchor="w", padx=10, pady=(0,5), fill='x')
        self._add_checkbox(self.metashapeFrame, "Enable Metashape Support:", "metashape", "enabled")
        self._add_folder_selector(self.metashapeFrame, "Set Path to Metashape EXE:", "metashape", "path", "Select the Metashape EXE file")

    def close_window(self, settingsBool: list[bool]):
        self.restartBool[0] = settingsBool[0]
        self.restartBool[1] = settingsBool[1]
        self.destroy()

    def _add_Label(self, parent, text: str):
        title = tk.Label(parent, text=text, font=("Consolas", 12), background=bgColor, foreground=normalTextColor)
        title.pack(anchor="w", padx=5, pady=(0,5))
    
    def _add_checkbox(self, parent: tk.Frame, label_text: str, setting_key:str, setting_name:str):
        """
        Helper to create a Checkbox.
        Example:
        
        Enable Spherical frames ☑
        
        """
        frame = tk.Frame(parent, bg=bgColor)
        frame.pack(fill='x', pady=2, padx=(10,0))
        
        lbl = tk.Label(frame, text=label_text, anchor='w', bg=bgColor, fg=normalTextColor)
        lbl.pack(side='left', padx=0,pady=0)
        
        current_value = self.settings["settings"][setting_key][setting_name]
        var = tk.BooleanVar(value=current_value)
        var.trace_add("write", lambda *args:  self._set_bool(setting_key, setting_name, var.get()))
        
        chk = tk.Checkbutton(frame, variable=var, bg=bgColor, fg=normalTextColor,justify="center",activebackground=bgColor, activeforeground=normalTextColor, selectcolor=bgColor)
        chk.pack(side='right', padx=0, pady=0) # Offset to align somewhat with entries

    def _add_folder_selector(self, parent: tk.Frame, label_text: str, setting_key:str, setting_name:str, fileDialogTitle:str): 
        """
        Helper to create an executable selector box.
        Example:
                            ┌────────────┐
        Important file      │Select file │
                            └────────────┘  
        """
        topFrame = tk.Frame(parent, padx=0, pady=0, background=bgColor)
        topFrame.pack(fill='x', pady=2, padx=(10,5))
        
        frame1 = tk.Frame(topFrame, bg=bgColor)
        frame1.pack(fill='x', expand=True, anchor='n')
        
        lbl = tk.Label(frame1, text=label_text, anchor='w', bg=bgColor, fg=normalTextColor)
        lbl.pack(side='left', padx=0)

        current_value = self.settings["settings"][setting_key][setting_name]
        textvar = tk.StringVar(value=current_value)
        textvar.trace_add("write", lambda *args: self._set_string(setting_key, setting_name, textvar.get()))

        tk.Button(frame1, text="Select...", anchor='e', command=lambda:self._select_input(textvar, fileDialogTitle), background=bgColor, foreground=normalTextColor
                  ).pack(side='right', padx=2)
        
        frame2 = tk.Frame(topFrame, bg=bgColor)
        frame2.pack(fill='x', expand=True, anchor='s', padx=(0.0,2.0))
        tk.Entry(frame2, textvariable=textvar, state='readonly',background=bgColor, foreground=normalTextColor,readonlybackground=bgColor
                 ).pack(fill='x', side='left', expand=True, padx=0)

    def _set_bool(self, setting_key:str, setting_name:str, value : bool):
        self.settings["settings"][setting_key][setting_name] = value

    def _set_string(self, setting_key:str, setting_name:str, value:str):
        self.settings["settings"][setting_key][setting_name] = value

    def _select_input(self, textVar:tk.StringVar, fileDialogTitle:str):    
        path = filedialog.askopenfilename(parent=self, title=fileDialogTitle, filetypes=[("Windows Files", "*.exe"), ("All files", "*.*")])
        textVar.set(path)

    
settings_outline = {
    "version": "0.1.0",
    "settings": {
        "brush" :{
            "enabled":False,
            "path":""
        },
        "metashape": {
            "enabled":False,
            "path":""
        }
    }
}