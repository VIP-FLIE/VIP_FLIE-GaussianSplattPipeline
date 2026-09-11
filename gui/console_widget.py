import tkinter as tk
from tkinter import scrolledtext
import queue
from .style import consoleColor, toolbarColor, normalTextColor, consoleError, consoleNormal, consoleWarning
from core.executor import line_dataclass
from dataclasses import dataclass

class ConsoleWidget(tk.Frame):
    """
    A unified Output Console.
    Polls a thread-safe Queue to update the text widget.
    """
    def __init__(self, parent: tk.Widget, output_queue: queue.Queue, poll_interval_ms: int = 100):
        super().__init__(parent)
        self.configure(background=consoleColor)
        self.output_queue = output_queue
        self.poll_interval_ms = poll_interval_ms
        self.current_text_column = 1
        self.carrige_return_for_next_line_b = False
        
        # UI Setup
        self.text_area = scrolledtext.ScrolledText(self, state='disabled', height=10, 
                                                   background=consoleColor, foreground=normalTextColor)
        #TODO: Fix scrollbar coloring
        #self.text_area.vbar.configure(troughcolor=consoleScrollcolor)
        self.text_area.tag_config("Manager Error", foreground=consoleError)
        self.text_area.tag_config("Manager Warning", foreground=consoleWarning)
        self.text_area.tag_config("Manager", foreground=consoleNormal)

        self.text_area.pack(fill='both', expand=True)
        self.text_area.config(state="normal")
        self.text_area.delete("1.0", "end")
        self.text_area.see(tk.END)
        self.text_area.config(state="disabled")

        # Start Polling
        self.after(self.poll_interval_ms, self._poll_queue)

    def _poll_queue(self):
        """Checks for new messages in the queue."""
        try:
            while True:
                # Get all available messages (non-blocking)
                text = self.output_queue.get_nowait()
                if (self.carrige_return_for_next_line_b):
                    self._carrige_return(self.text_area)
                    self.carrige_return_for_next_line_b = False
                if (type(text) == str):
                    self._append_text(text, self.text_area)
                else :
                    self._append_text(text.data_t, self.text_area)
                    if (text.type_t):
                        self.carrige_return_for_next_line_b = True
                self.output_queue.task_done()
        except queue.Empty:
            pass
        finally:
            # Reschedule poll
            self.after(self.poll_interval_ms, self._poll_queue)

    def _append_text(self, text: str, text_area):
        text_area.config(state='normal')
        print(text)
        print(self.current_text_column)
        text_area.insert(tk.END, text +"\n")
        if '[Manager Error]:' in text:
            index = text.find('[Manager Error]:')
            text_area.tag_add("Manager Error",
                                str(self.current_text_column)+'.'+str(index),
                                str(self.current_text_column)+'.'+str(index+16))
        if '[Manager WARNING]:' in text:
            index = text.find('[Manager WARNING]:')
            self.text_area.tag_add("Manager Warning",
                                    float(str(self.current_text_column)+'.'+str(index)),
                                    float(str(self.current_text_column)+'.'+str(index+18)))
        if '[Manager]:' in text:
            index = text.find('[Manager]:')
            self.text_area.tag_add("Manager",
                                    str(self.current_text_column)+'.'+ str(index),
                                    str(self.current_text_column)+'.'+ str(index+10))
        if '[System]:' in text:
            index = text.find('[System]:')
            self.text_area.tag_add("Manager",
                                    str(self.current_text_column)+'.'+ str(index),
                                    str(self.current_text_column)+'.'+ str(index+9))
        self.current_text_column += 1
        
            
        
        self.text_area.see(tk.END) # Auto-scroll
        
        self.text_area.config(state='disabled')
      
    def _carrige_return(self, text_area):
            text_area.config(state='normal')
            text_area.delete("end -2 lines", "end")
            text_area.insert(tk.END,"\n")
            for tag in text_area.tag_names():
                text_area.tag_remove(tag, str(self.current_text_column)+".0", str(self.current_text_column)+".end")
            self.current_text_column -= 1
            text_area.config(state='disabled')
