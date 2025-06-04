import json
import os

CONFIG_FILE = "config.json"

def load_config():
    """Carga la configuración desde el archivo JSON."""
    if not os.path.exists(CONFIG_FILE):
        return {
            "itemsadder_base_path": "",
            "projects": ["namespace"]
        }
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "itemsadder_base_path": "",
            "projects": ["namespace"]
        }

def save_config(config):
    """Guarda la configuración en el archivo JSON."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def update_config(key, value):
    """Actualiza un valor específico en la configuración."""
    config = load_config()
    config[key] = value
    save_config(config)

def add_project(project_name):
    """Añade un nuevo proyecto a la configuración."""
    config = load_config()
    if project_name not in config["projects"]:
        config["projects"].append(project_name)
        save_config(config)
        return True
    return False