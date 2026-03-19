File Search Indexer
A robust, Object-Oriented desktop application built with Python and Tkinter designed to index local file systems and perform fast, advanced searches.

 Features
Recursive Scanning: Traverses all subdirectories to build a complete index of the file system.
Fast Search Engine: Instantly query files by name or extension.
Advanced Filtering: Filter results by file size (MB) and modification date (e.g., "files changed in the last 7 days").
Sorting Options: Sort results by Name (A-Z), Size (Largest/Smallest), or Date (Newest/Oldest).
Duplicate Detection: Built-in tool to identify potential duplicate files based on name and size.
Pagination: Handles large datasets (1000+ files) efficiently with Next/Previous navigation.
Data Persistence: Saves the file index to file_index.json for instant loading without re-scanning.
User-Friendly GUI: Clean, modern interface built with Tkinter.
 Installation
This project uses only the Python Standard Library. No external packages or pip install commands are required.

Ensure you have Python 3.6 or higher installed.
Clone or download this repository to your local machine.
 Usage
Open your terminal or command prompt in the project folder.
Run the application:
python main.py
To Start: Click "Select Folder & Scan" and choose a directory (e.g., your Documents or Downloads folder).
To Search: Enter a file name or extension (e.g., .pdf) and click "Search".
To Filter: Use the "Min Size" or "Days Ago" fields to narrow down results.
To Find Duplicates: Click the " Find Duplicates" button to scan for copies of files.
Pagination: Use the Next/Previous buttons at the bottom to browse large result sets.

Technical Implementation (OOP)
The code is structured using Object-Oriented Programming (OOP) principles to ensure maintainability and scalability:

FileEntry: A data class representing a single file (encapsulating Path, Name, Size, and Date).
FileIndexer: Handles the recursive scanning logic and JSON serialization/deserialization.
SearchEngine: Encapsulates the business logic for filtering, sorting, and finding duplicates.
SearchApp: Manages the Tkinter GUI, user input, and event handling.
