# Video Preprocessing Pipeline

This repository contains a GUI-driven pipeline for video preprocessing, frame extraction, and preparation for Gaussian Splatting workflows.

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

## Adding your own scripts:
One of the main goals of this project is to give it the flexibility to run other people's scripts. While possible, this currently takes a tremendous amount of effort because the code's largely undocumented. If you still want to try adding your own scripts, you can look at the documentation that does exist [here](/documentation/full_documentation.md#full-documentation). 

Future work hopes to create a plugin .json structure that would allow for fully custom scripts to be added, but that has yet to be added