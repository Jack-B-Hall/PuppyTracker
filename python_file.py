import os
import sys

def export_py_files(directory='.', exclude_dirs=None):
    """
    Recursively scans the specified directory for .py files, excluding specified directories,
    and writes each filename along with its contents to an output text file.
    
    Parameters:
        directory (str): The root directory to start scanning from. Defaults to the current directory.
        exclude_dirs (list): A list of directory names to exclude from scanning. Defaults to ['streaming_client', 'logs'].
    """
    if exclude_dirs is None:
        exclude_dirs = ['streaming_client', 'logs']
    
    output_file = "exported_py_files.txt"
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        for root, dirs, files in os.walk(directory):
            # Modify dirs in-place to skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for filename in files:
                if filename.endswith('.py'):
                    file_path = os.path.join(root, filename)
                    outfile.write(f"File: {file_path}\n")
                    outfile.write("-" * 80 + "\n")
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as infile:
                            contents = infile.read()
                            outfile.write(contents)
                    except Exception as e:
                        outfile.write(f"Error reading file: {e}\n")
                    
                    outfile.write("\n" + "=" * 80 + "\n\n")
    
    print(f"Export complete: {output_file}")

if __name__ == '__main__':
    # Use the first command line argument as the directory, or default to '.'
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    export_py_files(directory)
