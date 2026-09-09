"""
    The executor takes in the commands passed by the pipeline manager, asyncronously executes them, 
and captures their stderr, stdout output. In other words, the executor is the script that actualy 
runs all the other scripts

"""
import io
import subprocess
import threading
import queue
import sys
from typing import List, Callable, Optional

class AsyncExecutor:
    """Handles execution of shell commands in a background thread.
    
    The AsyncEcecutor is the main execution class for the backend. The
    class takes in a queue for the stderr and stdout pipes and 
    Pipes stdout/stderr to a queue for the GUI to consume.
    """
    def __init__(self, output_queue: queue.Queue):
        self.output_queue = output_queue
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self._stop_event = threading.Event()

    def run_command(self, 
                    command: List[str], 
                    finished_callback: Optional[Callable[[int], None]] = None):
        """
        Starts the secondary application in a separate thread.
        args:
            command: List of command arguments (e.g., ['python', 'script.py', '--arg'])
            finished_callback: Function to call when process ends (receives return_code)
        """
        if self.is_running:
            self.output_queue.put("[System]: A process is already running.\n")
            return

        self.is_running = True
        self._stop_event.clear()
        
        thread = threading.Thread(
            target=self._worker, 
            args=(command, finished_callback), 
            daemon=True
        )
        thread.start()

    def stop(self):
        """Terminates the current process."""
        if self.process and self.is_running:
            self.output_queue.put("[System]: Terminating process...\n")
            self._stop_event.set()
            try:
                self.process.terminate()
            except Exception as e:
                self.output_queue.put(f"[System]: Error terminating: {e}\n")

    def _worker(self, command: List[str], finished_callback: Optional[Callable[[int], None]]):
        """
            Called by run_command in a separate thread. Used to open a 
            subprocess and then scans the output to detect failures and 
            and stops the program if the E-Stop is pressed. It is not meant to 
            be called directly.
        """
        try:
            self.output_queue.put(f"[System]: Starting command: {' '.join(command)}\n")
            
            # Using Popen to stream output
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Redirect stderr to stdout
                text=True,
                bufsize=1, # Line buffered
                universal_newlines=True
            )

            # Read output line by line
            for line in iter(self.process.stdout.readline, ''): # type: ignore
                if self._stop_event.is_set():
                    break
                if line:
                    self.output_queue.put(line)
            
            self.process.stdout.close()  # type: ignore
            return_code = self.process.wait()
            
            self.is_running = False
            
            self.output_queue.put(f"[System]: Process finished with return code {return_code}\n")
            
            if finished_callback:
                # Note: This calls callback in the WORKER thread. 
                # Tkinter updates must be scheduled via after() in the main thread if this callback touches GUI.
                finished_callback(return_code)

        except Exception as e:
            self.is_running = False
            self.output_queue.put(f"[System]: Error executing command: {str(e)}\n")
            if finished_callback:
                finished_callback(-1)
