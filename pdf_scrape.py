import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from tkinter import filedialog, Scrollbar, HORIZONTAL,Text, VERTICAL, RIGHT, BOTTOM, X, Y, BOTH, LEFT,TOP
import PyPDF2
import os
import re

def add_pdf():
    filename = filedialog.askopenfilename(initialdir="/", title="Select File",
                                          filetypes=(("pdf files", "*.pdf"), ("all files", "*.*")))
    if filename:
        pdf_label.config(text=os.path.basename(filename))
        global pdf_path
        pdf_path = filename

def search_pdf():
    search_string = search_entry.get()
    if pdf_path and search_string:
        search_string_in_pdf(pdf_path, search_string)

def search_string_in_pdf(pdf_filename, search_string):
    with open(pdf_filename, 'rb') as file:
        reader = PyPDF2.PdfReader(file)

        page_number = 0
        line_count = 0
        string_count = 0
        results_text.delete('1.0', tk.END)  # Clear previous results

        # Prepare the regular expression for whole word match
        word_regex = r'\b' + re.escape(search_string) + r'\b'

        for page in reader.pages:
            page_number += 1
            text = page.extract_text()

            if text:
                lines = text.splitlines()

                for line in lines:
                    if re.search(word_regex, line, re.IGNORECASE):
                        line_count += 1
                        string_count += 1
                        results = f" { line_count}. {line} -- Page {page_number}\n"
                        results_text.insert(tk.END, results)
        
        if string_count == 0:
            results_text.insert(tk.END, "No such string found")

# Setting up the main window
root = TkinterDnD.Tk()
root.title("PDF Text Search")

def drop(event):
    file = event.data
    if file.endswith('.pdf'):
        pdf_label.config(text=os.path.basename(file))
        global pdf_path
        pdf_path = file

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)

# Globals
pdf_path = ""

# PDF Selection
pdf_frame = tk.Frame(root)
pdf_frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=10)
pdf_label = tk.Label(pdf_frame, text="No PDF selected", fg="blue")
pdf_label.pack(side=tk.LEFT)
pdf_button = tk.Button(pdf_frame, text="Select PDF", command=add_pdf)
pdf_button.pack(side=tk.LEFT)

# Search Box and Button
search_frame = tk.Frame(root)
search_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10)
search_entry = tk.Entry(search_frame, width=50)
search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
search_button = tk.Button(search_frame, text="Search", command=search_pdf)
search_button.pack(side=tk.LEFT)


# Results Display with Scrollbars
results_frame = tk.Frame(root)
results_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

results_text = Text(results_frame, wrap="none")
results_text.grid(row=0, column=0, sticky="nsew")
results_frame.grid_rowconfigure(0, weight=1)
results_frame.grid_columnconfigure(0, weight=1)

v_scroll = Scrollbar(results_frame, orient=VERTICAL, command=results_text.yview)
v_scroll.grid(row=0, column=1, sticky="ns")
results_text.config(yscrollcommand=v_scroll.set)

h_scroll = Scrollbar(root, orient=HORIZONTAL, command=results_text.xview)
h_scroll.grid(row=3, column=0, sticky="ew")
results_text.config(xscrollcommand=h_scroll.set)

# Run the application
root.mainloop()
