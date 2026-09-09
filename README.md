# Gausian Splatt Pipeline

Developed for the [VIP:Drones](https://vip.udel.edu/project/drone/) team at the University of Delaware, the Gausian Splatt Pipeline is a GUI for Gaussian Splatting workflows. The program seeks to eliminate the the need for human intervention when going from video all the way to finished splat

## Current Program Support
The pipeline currently supports the following
<div style="padding-left: 10px;line-height: .5;">

  • Video Frame Extraction

  • Sharpness Based Image Culling

  • Frame Deduplication

  • Metashape Image Allignment

  • Brush Based Splat Training
  
</div>
 

## Setup Instructions

To set up the project locally, follow these steps:

### 1. Create a Virtual Environment

It is recommended to use a virtual environment to manage dependencies:

```bash
python -m venv .venv
```

### 2. Activate the Virtual Environment

- **macOS/Linux**:
  ```bash
  source .venv/bin/activate
  ```
- **Windows**:
  ```bash
  .venv\Scripts\activate
  ```

### 3. Install Dependencies

Install the required packages using `pip`:

```bash
pip install -r requirements.txt
```

### 4. Run the Application

Execute the main script to start the GUI:

```bash
python main.py
```
## Documentation
For documentation of the code and all its components, you can either go into the documents folder and explore on your own or start at the high level overview [here](/documentation/high_level_overview.md). 


## Adding your own scripts:
One of the main goals of this project is to give it the flexibility to run other people's scripts. While possible, this currently takes a tremendous amount of effort because of the code's largely undocumented state. If you still want to try adding your own scripts, you can look at the documentation that does exist [here](/documentation/full_documentation.md). 

Future work hopes to create a plugin .json structure that would allow for fully custom scripts to be added, but that has yet to be implemented