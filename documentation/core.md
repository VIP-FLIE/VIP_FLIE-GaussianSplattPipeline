# __Core__

The core is where most of the backend lives (although the core and GUI are fairly tightly integrated).
The category section hosts five scripts:

* [__category.py__](#categorypy)
* [__command_builders.py__](#command_builderspy)
* [__executor.py__](#executorpy)
* [__pipeline_manager.py__](#pipeline_managerpy)
* [__state_models.py__](#state_modelspy)

Each script and its component classes are described in greater detail below

</br>

## Category.py


The category script contains the classes used to create the categories that each script is contained in.
This ensures that steps are executed in the correct order, as well as enforcing exclusivity when two scripts of the same type can't be run together.

#### SelectionMode(Enum):
<div style="padding-left: 30px;">

_Description_:
<div style="padding-left: 30px;">

Selection mode is used to define the selection type for a category when creating a pipeline category.  
</div>

_Modes_  <div style="padding-left: 30px;">

__SINGLE__: Prevents another section from the same category being loaded into the pipeline  
__MULTI__: Allows you to load as many sections as you want from that category into the pipeline

</div>
</div>

#### PipelineCategory:

<div style="padding-left: 30px;">

_Description_: <div style="padding-left: 30px;"> PipelineCategory is used by main to initialize a new category for adding sections to.</div>

_Methods_:
<div style="padding-left: 30px;">

__\_\_init\_\___:

* name(str): 
    * The name\\title  of the category.
* selection_mode(SelectionMode):
    * The [selection mode](#selectionmodeenum) used by the category.

* stage_index(int):
    * The unique index of the stage in exectution order. This is used to order the stages in the ui and in the backend when executing.

__add\_section__:

* section(PipelineSection):
    * Used to add the sections into the category. See how to define a pipeline section [here](\sections.md#pipelinesection).
</div>

</div>

<br>

## Command_builders.py

Command Builders are used to take in the inputs from the gui and synthesize them into command line
arguments to be run by the executor. All the command builders for the included scrips are housed here, although they are not requiered to, so long as they can be called by the build method of their respective pipeline section. You can read more on that [here](/sections.md#pipelinesection).

Documentation on how to build your own command builder will be written later. For now, you have to reference the existing builders to see how they work if you want to.

</br>

## Executor.py

The executor takes in the commands passed by the [pipeline manager](#pipeline_managerpy), asyncronously executes them, and captures their stderr, stdout output. In other words, the executor is the script that actualy runs all the other scripts.

#### AsyncExecutor:

<div style="padding-left: 30px;">

_Description_: <div style="padding-left: 30px;">
Class containing all the executor code/methods</div>

_Methods_:<div style="padding-left: 30px;">
__\_\_init\_\___: Initializes the executor
* output_queue(queue.Queue):
  * The queue used to pass stdout, stderr outputs to the console in the GUI.

__run\_command__: Executes the provided script

* command( List[str] ):
  * The list containing the command to be run by the executor

* finished_callback( Optional[Callable[[int], None]] ):
  * Callback function for after a command runs. (Optional)

__stop__: prematurely kills the execution of a script

__\_worker__: Used by the run_command method to open a new process in a new thread for execution. Not advised to be called directly.
</div>

</div>

</br>

## Pipeline_manager.py

The pipeline manager is the center of the backend. 

#### PipelineManager

<div style="padding-left: 30px;">

_Description_: <div style="padding-left: 30px;">
Class containing all the code/methods for the manager</div>

_Methods_:<div style="padding-left: 30px;">
__\_\_init\_\___: Initializes the class on creation
* config(PipelineConfiguration):
  * The class used to store all the config settings for the different sections. For more information see the [state models](#state_modelspy) section.

* executor(AsyncExecutor):
  * The executor that will be used to run the scripts. For information on defining an executor, see the [executor.py](#executorpy) section.

__add\_staging\_listener__:

__\_notify\_staging\_changed__: Triggers all the calbacks added to the staging listener

__add\_category__: Adds a new PipelineCategory
* category(PipelineCategory)
  * The pipeline category object to be added. For more information on defining a category, see the [category.py](#categorypy) section.

__toggle\_section\_stage__: toggles a section(script) and enforces single mode if needed

__\_validate\_movement__: Ensures the movement is valled when calling move_staged_item
* index(int)
  * the index of the section attempting to be moved
* direction(int)
  * the direction the section is attempting to move. 

__move\_staged\_item__: Moves a section up or down. Returns True if moved or false if not
* index(int)
  * the index of the object being moved
* direction(int)
  * the direction its moving. Up is -1 and down is +1

__\_find\_category\_for\_section__: Returns the category of the current section
* section(pipelineSection)
  * The section to be evaluated

__run\_sequence__: Runs the currently loaded sequence of sections
* settings(dict)
  *  all the configued settings for the scripts + the input output and program paths

__\_validate_order__: Ensures all the steps are in order before running everything. Returns true if everything is correct

__\_validate\_pipeline\_environment__: Checks the in and out paths to make sure they exist and are write-able

__\_run\_next\_in\_sequence__: Sets up and calls the executor for the next step in the sequence. Calls \_on\_sequence\_step\_finished firectly after completion

__\_on\_sequence\_step\_finished__: Checks if the prior step in the sequence completed correctly. If it did, it cues the next step. If not it aborts and spits out an error to the console 

__\_notify\_status__: changes the status of the status event

__stop\_sequence__: stops the currently running async executor

</div>
</div>

</br>

## State_models.py
The state models store information that needs to be globaly accessed between the gui and the backend. This allows for fewer arguments to be passed between functions.

### GlobalContext
Initializes a set of globaly accesable variables for the program as a whole. 
* project_root (str)
* input_video_path (str)
* input_dir (str)
* output_dir (str)

### PipelineConfiguration
Initialises the GlobalContext as well as the section_settings, which are used to store the user provided settigns for each section (script)