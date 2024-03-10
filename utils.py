import os
import tkinter as tk
from tkinter import ttk

class AskStringDialog(tk.simpledialog.Dialog) :
    def __init__(self, parent, title, prompt, default, width=300, height=200) :
        self.width = width
        self.height = height
        self.prompt = prompt
        self.default = default
        super().__init__(parent, title)
    
    def body(self, container) :
        self.geometry(f"{self.width}x{self.height}")
        self.label = ttk.Label(container, text=self.prompt)
        self.label.pack(padx=10, pady=10)
        self.entry = ttk.Entry(container)
        self.entry.insert(0, self.default)
        self.entry.pack(padx=10, pady=10)
        self.entry.configure(width="25")
        return self.entry
    
    def apply(self) :
        self.result = self.entry.get()

class FileUtils :
    def check_if_settings_json_exists() :
        default_settings_json_path = f"{os.path.dirname(os.path.abspath(__file__))}/appdata/cfg/settings.json"
        # print(f"{os.path.basename(__file__)} line 6 :", default_settings_json_path)
        if not os.path.exists(default_settings_json_path) :
            return False, default_settings_json_path
        else :
            return True, default_settings_json_path

class XmlUtils :
    def indent_root(self, elem, level=0) :
        i = "\n" + level * "    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent_root(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i