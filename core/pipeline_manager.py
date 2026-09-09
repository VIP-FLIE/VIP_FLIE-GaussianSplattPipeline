from typing import List, Callable, Optional, Dict
from sections.base_section import PipelineSection
from .executor import AsyncExecutor
from .state_models import PipelineConfiguration
from .category import PipelineCategory, SelectionMode
import os

class PipelineManager:
    """
    Manages Categories, Staging, and Execution.
    """
    def __init__(self, 
                 config: PipelineConfiguration, 
                 executor: AsyncExecutor):
        self.config = config
        self.executor = executor
        
        self.categories: List[PipelineCategory] = []
        
        # The Ordered List of Sections to run
        # We store the *Section Objects* directly for simplicity
        self.staged_sections: List[PipelineSection] = []
        
        self.current_step_index = 0
        self.is_sequence_running = False
        
        # Events
        self.on_step_status_change: Optional[Callable[[int, str], None]] = None
        self._staging_listeners: List[Callable[[], None]] = []

    def add_staging_listener(self, callback: Callable[[], None]):
        self._staging_listeners.append(callback)

    def _notify_staging_changed(self):
        for callback in self._staging_listeners:
            callback()

    def add_category(self, category: PipelineCategory):
        self.categories.append(category)

    def toggle_section_stage(self, section: PipelineSection, active: bool):
        """
        Adds or removes a section from the staging list.
        Enforces Single-Select logic if needed.
        """
        if active:
            if section not in self.staged_sections:
                # Logic to handle Single Select:
                # Find the category this section belongs to
                parent_cat = self._find_category_for_section(section)
                if parent_cat and parent_cat.selection_mode == SelectionMode.SINGLE:
                    # Remove other sections from this category
                    for s in parent_cat.sections:
                        if s in self.staged_sections and s != section:
                            self.staged_sections.remove(s)
                
                self.staged_sections.append(section)
            while self._validate_order() == False:
                last_index = -1
                for index, section in enumerate(self.staged_sections):
                    cat = self._find_category_for_section(section)
                    if cat:
                        if cat.stage_index < last_index:
                            self.move_staged_item(index, -1)
                        last_index = cat.stage_index
        else:
            if section in self.staged_sections:
                self.staged_sections.remove(section)
                
        self._notify_staging_changed()

    def _validate_movement(self, index:int, direction:int) -> bool:
        """
        Used to enforce the ordering of the Pipeline when maually 
        reordering the options (aka you can't move an option from 
        category 1 to after category 2)
        
        Args:
            index(int): the index of the section attempting to be moved
            direction(int): the direction the section is attempting to move
            
        Return:
            bool: whether or not the movement is valid
        """
        new_index = direction + index
        section = self.staged_sections[index]
        compared_section = self.staged_sections[new_index]
        cat = self._find_category_for_section(section)
        compared_cat = self._find_category_for_section(compared_section)
        
        if cat == compared_cat:
            return True
        
        return False

    def move_staged_item(self, index: int, direction: int) -> bool:
        """
        Moves item at `index` up (-1) or down (+1).
        Returns True if moved.
        """
        
        new_index = index + direction
              
        if 0 <= new_index < len(self.staged_sections):
            self.staged_sections[index], self.staged_sections[new_index] = \
                self.staged_sections[new_index], self.staged_sections[index]
            
            self._notify_staging_changed()
            return True
        return False

    def _find_category_for_section(self, section: PipelineSection) -> Optional[PipelineCategory]:
        for cat in self.categories:
            if section in cat.sections:
                return cat
        return None

    def run_sequence(self, settings:dict):
        """Runs the STAGED steps."""
        if not self.staged_sections:
             self.executor.output_queue.put("[Manager Error]: No steps staged!\n")
             return

        # V2: Run-time validation
        if not self._validate_order():
             self.executor.output_queue.put("[Manager WARNING]: Pipeline appears out of order. Running anyway...\n")
             # TODO: Show a Popup here and ask to Continue/Cancel.
             # For now, we log it and proceed.
             # May now be a redundant feature to add with pipeline restrictions 
             # but maybe add later as a fail safe?

        if not self._validate_pipeline_environment():
            self.executor.output_queue.put("[Manager Error]: Dataset Validation Failed. Aborting\n")
            return

        self.current_step_index = 0
        self.is_sequence_running = True
        self._run_next_in_sequence(settings)

    def _validate_order(self) -> bool:
        """Checks if stage indices strictly increase."""
        last_index = -1
        for section in self.staged_sections:
            cat = self._find_category_for_section(section)
            if cat:
                if cat.stage_index < last_index:
                    return False
                last_index = cat.stage_index
        return True

    def _validate_pipeline_environment(self) -> bool:
        """
        Validates the Global Environment for the Pipeline.
        1. Global Input Dir exists.
        2. Global Output Dir is writable (or parent exists).
        """
        g_ctx = self.config.global_context
        
        # 1. Input Check
        if not os.path.exists(g_ctx.input_dir):
            self.executor.output_queue.put(f"[Manager Error]: Global Input Directory does not exist: {g_ctx.input_dir}\n")
            return False
            
        # 2. Output Check (Basic)
        # If it exists, check writable. If not, check parent writable.
        if os.path.exists(g_ctx.output_dir):
            if not os.access(g_ctx.output_dir, os.W_OK):
                self.executor.output_queue.put(f"[Manager Error]: Global Output Directory is not writable: {g_ctx.output_dir}\n")
                return False
        else:
            parent = os.path.dirname(g_ctx.output_dir)
            if parent and os.path.exists(parent) and not os.access(parent, os.W_OK):
                self.executor.output_queue.put(f"[Manager Error]: Cannot create Output Directory (Parent not writable): {parent}\n")
                return False
                
        return True

    def _run_next_in_sequence(self, settings:dict):
        if not self.is_sequence_running:
            return

        if self.current_step_index >= len(self.staged_sections):
            self.executor.output_queue.put("[Manager]: Sequence Complete.\n")
            self.is_sequence_running = False
            return

        section = self.staged_sections[self.current_step_index]
        self.executor.output_queue.put(f"\n[Manager]: Starting Step {self.current_step_index+1}: {section.name}\n")
        
        if not section.validate():
            self.executor.output_queue.put(f"[Manager]: Step '{section.name}' validation failed.\n")
            self.is_sequence_running = False
            self._notify_status(self.current_step_index, "Error")
            return

        # Chaining Logic (Snaking)
        # Determine Input
        if self.current_step_index == 0:
            current_input = self.config.global_context.input_dir
        else:
            # Input comes from previous step's output
            current_input = self.staged_sections[self.current_step_index - 1].output_path

        # Determine Output
        if self.current_step_index == len(self.staged_sections) - 1:
            current_output = os.path.join(self.config.global_context.output_dir, "output (" + section.name + ")")
        else:
            # Intermediate output
            # We'll create a folder named after the section inside the global output/intermediate
            # You might want a timestamp or run ID to avoid collisions, but for now simple structure:
            current_output = os.path.join(self.config.global_context.output_dir, "intermediate" , "#" + str(self.current_step_index + 1) + " " + section.name)
            
        # Ensure output directory exists (especially intermediate ones)
        if current_output and not os.path.exists(current_output):
             try:
                 os.makedirs(current_output, exist_ok=True)
             except OSError as e:
                 self.executor.output_queue.put(f"[Manager]: Failed to create output dir {current_output}: {e}\n")
                 # We continue, let the script complain if it fails

        # Apply paths to section
        section.set_paths(current_input, current_output)
        
        # Log for verification
        self.executor.output_queue.put(f"   -> Input: {current_input}\n")
        self.executor.output_queue.put(f"   -> Output: {current_output}\n")

        cmd = section.build_command(settings)
        self._notify_status(self.current_step_index, "Running")
        
        self.executor.run_command(cmd, lambda rc: self._on_sequence_step_finished(rc, settings))

    def _on_sequence_step_finished(self, return_code: int, settings:dict):
        if return_code == 0:
            self._notify_status(self.current_step_index, "Completed")
            self.current_step_index += 1
            self._run_next_in_sequence(settings)
        else:
            self._notify_status(self.current_step_index, "Failed")
            self.executor.output_queue.put("[Manager Error]: Aborted due to failed step\n")
            self.is_sequence_running = False

    def _notify_status(self, index: int, status: str):
        if self.on_step_status_change:
            self.on_step_status_change(index, status)

    def stop_sequence(self):
        self.is_sequence_running = False
        self.executor.stop()
