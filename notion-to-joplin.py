#!/usr/bin/env python3
# This script is used to convert a Notion export to a Joplin import (MD - Markdown directory).
# Step 1: Get the notion export zip file
# Step 2: Unzip the notion export zip file
# Step 3: Rename every file with a .md extension with the heading of the file and fix all the links
# Step 4: Rename all folder. Remove the "hash" from the ending of the folder name and fix all the links

from argparse import ArgumentParser
import sys
import zipfile
import glob
import shutil
from os import path
import ntpath
import urllib.parse
import re

# VARIABLES
FOLDER_EXTRACTION = "L:/NOTION/exporten/krt4"
MARKDOWN_EXTENSION = "md"
filename_backup = ""

# New version sanitizing filenames:
def sanitize_filename(name: str, replacement: str = "_") -> str:
    """
    Sanitize a filename for Windows:
    - Replace invalid characters: < > : " / \ | ? *
    - Remove control chars
    - Strip leading/trailing spaces and dots
    """
    # Replace invalid Windows filename characters
    invalid_chars = r'[<>:"/\\|?*]'
    cleaned = re.sub(invalid_chars, replacement, name)

    # Remove control characters (0–31)
    cleaned = "".join(ch for ch in cleaned if ord(ch) >= 32)

    # Strip leading/trailing spaces and dots
    cleaned = cleaned.strip(" .")

    # Fallback if everything got stripped
    return cleaned or "untitled"

path_to_files = path.join(FOLDER_EXTRACTION, "**/*." + MARKDOWN_EXTENSION)

# Step 1: Rename all files and store the mapping
file_mapping = {}  # To store old filename and new filename mappings
for filename in glob.iglob(path_to_files, recursive=True):
    # Get the heading of the file
    with open(filename, "r", encoding="utf-8") as file:
        first_line = file.readline()
        heading = (
            first_line.replace("# ", "")
            .replace("\n", "")
            .replace("/", "-")
        )
        heading = sanitize_filename(heading)

        # Delete two first lines
        lines = file.readlines()
        lines_without_heading = lines[1:]

    # Write the file without the heading
    with open(filename, "w", encoding="utf-8") as file:
        file.write("".join(lines_without_heading))

    # Rename the file
    new_filename = path.join(
        path.dirname(filename),
        heading + "." + MARKDOWN_EXTENSION,
    )
    shutil.move(filename, new_filename)

    # Print the current file being saved
    print(f"File saved: {new_filename}")

    # Store the old and new filenames for later link fixing
    old_filename_encoded = urllib.parse.quote(ntpath.basename(filename))
    new_filename_encoded = urllib.parse.quote(ntpath.basename(new_filename))
    file_mapping[old_filename_encoded] = new_filename_encoded

# Step 2: Fix all the links in all files
for filename_to_fix in glob.iglob(path_to_files, recursive=True):
    with open(filename_to_fix, "r", encoding="utf-8") as file:
        lines_to_fix = file.readlines()

    # Replace all old filenames with new filenames in the content
    text_to_write = "".join(lines_to_fix)
    for old_filename_encoded, new_filename_encoded in file_mapping.items():
        text_to_write = text_to_write.replace(old_filename_encoded, new_filename_encoded)

    # Write back the updated content
    with open(filename_to_fix, "w", encoding="utf-8") as file:
        file.write(text_to_write)

print("Renaming files and fixing links done.")

path_of_folders = r"L:/NOTION/exporten/krt4/**/"
# path_to_files   = "..."  # your pattern for files to fix, e.g. r"L:/NOTION/exporten/krt3/**/*.html"

for folder in glob.iglob(path_of_folders, recursive=True):
    if os.path.isdir(folder):
        folder = folder.rstrip("\\/")          # remove trailing slashes/backslashes
        current_folder_name = os.path.basename(folder)
        new_folder_name = " ".join(current_folder_name.split(" ")[:-1])

        # If there is no "last word" to remove, skip
        if not new_folder_name:
            continue

        new_folder_path = os.path.join(os.path.dirname(folder), new_folder_name)

        # Skip if the destination already exists
        if os.path.exists(new_folder_path):
            print(f"Skipping rename: {folder} → {new_folder_path} (already exists)")
            continue

        # Rename the folder
        shutil.move(folder, new_folder_path)

        # Fix all the links
        old_folder_name_encoded = urllib.parse.quote(current_folder_name)
        new_folder_name_encoded = urllib.parse.quote(new_folder_name)

        for filename_to_fix in glob.iglob(path_to_files, recursive=True):
            if not os.path.isfile(filename_to_fix):
                continue
            with open(filename_to_fix, "r", encoding="utf-8") as file:
                text = file.read()
            new_text = text.replace(old_folder_name_encoded, new_folder_name_encoded)
            if new_text != text:
                with open(filename_to_fix, "w", encoding="utf-8") as file:
                    file.write(new_text)

