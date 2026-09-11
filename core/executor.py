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
from dataclasses import dataclass
import os

@dataclass
class line_dataclass:
    """
    Used as a packet to neatly transfer data to the GUI console
    """
    type_t:bool #false: normal newline, true: carrige return
    data_t:str #The actual text in the line

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
            self.output_queue.put("[System]: A process is already running.")
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
            self.output_queue.put("[System]: Terminating process...")
            self._stop_event.set()
            try:
                self.process.terminate()
            except Exception as e:
                self.output_queue.put(f"[System]: Error terminating: {e}")

    def _worker(self, command: List[str], finished_callback: Optional[Callable[[int], None]]):
        """
            Called by run_command in a separate thread. Used to open a 
            subprocess and then scans the output to detect failures and 
            and stops the program if the E-Stop is pressed. It is not meant to 
            be called directly.
        """
        # Sets the os functions to non b
        
        read_pipe, write_pipe = os.pipe()
        os.set_blocking(read_pipe, False)
        
        try:
            self.output_queue.put(f"[System]: Starting command: {' '.join(command)}")
            
            # Using Popen to stream output
            
            self.process = subprocess.Popen(
                command,
                stdout=write_pipe,
                stderr=subprocess.STDOUT, # Redirect stderr to stdout
                text=False,
            )
            
            line = bytearray()
            
            prior_bit_bkslash_r = False #Used to test for \r vs \r\n bc windows uses \r\n instead of just \n for newlines
            
            # Reads output bit by bit to decipher carrige returns vs newlines
            while (1):
                try:
                    byte = os.read(read_pipe, 1)
                    if (byte == b'\r'):
                        if prior_bit_bkslash_r:   
                            console_packet = line_dataclass(type_t=True, data_t=line.decode("utf-8"))
                            self.output_queue.put(console_packet)
                            line.clear()
                        prior_bit_bkslash_r = True
                    elif (byte == b'\n'):
                        if prior_bit_bkslash_r:
                            prior_bit_bkslash_r == False
                        console_packet = line_dataclass(type_t=False, data_t=line.decode("utf-8"))
                        self.output_queue.put(console_packet)
                        line.clear()
                    elif(byte and byte != b''):
                        if prior_bit_bkslash_r:
                            prior_bit_bkslash_r = False
                            console_packet = line_dataclass(type_t=True, data_t=line.decode("utf-8"))
                            self.output_queue.put(console_packet)
                            line.clear()
                        line.extend(byte)
                    if(self._stop_event.is_set()):
                        if len(line) != 0:
                            self.output_queue.put(line.decode("utf-8"))
                        break
                except:   
                    if(not (self.process.poll() is None)): 
                        if len(line) != 0:
                            self.output_queue.put(line.decode("utf-8"))
                        break

            #closes the pipes for the subprocess stdout
            os.close(write_pipe) 
            os.close(read_pipe)
            
            return_code = self.process.wait()
            
            self.is_running = False
            
            self.output_queue.put(f"[System]: Process finished with return code {return_code}")
            
            if finished_callback:
                # Note: This calls callback in the WORKER thread. 
                # Tkinter updates must be scheduled via after() in the main thread if this callback touches GUI.
                finished_callback(return_code)

        except Exception as e:
            self.is_running = False
            self.output_queue.put(f"[System]: Error executing command: {str(e)}")
            if finished_callback:
                finished_callback(-1)
