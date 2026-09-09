"""
    The category script contains the classes used to create categories.
Categories are the "type" of processing that each script does. 

    This ensures that steps are executed in the correct order (ex you dont run the 
de-blur before frame extraction), as well as enforcing exclusivity when two 
scripts of the same type can't be run in the same pipeline (Ex comap and Metashape)
    
    THIS IS NOT WHERE YOU DEFINE CATEGORIES THOUGH!!! To define a category, you must 
declare it in main
"""
from enum import Enum
from typing import List
from sections.base_section import PipelineSection

class SelectionMode(Enum):
    """
    Used to define the selection type for a category
    Args: 
        (Enum):The enumerator used
    Returns:
        str: the string of the mode
    """
    SINGLE = "single"  # Radio button behavior
    MULTI = "multi"    # Checkbox behavior

class PipelineCategory:
    """
    Groups multiple PipelineSections together.
    e.g., 'Preprocessing' category containing 'BlurFilter' and 'FrameExtract'.
    !!!This is the initial object declaration, not where you define categories!!!
    To create a Category, declare it in main
    
    Args:
        name(str): The title of the category.
        selection_mode(SelectionMode): The selection mode used by the category.
        stage_index(int): The unique index of the stage in exectution order. This is used 
            to order the stages in the ui and in the backend when executing so it must be unique!
    
    
    """
    def __init__(self, name: str, selection_mode: SelectionMode, stage_index: int):
        self.name = name
        self.selection_mode = selection_mode
        self.stage_index = stage_index  # 1=Prep, 2=SfM, etc. (For ordering checks)
        self.sections: List[PipelineSection] = []

    def add_section(self, section: PipelineSection):
        self.sections.append(section)
