import os, argparse
import subprocess


if __name__ == '__main__':
    # Initialize the parser
    parser = argparse.ArgumentParser(description="A simple argument parser")

    # Add arguments
    parser.add_argument("-exe", "--executable")
    parser.add_argument("-i", "--input") 
    parser.add_argument("-o", "--output") 
    parser.add_argument("-m", "--metashape_output") 
    parser.add_argument("-n", "--name")

    # Parse the arguments
    args = parser.parse_args()

    if not args.executable:
        raise TypeError("Error, no Metashape .exe provided")
    elif not args.input:
        raise TypeError("Error, no input dir provided")
    elif not args.output:
        raise TypeError("Error, no ouput dir provided for the colmap data")
    elif not args.metashape_output:
        raise TypeError("Error, no output dir provided for the metashape file")
    elif not args.name:
        raise TypeError("Error, no output file naming convention")
    
    # base_dir is project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    #path to metashape_script.py
    script_path = str(os.path.join(base_dir, "scripts", "metashape_script.py"))


    
    command = f'"{args.executable}" -r "{script_path}" -i "{args.input}" -o "{args.output}" -m "{args.metashape_output}" -n "{args.name}"'
    process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT, # Redirect stderr to stdout
                text=True,
                bufsize=1, # Line buffered
                universal_newlines=True
            )
    
    # Read output line by line
    for line in iter(process.stdout.readline, ''): # pyright: ignore[reportOptionalMemberAccess]
        print(line)

    process.stdout.close() # pyright: ignore[reportOptionalMemberAccess]
    process.wait()