import os
import shutil
import cv2
import numpy as np
import multiprocessing
from skimage.metrics import structural_similarity as ssim
from glob import glob
import time
import argparse

class FrameDeduplicator:
    def __init__(self, source_dir, output_dir=None, threshold=0.92, resize_width=512, dry_run=False):
        """
        Initialize the Deduplicator.
        
        Args:
            source_dir (str): Path to the directory containing image frames.
            output_dir (str): Optional. If provided, UNIQUE frames are copied here. 
                              If None, DUPLICATES are moved to source_dir/duplicates.
            threshold (float): SSIM threshold. 
                               >= Threshold implies duplicate (discard).
                               < Threshold implies new content (keep/pivot).
            resize_width (int): Width to resize images to for comparison (optimization).
            dry_run (bool): If True, simulate actions without moving files.
        """
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.threshold = threshold
        self.resize_width = resize_width
        self.dry_run = dry_run

    def _find_image_directories(self):
        """
        Scans source_dir for directories containing images.
        Returns a list of (input_dir, output_dir, relative_path) tuples.
        """
        image_dirs = []
        extensions = {'.jpg', '.jpeg', '.png'}
        
        has_images = False
        for fname in os.listdir(self.source_dir):
            if os.path.splitext(fname)[1].lower() in extensions:
                has_images = True
                break
        
        if has_images:
            # Root
            out_d = self.output_dir if self.output_dir else self.source_dir
            image_dirs.append((self.source_dir, out_d, "."))
        
        for root, dirs, files in os.walk(self.source_dir):
            if root == self.source_dir and has_images:
                continue
                
            dir_has_images = any(os.path.splitext(f)[1].lower() in extensions for f in files)
            
            if dir_has_images:
                rel_path = os.path.relpath(root, self.source_dir)
                if self.output_dir:
                    out_d = os.path.join(self.output_dir, rel_path)
                else:
                    out_d = root
                image_dirs.append((root, out_d, rel_path))
                
        return image_dirs

    # _load_and_preprocess and _calculate_similarity remain unchanged
    def _load_and_preprocess(self, image_path):
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None: return None
        h, w = img.shape
        scale = self.resize_width / float(w)
        new_h = int(h * scale)
        return cv2.resize(img, (self.resize_width, new_h), interpolation=cv2.INTER_AREA)

    def _calculate_similarity(self, img_a, img_b):
        score, _, = ssim(img_a, img_b, full=True, data_range=255) # type: ignore
        return score

    def _process_chunk(self, file_chunk):
        duplicates_found = []
        if not file_chunk:
            return duplicates_found

        pivot_path = file_chunk[0]
        pivot_img = self._load_and_preprocess(pivot_path)

        for current_path in file_chunk[1:]:
            current_img = self._load_and_preprocess(current_path)
            
            if pivot_img is None or current_img is None:
                continue

            score = self._calculate_similarity(pivot_img, current_img)

            if score >= self.threshold:
                duplicates_found.append(current_path)
            else:
                pivot_path = current_path
                pivot_img = current_img
                
        return duplicates_found
        
    def _process_chunk_wrapper(self, chunk):
        return self._process_chunk(chunk)

    def run(self):
        print(f"--- Starting Deduplication on {self.source_dir} ---")
        if self.output_dir:
             print(f"Output Mode: Copying UNIQUE frames to {self.output_dir}")
        else:
             print(f"In-Place Mode: Moving DUPLICATES to ./duplicates folder")

        target_dirs = self._find_image_directories()
        
        if not target_dirs:
            print("No directories with images found.")
            return

        print(f"Found {len(target_dirs)} directories/videos to process.")
        
        total_files = 0
        total_dupes = 0
        
        # We process each directory sequentially, but parallelize within the directory
        for in_dir, out_dir, rel_path in target_dirs:
            print(f"Processing: {rel_path} ({in_dir})")
            
            # Gather files
            all_files = sorted(glob(os.path.join(in_dir, "*.jpg"))) + \
                        sorted(glob(os.path.join(in_dir, "*.png")))
            
            n_files = len(all_files)
            if n_files == 0: continue
            total_files += n_files
            
            # Parallel Execution
            cpu_count = multiprocessing.cpu_count()
            chunk_size = int(np.ceil(n_files / cpu_count))
            # Ensure at least 1 chunk
            if chunk_size < 1: chunk_size = 1
            
            chunks = [all_files[i:i + chunk_size] for i in range(0, n_files, chunk_size)]
            
            with multiprocessing.Pool(processes=cpu_count) as pool:
                results = pool.map(self._process_chunk_wrapper, chunks)
                
            dir_duplicates = [item for sublist in results for item in sublist]
            dir_duplicates_set = set(dir_duplicates)
            
            total_dupes += len(dir_duplicates)
            print(f"  Found {len(dir_duplicates)} duplicates out of {n_files} frames.")
            
            # Handle Output
            if self.output_dir:
                # COPY UNIQUE
                if not os.path.exists(out_dir) and not self.dry_run:
                    os.makedirs(out_dir, exist_ok=True)
                    
                for fpath in all_files:
                    if fpath not in dir_duplicates_set:
                        # It is unique, keep it
                        fname = os.path.basename(fpath)
                        dest = os.path.join(out_dir, fname)
                        if not self.dry_run:
                            shutil.copy2(fpath, dest)
            else:
                # MOVE DUPLICATES (In-Place)
                duplicates_dir = os.path.join(in_dir, "duplicates")
                if not os.path.exists(duplicates_dir) and not self.dry_run:
                    os.makedirs(duplicates_dir, exist_ok=True)
                    
                for fpath in dir_duplicates:
                    fname = os.path.basename(fpath)
                    dest = os.path.join(duplicates_dir, fname)
                    if not self.dry_run:
                        shutil.move(fpath, dest)

        # Summary
        kept = total_files - total_dupes
        rate = (kept / total_files * 100) if total_files > 0 else 0
        print("-" * 30)
        print(f"Deduplication Complete.")
        print(f"Total Frames: {total_files}")
        print(f"Duplicates:   {total_dupes}")
        print(f"Kept:         {kept} ({rate:.2f}%)")
        print("-" * 30)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Frame Deduplication Script")
    parser.add_argument("--input_dir", required=True, help="Path to input directory")
    parser.add_argument("--output_dir", default=None, help="Optional output directory for unique frames")
    parser.add_argument("--threshold", type=float, default=0.92, help="SSIM Threshold (default 0.92)")
    parser.add_argument("--resize_width", type=int, default=512, help="Width to resize images for comparison")
    parser.add_argument("--dry_run", action="store_true", help="Run without changes")
    
    args = parser.parse_args()
    
    deduplicator = FrameDeduplicator(
        source_dir=args.input_dir,
        output_dir=args.output_dir,
        threshold=args.threshold,
        resize_width=args.resize_width,
        dry_run=args.dry_run
    )
    deduplicator.run()
