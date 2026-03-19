import os
import json
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime, timedelta

# ==========================================
# CLASS: FileEntry (Data Container)
# ==========================================
class FileEntry:
    """Represents a single file with its metadata."""
    def __init__(self, path, name, size, modified_date):
        self.path = path
        self.name = name
        self.size = size
        self.modified_date = modified_date

    def to_dict(self):
        return {
            "path": self.path,
            "name": self.name,
            "size": self.size,
            "modified_date": self.modified_date
        }

# ==========================================
# CLASS: FileIndexer (Scanning & Storage)
# ==========================================
class FileIndexer:
    def __init__(self):
        self.index_data = []
        self.index_file = "file_index.json"

    def scan_directory(self, root_dir):
        """Recursively scans directory and collects file info."""
        self.index_data = []
        count = 0
        errors = 0
        
        # Recursive scan using os.walk
        for dirpath, dirnames, filenames in os.walk(root_dir):
            for filename in filenames:
                try:
                    full_path = os.path.join(dirpath, filename)
                    stat = os.stat(full_path)
                    entry = FileEntry(
                        path=full_path,
                        name=filename,
                        size=stat.st_size,
                        modified_date=stat.st_mtime
                    )
                    self.index_data.append(entry)
                    count += 1
                except (OSError, PermissionError):
                    # Handle broken files or permission denied
                    errors += 1
                    continue
        
        return count, errors

    def save_to_json(self):
        data_to_save = [item.to_dict() for item in self.index_data]
        with open(self.index_file, 'w') as f:
            json.dump(data_to_save, f, indent=4)

    def load_from_json(self):
        if not os.path.exists(self.index_file):
            return []
        with open(self.index_file, 'r') as f:
            data = json.load(f)
        self.index_data = []
        for item in data:
            self.index_data.append(FileEntry(item['path'], item['name'], item['size'], item['modified_date']))
        return self.index_data

# ==========================================
# CLASS: SearchEngine (Logic & Filtering)
# ==========================================
class SearchEngine:
    def __init__(self, data):
        self.data = data

    def search(self, query, ext_filter, min_size, days_ago, sort_by):
        results = []
        now = time.time()
        seconds_in_day = 86400

        for item in self.data:
            # 1. Name Check
            name_match = query.lower() in item.name.lower()
            
            # 2. Extension Check
            ext_match = True
            if ext_filter:
                ext_match = item.name.lower().endswith(ext_filter.lower())
            
            # 3. Size Check
            size_match = item.size >= min_size
            
            # 4. Date Check (Modified within X days)
            date_match = True
            if days_ago > 0:
                time_diff = now - item.modified_date
                date_match = time_diff <= (days_ago * seconds_in_day)

            if name_match and ext_match and size_match and date_match:
                results.append(item)

        # 5. Sort
        if sort_by == "Name (A-Z)":
            results.sort(key=lambda x: x.name.lower(), reverse=False)
        elif sort_by == "Size (Largest)":
            results.sort(key=lambda x: x.size, reverse=True)
        elif sort_by == "Size (Smallest)":
            results.sort(key=lambda x: x.size, reverse=False)
        elif sort_by == "Date (Oldest)":
            results.sort(key=lambda x: x.modified_date, reverse=False)
        else: # Date (Newest)
            results.sort(key=lambda x: x.modified_date, reverse=True)

        return results

    def find_duplicates(self):
        """Finds files with identical name and size."""
        seen = {}
        duplicates = []
        
        for item in self.data:
            # Create a unique signature based on Name and Size
            signature = (item.name.lower(), item.size)
            if signature in seen:
                duplicates.append(item)
                # Also append the original match so user sees both
                if seen[signature] not in duplicates:
                    duplicates.append(seen[signature])
            else:
                seen[signature] = item
        
        # Sort duplicates by name
        duplicates.sort(key=lambda x: x.name.lower())
        return duplicates

