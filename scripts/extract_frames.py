import os
import cv2
import argparse
from glob import glob
from pathlib import Path

class FrameExtractor:
    def __init__(self, source_path, output_dir, output_format="jpg", every_n=1, dry_run=False):
        """
        Initialize the FrameExtractor.
        
        Args:
            source_path (str): Path to a video file OR a directory containing videos.
            output_dir (str): Path to the root directory to save extracted frames.
            output_format (str): Image format (e.g., 'jpg', 'png').
            every_n (int): Extract every Nth frame.
            dry_run (bool): If True, simulate actions without writing files.
        """
        self.source_path = str(source_path)
        self.output_dir = str(output_dir)
        self.output_format = output_format.lstrip('.')
        self.every_n = max(1, int(every_n))
        self.dry_run = dry_run
        
        # Supported video extensions
        self.video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.flv', '*.wmv']

    def _get_video_files(self):
        """Resolves source_path to a list of video files."""
        if os.path.isfile(self.source_path):
            return [self.source_path]
        
        elif os.path.isdir(self.source_path):
            videos = []
            for ext in self.video_extensions:
                # Case insensitive search would be better, but glob is case-sensitive on Linux/Mac usually.
                # We'll just checks lower and upper for now to be safe, similar to other scripts.
                videos.extend(glob(os.path.join(self.source_path, ext)))
                videos.extend(glob(os.path.join(self.source_path, ext.upper())))
            return sorted(list(set(videos))) # Sort and unique
        else:
            print(f"Error: Input path does not exist: {self.source_path}")
            return []

    def _extract_from_video(self, video_path, destination_dir):
        """Extracts frames from a single video file."""
        
        # Safety Check: Input dir != Output dir
        # We check if the destination directory is the same as where the video lives
        if os.path.abspath(destination_dir) == os.path.abspath(os.path.dirname(video_path)):
            print(f"Error: Output directory cannot be the same as input directory for {video_path}")
            return

        if not self.dry_run:
            os.makedirs(destination_dir, exist_ok=True)

        print(f"Processing: {os.path.basename(video_path)} -> {destination_dir}")
        if self.every_n > 1:
            print(f"  Strategy: Extracting every {self.every_n}th frame.")
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            return

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        print(f"  Total Frames detected: {total_frames}")

        frame_count = 0
        saved_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Selection Strategy
            if frame_count % self.every_n == 0:
                output_filename = f"frame_{frame_count:06d}.{self.output_format}"
                output_path = os.path.join(destination_dir, output_filename)
                
                if self.dry_run:
                    # Verbose only for first few to minimize noise
                    if saved_count < 3:
                        print(f"  [PREDICTION] Would write: {output_path}")
                else:
                    success = cv2.imwrite(output_path, frame)
                    if not success:
                        print(f"  Error writing frame {frame_count}")
                saved_count += 1
            
            frame_count += 1

        cap.release()
        print(f"  Extracted {saved_count} frames.")

    def run(self):
        print(f"--- Starting Frame Extraction ---")
        print(f"Input: {self.source_path}")
        print(f"Output Root: {self.output_dir}")
        
        video_files = self._get_video_files()
        
        if not video_files:
            print("No video files found.")
            return

        print(f"Found {len(video_files)} video(s) to process.")

        is_batch_mode = len(video_files) > 1 or os.path.isdir(self.source_path)

        for video_path in video_files:
            # Determine specific output directory
            if is_batch_mode:
                # Batch mode: create subdirectory named after the video file
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                target_dir = os.path.join(self.output_dir, video_name)
            else:
                # Single file mode: output directly to requested dir
                target_dir = self.output_dir
            
            self._extract_from_video(video_path, target_dir)

        print("-" * 30)
        print("Extraction pipeline complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Video Frame Extraction Script")
    parser.add_argument("--input_dir", required=True, help="Path to video file OR directory containing videos")
    parser.add_argument("--output_dir", required=True, help="Directory to save extracted frames")
    parser.add_argument("--format", type=str, default="png", help="Output image format (jpg, png, bmp, etc.)")
    parser.add_argument("--every_n", type=int, default=1, help="Extract every Nth frame (default: 1)")
    parser.add_argument("--dry_run", action="store_true", help="Simulate without writing files")
    
    args = parser.parse_args()
    
    extractor = FrameExtractor(
        source_path=args.input_dir,
        output_dir=args.output_dir,
        output_format=args.format,
        every_n=args.every_n,
        dry_run=args.dry_run
    )
    extractor.run()
