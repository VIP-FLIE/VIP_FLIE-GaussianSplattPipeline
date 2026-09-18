"""
Important note!!
This script is designed to be passed to metashape through a command line, not acessed through other sections of this program
IT WILL CRASH IF CALLED DIRECTLY!
Instead, call a subprocess with the string '"path\\to\\your\\metashape.exe" -r "C:\\path\\to\\your_script.py" -args' if you wish to use this 
"""

import os
from pathlib import *
import Metashape # type: ignore
import argparse


class MetashapeProject:

    def __init__(self, export_path, project_name, images:list[str], metashape_dir:str):
        self.export_path = export_path
        self.project_name = project_name
        self.images = images
        self.metashape_dir = metashape_dir
    

    def project_execute(self) -> None:
        self.doc = Metashape.Document()
        self.doc.save(self.metashape_dir+"\\"+self.project_name+".psx")
        self.chunk = self.doc.addChunk()
        self.chunk.label = self.project_name + "_Chunk"
        self.chunk.addPhotos(self.images)
        self.doc.save()
        self.align_photos()
        self.doc.save()
        self.export_cameras_to_colmap()
        photocount = len(self.images)
        self.display_metrics(photocount)
        self.doc.save()

    def align_photos(self) -> None:
        self.chunk.matchPhotos(downscale=1, generic_preselection=True, reference_preselection=False)
        self.chunk.alignCameras()

    def export_cameras_to_colmap(self) -> None:
        export_path = f"{self.export_path}/{self.project_name}_COLMAP.txt"
        self.chunk.exportCameras(export_path, format=Metashape.CamerasFormatColmap)

    def display_metrics(self, photocount) -> None:
        aligned_count = 0
        for cam in self.chunk.cameras:
            if cam.transform is not None: # Check if camera has a valid transform matrix
                aligned_count += 1
        with open(self.metashape_dir+"\\"+self.project_name+'_point&photo_stats.txt', 'w') as file:
            file.write(f"Photos Alligned: {aligned_count}\\{photocount}\n")
            file.write(f"Total tie points: {len(self.chunk.tie_points.points)}")
            file.close()
        print(f"Photos Alligned: {aligned_count}\\{photocount}\n")
        print(f"Total tie points: {len(self.chunk.tie_points.points)}")

def recursivefile_search(import_path:str, export_path, name, metashape_directory):
    photos = []
    entries = os.listdir(import_path)
    for entry in entries:
        entrypath = os.path.abspath(import_path + os.path.sep + entry)
        if os.path.isdir(entrypath): 
            if export_path == metashape_directory:
                recursivefile_search(entrypath, export_path+ os.path.sep +os.path.basename(import_path), name, export_path+ os.path.sep +os.path.basename(import_path))
            else:
                recursivefile_search(entrypath, export_path+ os.path.sep +os.path.basename(import_path), name+'_'+os.path.basename(import_path), metashape_directory)
        else:
            if '.png' == entry[-4:] or '.jpg' == entry[-4]: photos.append(entrypath)
    if photos:
        project = MetashapeProject(
        export_path=export_path,
        project_name=name,
        images=photos,
        metashape_dir=metashape_directory,
        )
        project.project_execute()

if __name__ == '__main__':
# Initialize the parser
    parser = argparse.ArgumentParser(description="A simple argument parser")

    # Add arguments
    parser.add_argument("-i", "--input") 
    parser.add_argument("-o", "--output") 
    parser.add_argument("-m", "--metashape_output") 
    parser.add_argument("-n", "--name")

    # Parse the arguments
    args = parser.parse_args()

    if not args.input:
        raise TypeError("Error, no --input directory provided")
    elif not args.output:
        raise TypeError("Error, no ouput dir provided for the colmap data")
    elif not args.metashape_output:
        raise TypeError("Error, no output dir provided for the metashape file")
    elif not args.name:
        raise TypeError("Error, no output file naming convention")

    import_path = args.input
    export_path = args.output
    metashape_directory = args.metashape_output
    name = args.name
    
    recursivefile_search(import_path, export_path, name, metashape_directory)
    
    #entries = os.listdir(import_path)
    # # Keep only files, not directories
    # photos = []
    
    # for entry in entries:
    #     if os.path.isfile(entry):
    #     photos.append(str(import_path) + '\\' + str(file))

    # project = MetashapeProject(
    #     export_path=export_path,
    #     project_name=name,
    #     images=photos,
    #     metashape_dir=metashape_directory,
    # )
    
    # project.project_execute() # type: ignore


