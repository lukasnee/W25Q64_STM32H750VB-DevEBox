#!/usr/bin/env python3
import os
import subprocess

def format_file(file_path):
    try:
        subprocess.run(['clang-format', '-i', file_path], check=True)
        print(f"Formatted: {file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to format: {file_path}")
        print(e)

def format_core_folder(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            format_file(file_path)

if __name__ == "__main__":
    core_folder_path = "Core"
    format_core_folder(core_folder_path)