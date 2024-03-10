import os

class FileUtils :
    def check_if_settings_json_exists() :
        default_settings_json_path = f"{os.path.dirname(os.path.abspath(__file__))}/appdata/cfg/settings.json"
        print(f"{os.path.basename(__file__)} line 6 :", default_settings_json_path)
        if not os.path.exists(default_settings_json_path) :
            return False, default_settings_json_path
        else :
            return True, default_settings_json_path