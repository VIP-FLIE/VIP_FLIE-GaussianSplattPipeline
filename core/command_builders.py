from pathlib import Path
import sys
import os
from typing import List, Dict, Any

class BlurCommandBuilder:
    @staticmethod
    def build(config: Dict[str, Any]) -> List[str]:
        """
        Builds the command line arguments for the Blur Filter script.
        """
        # Resolve script path relative to this file
        # This file is in core/
        # Scripts are in scripts/
        # Path: ../scripts/blur_filter.py
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # base_dir is now the project root
        script_path = os.path.join(base_dir, "scripts", "blur_filter.py")
        
        cmd = [ sys.executable, script_path]
        
        # injected paths
        if "input_dir" in config:
            cmd.extend(["--input_dir", str(config["input_dir"])])
        
        if "output_dir" in config:
            cmd.extend(["--output_dir", str(config["output_dir"])])
            
        # Optional args
        
        # Target Count
        if "target_count" in config:
            try:
                tc = float(config["target_count"])
                if tc > 0:
                    cmd.extend(["--target_count", str(int(tc))])
            except (ValueError, TypeError):
                pass
                
        # Keep Percentage
        if "target_percentage" in config:
            try:
                tp = float(config["target_percentage"])
                # Heuristic: If value > 1.0, assume it is 0-100 range and normalize
                if tp > 1.0:
                    tp = tp / 100.0
                cmd.extend(["--keep_percent", str(tp)])
            except (ValueError, TypeError):
                pass

        # Groups
        if "groups" in config:
            try:
                g = float(config["groups"])
                if g > 0:
                    cmd.extend(["--groups", str(int(g))])
            except (ValueError, TypeError):
                pass
                
        # Dry Run
        # Checkbox usually stores boolean or 0/1
        dr = config.get("dry_run", False)
        # It might be a string "0" or "1" or "False" if coming from some UI save
        if str(dr).lower() in ("true", "1", "yes"):
             cmd.append("--dry_run")

        return cmd

class DeduplicateCommandBuilder:
    @staticmethod
    def build(config: Dict[str, Any]) -> List[str]:
        """
        Builds the command line arguments for the Deduplicate script.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # base_dir is project root
        script_path = os.path.join(base_dir, "scripts", "deduplicate.py")
        
        cmd = [sys.executable, script_path]
        
        # Injected paths
        # Deduplicate script mainly needs input_dir. 
        # For chaining, if this follows Blur, 'input_dir' here is the 'output_dir' of Blur.
        if "input_dir" in config:
            cmd.extend(["--input_dir", str(config["input_dir"])])

        if "output_dir" in config:
            cmd.extend(["--output_dir", str(config["output_dir"])])
            
        # Threshold
        if "threshold" in config:
            try:
                th = float(config["threshold"])
                # Boundary checks if needed
                if 0.0 <= th <= 1.0:
                    cmd.extend(["--threshold", str(th)])
            except (ValueError, TypeError):
                pass

        # Resolution (resize_width)
        if "resolution" in config:
            try:
                # The GUI Dropdown likely returns an int or string "512"
                res = int(config["resolution"])
                if res > 0:
                    cmd.extend(["--resize_width", str(res)])
            except (ValueError, TypeError):
                pass
                
        # Dry Run
        dr = config.get("dry_run", False)
        if str(dr).lower() in ("true", "1", "yes"):
             cmd.append("--dry_run")
             
        # Note: 'resolution' is in the GUI but not exposed in scripts/deduplicate.py CLI arguments yet.
        # We will need to update scripts/deduplicate.py to accept it if we want to support it.

        return cmd

class ExtractFramesCommandBuilder:
    @staticmethod
    def build(config: Dict[str, Any]) -> List[str]:
        """
        Builds the command line arguments for the Extract Frames script.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # base_dir is project root
        script_path = os.path.join(base_dir, "scripts", "extract_frames.py")
        
        cmd = [ sys.executable, script_path]
        
        # Mandatory Arguments
        if "input_dir" in config:
            cmd.extend(["--input_dir", str(config["input_dir"])])
            
        if "output_dir" in config:
            cmd.extend(["--output_dir", str(config["output_dir"])])
            
        # Optional Arguments
        if "format" in config:
            # Dropdown value e.g. "jpg"
            cmd.extend(["--format", str(config["format"])])
            
        if "every_n" in config:
            try:
                n = int(config["every_n"])
                if n > 1:
                    cmd.extend(["--every_n", str(n)])
            except (ValueError, TypeError):
                pass
            
        # Dry Run
        dr = config.get("dry_run", False)
        if str(dr).lower() in ("true", "1", "yes"):
             cmd.append("--dry_run")

        return cmd

class MetashapeCommandBuilder:
    @staticmethod
    def build(config: Dict[str, Any], settings:dict) -> List[str]:
        """
        Builds the command line arguments for the Metashape script.
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # base_dir is project root
        script_path = os.path.join(base_dir, "scripts", "metashape_executor_script.py")
        
        cmd = [sys.executable, script_path]
        
        # Mandatory Arguments (configs not defined in section)
        
        cmd.extend(["--executable", settings["settings"]["metashape"]["path"]])

        if "input_dir" in config:
            cmd.extend(["--input", '"'+str(config["input_dir"])+'"'])
            
        if "output_dir" in config:
            cmd.extend(["--output", '"'+str(config["output_dir"])+'"'])
        
        # Mandatory Arguments (Configs defined in Metashape section)
        if "metashape_name" in config:
            cmd.extend(["--name", '"'+str(config["metashape_name"])+'"'])

        if ("metashape_output" in config) and (config["separateDirFlag"]):
            cmd.extend(["--metashape_output", '"'+str(config["metashape_output"])+'"'])        
        else:
            cmd.extend(["--metashape_output", '"'+str(config["output_dir"]) +'"'])
        print(cmd)
        return cmd
    
class BrushCommandBuilder:
    @staticmethod
    def build(config: Dict[str, Any], settings:dict) -> List[str]:
        """
        Builds the command line arguments for Brush
        """
        brush_exe = settings["settings"]["brush"]["path"]
        
        cmd = [brush_exe]
            
        if "output_dir" in config:
            cmd.extend(["--export-path", str(Path(config["output_dir"]).absolute())])

        if "brush_name" in config:
            cmd.extend(["--export-name", str(config["brush_name"])])
        
        if config["brush_GUI_Flag"]:
            cmd.extend(["--with-viewer"])  
        
        if "brush_steps" in config:
            cmd.extend(["--total-steps", str(config["brush_steps"])])

        if "brush_splats" in config:
            cmd.extend(["--max-splats", str(config["brush_splats"])])

        if "brush_SH" in config:
            cmd.extend(["--sh-degree", str(config["brush_SH"])])    

        if "input_dir" in config:
            cmd.extend([str(Path(config["input_dir"]).absolute())])

        print(cmd)

        return cmd