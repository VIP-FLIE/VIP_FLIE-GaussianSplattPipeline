import tkinter as tk
from tkinter import ttk
import queue
import sys
import os
import argparse

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from core.state_models import PipelineConfiguration
from core.executor import AsyncExecutor
from core.pipeline_manager import PipelineManager
from core.category import PipelineCategory, SelectionMode
from gui.app_window import AppWindow
from gui.style import bgColor
from sections.newline_test import Newline_Test

# Sections
from sections.example_section import ExampleSection
from sections.blur_section import BlurSection
from sections.extract_frames_section import ExtractFramesSection
from sections.deduplicate_section import DeduplicateSection
from sections.metashape_section import MetashapeSection
from sections.brush_section import BrushSection

def main(debug:bool=False):
    output_queue = queue.Queue()
    config = PipelineConfiguration()
    executor = AsyncExecutor(output_queue)
    manager = PipelineManager(config, executor)
    # --- Define Categories & Sections ---
    
    # 1. Frame Extraction
    cat_extrct = PipelineCategory("Frame Extraction", SelectionMode.SINGLE, stage_index=1)
    cat_extrct.add_section(ExtractFramesSection("Frame Extraction", config))
    manager.add_category(cat_extrct)
    
    # 2. Preprocessing (Multi-Select allowed)
    cat_prep = PipelineCategory("Preprocessing", SelectionMode.MULTI, stage_index=2)
    cat_prep.add_section(BlurSection("Blur Filter", config))
    cat_prep.add_section(DeduplicateSection("Deduplicate Frames", config))
    manager.add_category(cat_prep)
    
    # 3. SfM (Single Select implied)
    cat_sfm = PipelineCategory("Structure from Motion", SelectionMode.SINGLE, stage_index=3)
    #TODO: ImplementTest Colmap
    #cat_sfm.add_section(ExampleSection("COLMAP", config))
    #TODO: ImplementTest Glomap
    #cat_sfm.add_section(ExampleSection("GLOMAP (Global)", config))
    #TODO: Test Metashape option 
    cat_sfm.add_section(MetashapeSection("Metashape (Colmap Output)", config))
    manager.add_category(cat_sfm)
    
    # 4. Training
    cat_train = PipelineCategory("Training", SelectionMode.SINGLE, stage_index=4)
    #TODO: Implement Brush Support
    cat_train.add_section(BrushSection("Brush", config))
    manager.add_category(cat_train)
    
    # 5. Debugs
    if (debug):
        cat_debug = PipelineCategory("Testing", SelectionMode.SINGLE, stage_index=5)
        cat_debug.add_section(Newline_Test("Newline Test", config))
        manager.add_category(cat_debug)
        print("Debug Mode Enabled")
        
        
    
    # --- Launch ---
    app = AppWindow(manager, executor, output_queue)
    app.configure(bg=bgColor)
    def on_close():
        executor.stop()
        app.destroy()
        
    app.protocol("WM_DELETE_WINDOW", on_close)
    app.mainloop()

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(description="Gausian Splatting Pipeline Script")
    parser.add_argument('-d','--debug', required=False, help="Debug flag for implementing debug features")
    
    args = parser.parse_args()
    
    if args.debug:
        main(True)
    else :
        main()
    
