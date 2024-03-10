import tkinter as tk
from tkinter import ttk
import os
import json
import pymsgbox
import time
import sys
import subprocess
import signal
from datetime import datetime
import shutil
import pyautogui
from tkinter import simpledialog
from tkinter.messagebox import askyesno
from xml_to_xlsx import Profile_Xml_to_Xlsx
from tktooltip import ToolTip
from utils import FileUtils
from utils import AskStringDialog

class AppGUI :
    def __init__(self) :
        self.app_path = os.path.dirname(os.path.abspath(__file__))
        # self.styling = {}
        # self.styling["paddings"] = {"padx": 4, "pady": 4}
        # if sys.platform == "darwin" :
        #     self.app_path = self.app_path.replace("/_internal", "")

        self.stored_org_list = self.get_stored_orgs()

        self.create_main_window()

    def get_stored_orgs(self) :
        stored_orgs_dir = os.listdir(f'{self.app_path}/appdata/stored_orgs')
        stored_org_list = []
        for stored_org in stored_orgs_dir :
            stored_org_list.append(stored_org.split('.')[0])
        return stored_org_list

    def create_main_window(self) :
        self.current_target_org = None
        self.main_window = tk.Tk()
        style = ttk.Style()
        style.layout("Tab", [('Notebook.tab', {'sticky': 'nswe', 'children':
                        [('Notebook.padding', {'side': 'top', 'sticky': 'nswe', 'children':
                            [('Notebook.label', {'side': 'top', 'sticky': ''})],
                        })],
                    })]
                    )
        # style.configure("Tab", focuscolor=style.configure(".")["background"], padding=(10, 3))
        # style.configure("TMenubutton", background="#ff0000")
        # style.theme_use('clam')
        style.configure("border.TMenubutton", background="#ffffff", width=45, borderwidth=1)
        # style.configure('TCheckbutton', focuscolor=style.configure(".")["background"])

        self.main_window.geometry('750x400')
        self.main_window.resizable(False, False)

        self.create_org_selection_section()
        
        self.tabs = ttk.Notebook(self.main_window, style="TNotebook", takefocus=False)
        self.tabs.place(x=0, y=100, width=750, height=310)

        self.create_retrieve_frame(self.tabs)
        self.create_deploy_frame(self.tabs)
        self.create_setting_frame(self.tabs)

        self.status_text = tk.StringVar()
        self.status_text.set("Ready")
        self.status = ttk.Label(self.main_window, textvariable=self.status_text, relief=tk.SUNKEN, border=1, anchor=tk.S)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

        # self.main_window.eval('tk::PlaceWindow . center')
        self.main_window.mainloop()

    def create_org_selection_section(self) :
        target_org_label = ttk.Label(self.main_window, text="Target org")
        target_org_label.place(x=10, y=10)

        target_org_label_pipe = ttk.Label(self.main_window, text="|")
        target_org_label_pipe.place(x=90, y=10)

        self.target_org = tk.StringVar()
        self.target_org_menu = ttk.OptionMenu(self.main_window, self.target_org, "Please select an org...", *self.stored_org_list, "Add new org", command=self.target_org_changed)
        self.target_org_menu.place(x=100, y=9)

        # target_org_type_label = ttk.Label(self.main_window, text='Org type')
        # target_org_type_label.place(x=10, y=40)
        
        # target_org_type_label_pipe = ttk.Label(self.main_window, text="|")
        # target_org_type_label_pipe.place(x=75, y=40)

        # org_type_list = ["Sandbox", "Developer Edition"]
        # self.target_org_type_menu = ttk.OptionMenu(self.main_window, self.target_org_type, "Please select target org...", *org_type_list)
        # self.target_org_type_menu.place(x=85, y=40)
        self.target_org_type = tk.StringVar()
        self.target_org_type_value = ttk.Label(self.main_window, textvariable=self.target_org_type)
        self.target_org_type_value.place(x=90, y=40)

    def create_retrieve_frame(self, container) :
        retrieve_frame = ttk.Frame(container)
        # retrieve_frame.columnconfigure(3, weight=2)
        selector_label = ttk.Label(retrieve_frame, text="Selector").grid(row=0, column=0, padx=10, ipady=10)
        selector_label_pipe = ttk.Label(retrieve_frame, text="|").grid(row=0, column=1)

        # self.stored_selectors = os.listdir(f'{self.app_path}/appdata/stored_selector/{self.target_org.get()}')
        self.selector_file = tk.StringVar()
        self.selector_file_menu = ttk.OptionMenu(retrieve_frame, self.selector_file, "", style="border.TMenubutton", command=self.selector_file_changed)
        self.selector_file_menu.configure(state="disabled")
        self.selector_file_menu.grid(row=0, column=2, padx=5, sticky=tk.W)
        self.retrieve_btn = ttk.Button(retrieve_frame, text="Retrieve Permissions", state=tk.DISABLED, takefocus=0, command=self.retrieve_perms)
        self.retrieve_btn.grid(row=1, column=2, padx=5)

        self.open_selector_file_btn = ttk.Button(retrieve_frame, text="Open file", state=tk.DISABLED, takefocus=0, command=self.open_selector_file_click)
        self.open_selector_file_btn.grid(row=0, column=3)

        self.tabs.add(retrieve_frame, text="Retrieve")

    def create_deploy_frame(self, container) :
        deploy_frame = ttk.Frame(container)
        self.tabs.add(deploy_frame, text="Deploy")

    def create_setting_frame(self, container) :
        setting_frame = ttk.Frame(container)

        settings_json_exists, settings_data = FileUtils.check_if_settings_json_exists()
        print(f"{os.path.basename(__file__)} line 118 :", settings_json_exists)
        print(f"{os.path.basename(__file__)} line 119 :", settings_data)
        if settings_json_exists :
            settings_data = ""

        perm_list = ["CustomApplication", "ApexClass"]
        perm_filter = {}
        for perm in perm_list :
            perm_filter[perm] = tk.StringVar()
            perm_filter[perm].set("Enabled")

        for idx, perm in enumerate(perm_list) :
            checkbox = ttk.Checkbutton(setting_frame, text=perm, var=perm_filter[perm], onvalue="Enabled", offvalue="Disabled")
            checkbox.grid(row=idx, column=0, sticky=tk.W)

        self.tabs.add(setting_frame, text="Settings")

    def target_org_changed(self, *args) :
        if self.target_org.get() != self.current_target_org or self.target_org.get() == "Add new org":
            self.current_target_org = self.target_org.get()
            self.status_text.set("Processing...")
            # self.main_window.after(100, self.status_text.set, "Ready")
            # self.main_window.wait_variable(self.status_text)
            if self.target_org.get() == "Add new org" :
                self.target_org.set("Please select an org...")
                # org_type = pymsgbox.confirm(title="Select org type", text="Please select org type.", buttons=["Sandbox", "Developer Edition"], timeout=7000)
                # org_type = pyautogui.confirm("KK", buttons=["Sandbox", "Developer Edition"])
                # org_type = simpledialog.askstring(title="Test", prompt="Entire Start Date in MM/DD/YYYY format:")
                self.retrieve_btn["state"] = tk.DISABLED
                self.open_selector_file_btn["state"] = tk.DISABLED
                self.selector_file.set("")
                self.selector_file_menu["state"] = tk.DISABLED
                self.popup_select_org_type()
                # if org_type != None and org_type in ["Sandbox", "Developer Edition"]:
                #     self.sf_authenticate(org_type)
                # print(org_type)
            else :
                if self.target_org.get() != None :
                    stored_org_file = open(f'{self.app_path}/appdata/stored_orgs/{self.target_org.get()}.json')
                    stored_org_data = json.load(stored_org_file)

                    check_alias = subprocess.Popen("sf alias list --json", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                    self.main_window.update()
                    check_alias_out, check_alias_err = check_alias.communicate()
                    check_alias_result = json.loads(check_alias_out.decode("utf-8"))

                    is_check_alias_complete = None
                    for item in check_alias_result["result"] :
                        if item["alias"] == stored_org_data["sf_alias"] and item["value"] == stored_org_data["username"] :
                            is_check_alias_complete = "Done"
                            break

                    if is_check_alias_complete != None :
                        if stored_org_data["isSandbox"] == True :
                            self.update_org_type("Sandbox")
                            # self.target_org_type.set("Sandbox")
                            # ToolTip(self.target_org_type_menu, msg="Target org has logged in with Sandbox")
                        else :
                            self.update_org_type("Developer Edition")
                            # self.target_org_type.set("Developer Edition")
                            # ToolTip(self.target_org_type_menu, msg="Target org has logged in with Developer Edition")
                        # self.target_org_type_menu["state"] = tk.DISABLED

                        try :
                            self.stored_selectors = os.listdir(f'{self.app_path}/appdata/stored_selector/{stored_org_data["orgName"]}')
                        except FileNotFoundError :
                            os.makedirs(f'{self.app_path}/appdata/stored_selector/{stored_org_data["orgName"]}')
                            self.stored_selectors = os.listdir(f'{self.app_path}/appdata/stored_selector/{stored_org_data["orgName"]}')

                        try :
                            self.selector_file_menu.set_menu(self.stored_selectors[0], *self.stored_selectors, "Import", "Add new")
                        except IndexError :
                            self.selector_file_menu.set_menu("", *self.stored_selectors, "Import", "Add new")
                        self.retrieve_btn["state"] = tk.NORMAL
                        self.open_selector_file_btn["state"] = tk.NORMAL
                        self.selector_file_menu["state"] = tk.NORMAL

                        self.status_text.set("Ready")
    
    def update_org_type(self, org_type) :
        # self.target_org_type_value = ttk.Label(self.main_window, textvariable=self.target_org_type)
        # self.target_org_type_value.place(x=90, y=40)
        # and self.target_org_type_label != None and self.target_org_type_label_pipe != None
        if org_type == None or org_type == "Add new org" :
            # if self.target_org_type_label.winfo_exists() == 1 and self.target_org_type_label_pipe.winfo_exists() == 1 :
            # self.target_org_type_label.after(100, self.target_org_type_label.destroy())
            try :
                self.target_org_type_label.destroy()
                self.target_org_type_label_pipe.destroy()
                self.target_org_type.set("")
            except :
                pass
        else :
            self.target_org_type_label = ttk.Label(self.main_window, text='Org type')
            self.target_org_type_label.place(x=10, y=40)
        
            self.target_org_type_label_pipe = ttk.Label(self.main_window, text="|")
            self.target_org_type_label_pipe.place(x=75, y=40)
            self.target_org_type.set(org_type)

        # self.main_window.update()
        # print(self.target_org_type_label.winfo_exists())

    def sf_authenticate(self, org_type) :
        if org_type == "Developer Edition" :
            instance_url = "https://login.salesforce.com"
        else :
            instance_url = "https://test.salesforce.com"
        
        timeout = 60
        get_timer = time.time
        process = subprocess.Popen(f'sf org login web --instance-url {instance_url} --json', stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        current_time = get_timer()

        while get_timer() < current_time + timeout and process.poll() is None :
            time.sleep(0.5)
        if process.poll() is None :
            alert = pymsgbox.alert(title="Timeout", text="Salesforce Login Timeout!", button="OK")
            process.terminate()
            if sys.platform == "win32" or sys.platfrom == "darwin" :
                if sys.platform == "win32" :
                    check_port_cmd = "netstat -ano | findstr 1717"
                else :
                    check_port_cmd = "lsof -t tcp:1717"

                check_port = subprocess.Popen(check_port_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                out, err = check_port.communicate()
                if sys.platform == "win32" :
                    os.kill(int(out.decode().strip().split(" ")[-1]), signal.SIGTERM)
                else :
                    os.kill(int(out.decode().split("node").split(" ")[4]), signal.SIGTERM)

        else :
            out, err = process.communicate()
            result = json.loads(out.decode('utf-8'))
            if result :
                org_id = result["result"]["orgId"]
                try :
                    org_name = result["result"]["instanceUrl"].split('.')[0].split('--')[1]
                except IndexError :
                    org_name = result["result"]["instanceUrl"].split('.')[0].split('//')[1]
                
                is_sandbox = result["result"]["isSandbox"]
                is_scratch = result["result"]["isScratch"]
                username = result["result"]["username"]

                set_alias = subprocess.run(f"sf alias set pgcv_{org_name} --json", stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
                set_alias_out = json.loads(set_alias.stdout.decode("utf-8"))
                if set_alias_out["result"]["success"] == True :
                    if org_name not in self.stored_org_list :
                        org_properties = {}
                        org_properties["orgId"] = org_id
                        org_properties["orgName"] = org_name
                        org_properties["isSandbox"] = is_sandbox
                        org_properties["isScratch"] = is_scratch
                        org_properties["sf_alias"] = set_alias_out["result"]["alias"]
                        org_properties["username"] = username
                        org_properties["stored_date"] = datetime.now().strftime("%d-%m-%Y")

                        os.makesdir(f'{self.app_path}/appdata/stored_orgs/{org_name}')

                        with open(f'{self.app_path}/appdata/stored_orgs/{org_name}.json', 'w') as stored_org_file :
                            json.dump(org_properties, stored_org_file, indent=4)

                        self.stored_org_list.append(str(org_name))
                        self.target_org_menu.set_menu(str(org_name), *self.stored_org_list, "Add new org")
                        if org_properties["isSandbox"] == True :
                            self.target_org_type.set("Sandbox")
                        else :
                            self.target_org_type.set("Developer Edition")

                        self.retrieve_btn["state"] = tk.NORMAL
                        self.open_selector_file_btn["state"] = tk.NORMAL
                        self.selector_file_menu["state"] = tk.NORMAL

                        self.status_text.set("Ready")

    def selector_file_changed(self, *args) :
        if self.selector_file.get() == "Add new" :
            self.open_selector_file_btn["state"] = tk.DISABLED
            self.retrieve_btn["state"] = tk.DISABLED

            self.selector_file.set("")
            file_name = pymsgbox.prompt(title="", text="Please enter file name", default=f'{self.target_org.get()}_')
            # print(file_name)
            if file_name != None :
                try :
                    shutil.copy(f'{self.app_path}/appdata/default_template/Default_Template.xlsx', f'{self.app_path}/appdata/stored_selector/{self.target_org.get()}')
                    os.chdir(f'{self.app_path}/appdata/stored_selector/{self.target_org.get()}')
                    os.rename("Default_Template.xlsx", f'{file_name}.xlsx')
                    self.stored_selectors.append(file_name)
                    self.selector_file_menu.set_menu(str(file_name), *self.stored_selectors, "Import", "Add new")

                    self.open_selector_file_btn["state"] = tk.NORMAL
                    self.retrieve_btn["state"] = tk.NORMAL

                    os.chdir(self.app_path)
                except OSError :
                    pass
        else :
            self.open_selector_file_btn["state"] = tk.NORMAL
            self.retrieve_btn["state"] = tk.NORMAL

    def open_selector_file_click(self) :
        # file_path = os.path.abspath(self.selector_file.get())
        file_path = f"{self.app_path}/appdata/stored_selector/{self.target_org.get()}/{self.selector_file.get()}"
        os.startfile(file_path)
    
    def retrieve_perms(self) :
        default_output_path = f"{self.app_path}/appdata/stored_perms/{self.target_org.get()}"
        if not os.path.exists(default_output_path):
            os.makedirs(default_output_path)

        config_path = f"{self.app_path}/appdata/stored_selector/{self.target_org.get()}/{self.selector_file.get()}"
        # print(config_path)
        perm_file_name = AskStringDialog(self.main_window, title="Enter file name", prompt="Please name the file", default=f"{self.target_org.get()}_")

        converter = Profile_Xml_to_Xlsx(self.app_path)
        converter.start_convert(perm_file_name.result, default_output_path, config_path, f"pgcv_{self.target_org.get()}")

    def popup_select_org_type(self) :
        self.update_org_type(None)
        self.popup = tk.Toplevel(self.main_window)
        root_x = self.main_window.winfo_rootx()
        root_y = self.main_window.winfo_rooty()
        self.popup.geometry("350x150")
        self.popup.geometry(f"+{root_x+300}+{root_y+100}") 
        self.popup.resizable(False, False)
        self.popup.grab_set()

        please_select_org_type_label = ttk.Label(self.popup, text="Please select org type.")
        please_select_org_type_label.place(relx=0.5,  rely=0.2, anchor=tk.CENTER)
        developer_edition_btn = ttk.Button(self.popup, text="Developer Edition", command=lambda:[self.popup.destroy(), self.update_org_type("Developer Edition"), self.self.sf_authenticate("Developer Edition")])
        developer_edition_btn.place(relx=0.715, rely=0.6, anchor=tk.CENTER)

        sandbox_btn = ttk.Button(self.popup, text="Sandbox", command=lambda:[self.popup.destroy(), self.update_org_type("Sandbox"), self.sf_authenticate("Sandbox")])
        sandbox_btn.place(relx=0.25, rely=0.6, anchor=tk.CENTER)

if __name__ == "__main__" :
    appGui = AppGUI()