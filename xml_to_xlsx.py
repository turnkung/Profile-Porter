import os
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as eTree
import subprocess
import pymsgbox
from utils import XmlUtils
from tkinter import simpledialog
import pyautogui

class Profile_Xml_to_Xlsx :
    def __init__(self, app_path) :
        self.app_path = app_path
        self.salesforce_project_path = f"{self.app_path}/appdata/salesforce/salesforce_project/"

    def start_convert(self, perm_file_name, output_path, config_path, org_alias) :
        default_package_path = f"{self.salesforce_project_path}/manifest/package.xml"
        # perm_file_name = pymsgbox.prompt(title="File name required.", text="Please enter file name.", default=f"{org_alias.split('_')[1]}_")
        # perm_file_name = AskStringDialog(title="Enter file name", prompt="Please enter filename", default=f"{org_alias.split('_')[1]}_")
        # perm_file_name = pyautogui.prompt(title="Enter file name", text="Please name the permission file", default=f"{org_alias.split('_')[1]}_")
        print(perm_file_name)

        if perm_file_name != None :
            self.clear_profile_dir()
            self.read_config(config_path)
            self.retrieve_package(default_package_path, org_alias, perm_file_name)

    def clear_profile_dir(self) :
        profile_dir = f"{self.app_path}/appdata/salesforce/salesforce_project/force-app/main/default/profiles"
        if os.path.exists(profile_dir) :
            for profile in os.scandir(profile_dir) :
                os.remove(profile.path)

    def read_config(self, config_path) :
        components_df = pd.read_excel(config_path, sheet_name="Components", index_col=None)
        profiles_df = pd.read_excel(config_path, sheet_name="Profiles", index_col=None)

        target = {}
        target["profiles"] = []
        target["components"] = {}

        acceptable_components = ["CustomApplication", "ApexClass", "CustomField", "Flow", "Layout", "CustomObject", "ApexPage", "RecordType", "CustomTab"]

        previous_component_type = None
        current_component_type = None
        for i in range(components_df.sahpe[0]) :
            component_type = components_df.iloc[i, 0]

            if component_type in acceptable_components :
                current_component_type = component_type
                if previous_component_type != current_component_type :
                    target["components"][components_df.iloc[i, 0]] = []
                
                target["components"][components_df.iloc[i, 0]].append(components_df.iloc[i, 1].strip())
                previous_component_type = component_type
        
        for j in range(profiles_df.shape[0]) :
            target["profiles"].append(profiles_df.iloc[j, 0])
        
        self.re_write_package(target["profiles"], target["components"])

    def re_write_package(self, package_path, target_profiles, target_components) :
        root = eTree.Element("Package")
        root.set("xmlns", "http://soap.sforce.com/2006/04/metadata")
        element = eTree.Element("types")
        root.append(element)

        for profile in target_profiles :
            sub_element = eTree.SubElement(element, "members")
            sub_element.text = str(profile)
        
        name_element = eTree.SubElement(element, "name")
        name_element.text = "Profile"

        for idx, component_type in enumerate(target_components) :
            element = eTree.Element("types")
            root.append(element)
            for component in target_components[component_type] :
                member = eTree.SubElement(element, "members")
                member.text = str(component)
            
            name_element = eTree.SubElement(element, "name")
            name_element.text = str(component_type)
        
        element = eTree.Element("version")
        element.text = "58.0"
        root.append(element)

        xmlUtils = XmlUtils()
        xmlUtils.indent_root(root)
        xml_tree = eTree.ElementTree(root)
        with open(package_path, 'wb') as xml_file :
            xml_tree.write(xml_file, encoding="utf-8", xml_declaration=True)

    def retrieve_package(self, package_path, org_alias) :
        retrieve_cmd = f"sf project retrieve start --manifest {package_path} --target-org {org_alias}"
        process = subprocess.Popen(retrieve_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

    def convert_profile_xml_to_xlsx(self, profile_dir, perm_file_name) :
        if profile_dir == None :
            pymsgbox.alert(title="Error", text="Invalid profile directory.", button="OK")
        else :
            profile_list = []
            permission_list = []
            permission_data = {}

            prohibited_perms = ["loginRanges", "custom", "userLicense"]

            for file in Path(profile_dir).glob("*.profile-meta.xml") :
                profile = eTree.parse(profile_dir + file.name)
                profile_name = str(file.name)[:len(file.name) - 17]
                permissions = profile.getroot()