# ==========================================
# CLASS: SearchApp (GUI)
# ==========================================
class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Search Indexer Pro")
        self.root.geometry("1000x700")

        self.indexer = FileIndexer()
        self.current_results = []
        self.page = 0
        self.results_per_page = 50

        self.setup_ui()

    def setup_ui(self):
        # --- TOP PANEL: Indexing ---
        top_frame = ttk.LabelFrame(self.root, text="1. Data Source")
        top_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(top_frame, text="Select Folder & Scan", command=self.run_scan).pack(side="left", padx=5, pady=5)
        ttk.Button(top_frame, text="Load Existing Index", command=self.load_index_only).pack(side="left", padx=5, pady=5)
        self.lbl_status = ttk.Label(top_frame, text="Status: No index loaded.", foreground="blue")
        self.lbl_status.pack(side="left", padx=10)

        # --- MIDDLE PANEL: Search ---
        search_frame = ttk.LabelFrame(self.root, text="2. Search & Filters")
        search_frame.pack(fill="x", padx=10, pady=5)

        # Row 0: Text Inputs
        ttk.Label(search_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.ent_search = ttk.Entry(search_frame, width=15)
        self.ent_search.grid(row=0, column=1, padx=5)

        ttk.Label(search_frame, text="Ext:").grid(row=0, column=2, padx=5)
        self.ent_ext = ttk.Entry(search_frame, width=8)
        self.ent_ext.grid(row=0, column=3, padx=5)

        ttk.Label(search_frame, text="Min Size (MB):").grid(row=0, column=4, padx=5)
        self.ent_size = ttk.Entry(search_frame, width=8)
        self.ent_size.grid(row=0, column=5, padx=5)
        self.ent_size.insert(0, "0")

        ttk.Label(search_frame, text="Modified (Days ago):").grid(row=0, column=6, padx=5)
        self.ent_days = ttk.Entry(search_frame, width=8)
        self.ent_days.grid(row=0, column=7, padx=5)
        self.ent_days.insert(0, "0") # 0 means all time

        ttk.Label(search_frame, text="Sort:").grid(row=0, column=8, padx=5)
        self.sort_var = tk.StringVar(value="Date (Newest)")
        sort_opts = ["Name (A-Z)", "Size (Largest)", "Size (Smallest)", "Date (Newest)", "Date (Oldest)"]
        ttk.OptionMenu(search_frame, self.sort_var, sort_opts[0], *sort_opts).grid(row=0, column=9, padx=5)

        # Row 1: Action Buttons
        btn_frame = ttk.Frame(search_frame)
        btn_frame.grid(row=1, column=0, columnspan=10, pady=10)
        
        ttk.Button(btn_frame, text="🔍 Search", command=self.run_search).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="📅 Recently Added", command=self.show_recent).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="👯 Find Duplicates", command=self.run_duplicate_finder).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🧹 Clear Filters", command=self.clear_filters).pack(side="left", padx=5)

        # --- BOTTOM PANEL: Results ---
        res_frame = ttk.LabelFrame(self.root, text="3. Results")
        res_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Treeview Columns
        columns = ("name", "size", "date", "path")
        self.tree = ttk.Treeview(res_frame, columns=columns, show="headings", selectmode="browse")
        
        self.tree.heading("name", text="File Name")
        self.tree.heading("size", text="Size")
        self.tree.heading("date", text="Modified Date")
        self.tree.heading("path", text="Full Path")
        
        self.tree.column("name", width=200)
        self.tree.column("size", width=100)
        self.tree.column("date", width=150)
        self.tree.column("path", width=400)

        # Scrollbar
        vsb = ttk.Scrollbar(res_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Pagination Footer
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Button(footer_frame, text="Previous", command=self.prev_page).pack(side="left", padx=5)
        self.lbl_page_info = ttk.Label(footer_frame, text="Page 1")
        self.lbl_page_info.pack(side="left", padx=5)
        ttk.Button(footer_frame, text="Next", command=self.next_page).pack(side="left", padx=5)
        
        self.lbl_stats = ttk.Label(footer_frame, text="Total Results: 0")
        self.lbl_stats.pack(side="right", padx=10)

    # --- LOGIC HELPER: Formatters ---
    @staticmethod
    def format_size(size_bytes):
        if size_bytes == 0: return "0 B"
        units = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(units)-1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.2f} {units[i]}"

    # --- LOGIC: Actions ---
    def run_scan(self):
        folder = filedialog.askdirectory()
        if not folder: return
        
        self.lbl_status.config(text="Scanning... Please wait.", foreground="orange")
        self.root.update()
        
        start_time = time.time()
        count, errors = self.indexer.scan_directory(folder)
        self.indexer.save_to_json()
        
        elapsed = time.time() - start_time
        msg = f"Done. Indexed {count} files in {elapsed:.2f}s."
        if errors > 0: msg += f" (Skipped {errors} errors)"
        
        self.lbl_status.config(text=msg, foreground="green")
        self.current_results = self.indexer.index_data
        self.page = 0
        self.render_results()

    def load_index_only(self):
        data = self.indexer.load_from_json()
        if data:
            self.lbl_status.config(text=f"Loaded {len(data)} files from JSON.", foreground="green")
            self.current_results = data
            self.page = 0
            self.render_results()
        else:
            messagebox.showerror("Error", "No index file found. Scan a folder first.")

    def run_search(self):
        if not self.indexer.index_data:
            self.load_index_only()
            if not self.indexer.index_data: return

        query = self.ent_search.get()
        ext = self.ent_ext.get()
        
        try:
            min_size_mb = float(self.ent_size.get())
            min_size_bytes = min_size_mb * 1024 * 1024
        except ValueError:
            min_size_bytes = 0

        try:
            days = int(self.ent_days.get())
        except ValueError:
            days = 0

        sort_mode = self.sort_var.get()

        engine = SearchEngine(self.indexer.index_data)
        self.current_results = engine.search(query, ext, min_size_bytes, days, sort_mode)
        
        self.page = 0
        self.render_results()

    def show_recent(self):
        # Shortcut: Just sort by date descending
        self.sort_var.set("Date (Newest)")
        self.ent_days.delete(0, tk.END)
        self.ent_days.insert(0, "30") # Last 30 days
        self.run_search()

    def run_duplicate_finder(self):
        if not self.indexer.index_data:
            self.load_index_only()
            if not self.indexer.index_data: return

        engine = SearchEngine(self.indexer.index_data)
        self.current_results = engine.find_duplicates()
        self.page = 0
        
        self.lbl_status.config(text="Showing duplicate files (Same Name & Size).", foreground="purple")
        self.render_results()

    def clear_filters(self):
        self.ent_search.delete(0, tk.END)
        self.ent_ext.delete(0, tk.END)
        self.ent_size.delete(0, tk.END)
        self.ent_size.insert(0, "0")
        self.ent_days.delete(0, tk.END)
        self.ent_days.insert(0, "0")

    # --- PAGINATION LOGIC ---
    def render_results(self):
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.current_results:
            self.lbl_stats.config(text="No results found.")
            self.lbl_page_info.config(text="Page 0/0")
            return

        # Calculate slice
        start_idx = self.page * self.results_per_page
        end_idx = start_idx + self.results_per_page
        page_data = self.current_results[start_idx:end_idx]

        # Populate Tree
        for r in page_data:
            date_str = datetime.fromtimestamp(r.modified_date).strftime('%Y-%m-%d %H:%M:%S')
            size_str = self.format_size(r.size)
            self.tree.insert("", "end", values=(r.name, size_str, date_str, r.path))

        # Update Footer Stats
        total = len(self.current_results)
        max_page = (total - 1) // self.results_per_page
        self.lbl_page_info.config(text=f"Page {self.page + 1} / {max_page + 1}")
        self.lbl_stats.config(text=f"Showing {len(page_data)} of {total} results")

    def next_page(self):
        max_page = (len(self.current_results) - 1) // self.results_per_page
        if self.page < max_page:
            self.page += 1
            self.render_results()

    def prev_page(self):
        if self.page > 0:
            self.page -= 1
            self.render_results()

# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    root = tk.Tk()
    # Try to set a modern theme
    try:
        style = ttk.Style()
        style.theme_use('clam') 
    except:
        pass
    
    app = SearchApp(root)
    root.mainloop()