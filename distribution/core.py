import requests
import logging
import importlib.util
import os
import ctypes
import json
import sys
import platform

FEATUREDATA = os.path.join(os.environ['USERPROFILE'], 'AppData', 'Roaming', 'featuredata')
os.makedirs(FEATUREDATA, exist_ok=True)
FEATURELOGS = os.path.join(FEATUREDATA, "logs")
FEATURETEMP = os.path.join(FEATUREDATA, "temp")
FEATURESETTINGS = os.path.join(FEATUREDATA, "settings.json")

def getmodule(url, module_name):
    response = requests.get(url)
    script_content = response.text
    os.makedirs(os.path.join(FEATUREDATA, 'temp'), exist_ok=True)
    temp_file = os.path.join(os.path.join(FEATUREDATA, 'temp'), f"{module_name}.py")
    
    with open(temp_file, "w") as file:
        file.write(script_content)

    spec = importlib.util.spec_from_file_location(module_name, temp_file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    os.remove(temp_file)
    
    return module

loggermodule = getmodule("https://raw.githubusercontent.com/ftnick/feature/main/host/script/logger.py", "logger")
LoggerManager = getattr(loggermodule, 'LoggerManager') # get class
LOGGER_MANAGER = LoggerManager(name="__main__", appendlog=False, level=logging.INFO)
LOGGER = LOGGER_MANAGER.get_logger()

CURRENT_PLATFORM = str(platform.system()).lower()
CURRENT_PLATFORM_RELEASE = str(platform.release()).lower()

MB_OK = 0x00000000
MB_ICONINFORMATION = 0x00000040
MB_ICONWARNING = 0x00000030
MB_ICONERROR = 0x00000010
MB_YESNO = 0x04
MB_ICONQUESTION = 0x20
MB_IDYES = 6
MB_IDNO = 7

USER32 = ctypes.windll.user32
SCREEN_WIDTH = USER32.GetSystemMetrics(0)
SCREEN_HEIGHT = USER32.GetSystemMetrics(1)
CONSOLE_WIDTH = int(SCREEN_WIDTH * 0.75)
CONSOLE_HEIGHT = int(SCREEN_HEIGHT * 0.75)
WLEFT = int((SCREEN_WIDTH - CONSOLE_WIDTH) / 2)
WTOP = int((SCREEN_HEIGHT - CONSOLE_HEIGHT) / 2)

def version():
    try:
        response = requests.get("https://raw.githubusercontent.com/ftnick/feature/main/host/version.txt")
        response.raise_for_status()
        version = response.text.strip()
        return version
    except requests.HTTPError as http_err:
        LOGGER.error(f"HTTP error occurred: {http_err}")
    except requests.ConnectionError as conn_err:
        LOGGER.error(f"Connection error occurred: {conn_err}")
    except requests.Timeout as timeout_err:
        LOGGER.error(f"Timeout error occurred: {timeout_err}")
    except requests.RequestException as req_err:
        LOGGER.error(f"Error occurred: {req_err}")
    return None

def message_box(message, title, icon=MB_ICONINFORMATION):
    USER32.MessageBoxW(0, message, title, MB_OK | icon)

def load_local_settings():
    try:
        with open(FEATURESETTINGS, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_local_settings(settings):
    with open(FEATURESETTINGS, 'w') as file:
        json.dump(settings, file, indent=4)

def check_admin():
    return ctypes.windll.shell32.IsUserAnAdmin() and True or False

def relaunch_as_admin(exit):
    if not ctypes.windll.shell32.IsUserAnAdmin():
        try:
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        except Exception as e:
            LOGGER.error(f"Failed to launch {sys.argv} as an administrator ({str(e)})")
        else:
            LOGGER.info(f"No exception launching {sys.argv} as an administrator")
        if exit:
            sys.exit()

def console_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)