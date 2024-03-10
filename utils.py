import os

class FileUtils :
    def check_if_settings_json_exists() :
        default_settings_json_path = f"{os.path.dirname(os.path.abspath(__file__))}/appdata/cfg/settings.json"
        print(f"{os.path.basename(__file__)} line 6 :", default_settings_json_path)
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