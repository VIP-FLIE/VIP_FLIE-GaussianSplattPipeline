# High Level Overview
### Startup:  
<div style="padding-left: 30px;">

When launching main.py, the program first creates objects for all of the major components: 
* An Output Queue for thread safe capture of stdout and stderr when running scripts 

* An Executor for running the scripts asyncronously

* A Config for storing information about the current state of everything in the GUI for easy retrieval

* A Manager for coordinating all of this with the gui

The program then loads all the categories and the scripts(called sections), before launching the main GUI 
</div>

### The Core
<div style="padding-left: 30px;">

The core is where most of the backend lives. The UI makes calls to the backend objects whenever the user interacts with the program.

</div>

### The GUI
<div style="padding-left: 30px;">
This is where the code for the main window lives. It sets up everything using Tkinter and ties the GUI callbacks to backend functions/object methods. It also is where the settings and paths windows are launched from
</div>

### Sections
<div style="padding-left: 30px;">
Sections are how you define the configurable settings for each script along with their defaults. All of the sections derive from the base section abstactclass.
</div>