# Create Subject Structure

This folder contains scripts to help automate the creation of folder structures for school subjects and their weekly content.

## Files

- **`create_single_subject.bat`**  
  A Windows batch script that prompts for a subject name and number of weeks, then creates a folder with subfolders named `01_WEEK`, `02_WEEK`, etc.

- **`create_multiple_subjects.py`**  
  A Python script that allows you to input multiple subjects. You can specify whether all subjects have the same number of weeks or different ones. It then generates a folder for each subject, with weekly subfolders in the same `XX_WEEK` format.


## Output Example
If you enter:

> Subject: Physics

> Weeks: 3

The following structure will be created:

```cmd
Physics/
├── 01_WEEK
├── 02_WEEK
└── 03_WEEK
```
## How to Use

1. Open a terminal or command prompt.

2. Navigate to this folder:
   ```cmd
   cd create-subject-structure
   ```
3. run
    ```cmd
    create_single_subject.bat
    ```
    or 

    ```cmd
    py create_multiple_subjects.py
    ```
