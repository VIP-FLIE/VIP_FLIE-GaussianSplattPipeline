import pycolmap
from pathlib import Path
from abc import ABC, abstractmethod
import os
import subprocess
import argparse
import shutil
from config import get_env_executable

class BaseReconstruction(ABC):
  def __init__(self, input_dir, output_dir, camera_model="PINHOLE"):
    '''
    Remove defaults once GUI is implemented
    Add GPU?
    Add Quality?
    Check if Path() is needed with GUI implementation
    Check if output directories exist with os
    working directory logic system vs input/output
    '''
    self.input_dir = Path(input_dir) 
    self.output_dir = Path(output_dir)
    self.camera_model = camera_model
    self.database_path = self.output_dir / "database.db"
    self.sparse_dir = self.output_dir / "sparse"

  def extract_matchFeatures(self):
    '''
    extracts and matches features from images using command line from colmap
    Args:
      input_dir: directory containing images
      output_dir: directory to store results
      camera_model: camera model to use
    Returns:
      nothing ? The extraction/matching is stored in the db?
    '''
    colmap_exe = get_env_executable("COLMAP")
  # Feature extraction
    feature_cmd = [
        colmap_exe, "feature_extractor",
        "--database_path", str(self.database_path),
        "--image_path", str(self.input_dir),
        "--ImageReader.camera_model", self.camera_model,
        "--ImageReader.single_camera", "1",
    ]
    # run the feature extraction
    subprocess.run(feature_cmd, check=True)

    # Feature matching
    matching_cmd = [
        colmap_exe, "exhaustive_matcher",
        "--database_path", str(self.database_path),
    ]
    # run the feature matching
    subprocess.run(matching_cmd, check=True)

    pass

  def find_reconstruction(self):
    '''
    find the reconstruction folder
    see lines 123-131 https://github.com/arpm511/guassian_splats_pipeline/blob/main/scripts/run_colmap.py
    '''
    pass

  @abstractmethod # any class inheriting this function must write their own version of this function
  def perform_mapping(self):
    '''
    kicks out to child class to run the mapping portion
    '''

    pass

  def run(self):
    '''
    called by GUI
    '''
    self.extract_matchFeatures()
    self.perform_mapping()
    pass

class COLMAP_Mapper(BaseReconstruction):
    '''
    runs the COLMAP mapping portion
    '''

    def perform_mapping(self):
        '''
        runs the COLMAP mapping portion
        '''
        colmap_exe = get_env_executable("COLMAP")
        mapper_cmd = [
            colmap_exe, "mapper",
            "--database_path", str(self.database_path),
            "--image_path", str(self.input_dir),
            "--output_path", str(self.sparse_dir),
        ]
        
        subprocess.run(mapper_cmd, check=True)

    pass
        
class GLOMAP_Mapper(BaseReconstruction):
    '''
    runs the GLOMAP mapping portion
    need to clone inside a docker or conda env
    '''
    def perform_mapping(self):
        glomap_exe = get_env_executable("GLOMAP")
        cmd = [
            glomap_exe, "mapper",
            "--database_path", str(self.database_path),
            "--image_path", str(self.input_dir),
            "--output_path", str(self.sparse_dir)
        ]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running GLOMAP: {e}")

        pass

class FASTMAP_Mapper(BaseReconstruction):
    '''
    runs the FASTMAP mapping portion
    need to clone inside a docker or conda env
    '''
    def perform_mapping(self):
        fastmap_exe = get_env_executable("FASTMAP")
        cmd = [
            fastmap_exe, "mapper",
            "--database_path", str(self.database_path),
            "--image_path", str(self.input_dir),
            "--output_path", str(self.sparse_dir)
        ]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error running FASTMAP: {e}")

        pass

class LiMap:
    '''
    Will implement at some later point. Detects features and edges to map

    does extraction, matching, and mapping
    '''
    pass

class mpSfM:
    '''
    Will implement at some later point. Most advanced SfM
    does extraction, matching, and mapping
    '''
    pass