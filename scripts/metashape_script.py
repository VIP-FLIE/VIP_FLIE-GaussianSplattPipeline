"""
Important note!!
This script is designed to be passed to metashape through a command line, not acessed through other sections of this program
IT WILL CRASH IF CALLED DIRECTLY!
Instead, call a subprocess with the string '"path\\to\\your\\metashape.exe" -r "C:\\path\\to\\your_script.py" -args' if you wish to use this 
"""

import os
import Metashape # type: ignore
import argparse


class MetashapeProject:

    def __init__(self, export_path, project_name, images:list[str], metashape_dir:str):
        self.export_path = export_path
        self.project_name = project_name
        self.images = images
        self.metashape_dir = metashape_dir
    

    def project_execute(self) -> None:
        doc = self.create_new_project()
        chunk = self.get_chunk(doc) # type: ignore
        self.save_project(doc, self.metashape_dir, self.project_name) # type: ignore
        self.add_photos_to_chunk(chunk, self.images) # type: ignore
        self.save_project(doc)
        self.align_photos(chunk) # type: ignore
        self.save_project(doc)
        self.export_cameras_to_colmap(chunk, export_path, self.project_name) # type: ignore
        photocount = len(self.images)
        self.display_metrics(chunk, photocount, self.metashape_dir, self.project_name) # type: ignore
        self.save_project(doc)
        Metashape.app.quit()
        
    def create_new_project(self) -> Metashape.app.document:
        doc = Metashape.app.document
        return doc

    def get_chunk(self, doc:Metashape.app.document) -> Metashape.Chunk:
        chunk = doc.chunk
        return chunk

    def add_photos_to_chunk(self, chunk:Metashape.Chunk, photo_paths:list[str]) -> None:
        chunk.addPhotos(photo_paths)

    def align_photos(self, chunk:Metashape.Chunk) -> None:
        chunk.matchPhotos(downscale=1, generic_preselection=True, reference_preselection=False)
        chunk.alignCameras()

    def export_cameras_to_colmap(self, chunk:Metashape.Chunk, path:str, filename:str) -> None:
        export_path = f"{path}/{filename}_COLMAP.txt"
        chunk.exportCameras(export_path, format=Metashape.CamerasFormatColmap)

    def save_project(doc: Metashape.app.document, path:str=None, filename:str=None) -> None: # type: ignore
        if not(path and filename):
            doc.save()
        else:
            doc.save(path+"\\"+filename+".psx")

    def display_metrics(self, chunk:Metashape.app.document.chunk, photocount, metashape_dir:str, project_name:str) -> None:
        aligned_count = 0
        for cam in chunk.cameras:
            if cam.transform is not None: # Check if camera has a valid transform matrix
                aligned_count += 1
        with open(metashape_dir+"\\"+project_name+'_point&photo_stats.txt', 'w') as file:
            file.write(f"Photos Alligned: {aligned_count}\\{photocount}\n")
            file.write(f"Total tie points: {len(chunk.tie_points.points)}")
            file.close()

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
    entries = os.listdir(import_path)
    # Keep only files, not directories
    photos = []

    for file in entries:
        photos.append(str(import_path) + '\\' + str(file))

    project = MetashapeProject(
        export_path=export_path,
        project_name=name,
        images=photos,
        metashape_dir=metashape_directory,
    )
    
    project.project_execute(export_path, name, photos, metashape_directory) # type: ignore