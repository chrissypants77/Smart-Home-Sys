import os
import ast

default_settings = {'voice_control': False}
settings_file_path = "Misc/settings.txt"


def get_settings():
    global settings_dict

    os.makedirs("Misc", exist_ok=True)

    if not os.path.isfile(settings_file_path):
        with open(settings_file_path, "w") as f:
            f.write(str(default_settings))

    with open(settings_file_path) as f:
        settings_dict = ast.literal_eval(f.read())


get_settings()
