import os
import shutil
from pathlib import Path

def copy_file_to_new_dir(source_path:Path, target_path:Path):
    # Check if the input file exists
    if not os.path.exists(source_path):
        raise ValueError(f"Source file '{source_path}' does not exist.")
    else:
        # extract file name from source path and remove file extension
        file_name = os.path.splitext(os.path.basename(source_path))[0]
        # create new directory path
        new_dir_path:Path = Path(f"{target_path}/{file_name}")
        # Use the os module to create the new directory
        os.makedirs(new_dir_path, exist_ok=True)

        # Use the shutil module to copy the file to the new directory
        new_file_path = os.path.join(new_dir_path, f"source_{file_name}.png")
        shutil.copy(source_path, new_file_path)

        # Return the path to the new directory as a Path object
        return Path(new_dir_path)
