import yaml
import os
from tkinter import messagebox

def guardar_yaml_en_archivo(yaml_content, file_base_name, output_full_path, message_prefix=""):
    """Guarda el contenido YAML en un archivo."""
    if not yaml_content.strip():
        messagebox.showwarning("Contenido vacío", "El área de YAML está vacía. No hay nada que guardar.")
        return False

    try:
        # Validar estructura YAML
        yaml.safe_load(yaml_content)
        
        # Asegurar que exista el directorio
        os.makedirs(os.path.dirname(output_full_path), exist_ok=True)
        
        with open(output_full_path, 'w', encoding='utf-8') as f:
            f.write(yaml_content)
        return True
    except yaml.YAMLError as e:
        messagebox.showerror("Error al guardar", f"El contenido YAML es inválido:\n{e}")
    except Exception as e:
        messagebox.showerror("Error al guardar", f"Ocurrió un error al guardar el archivo: {e}")
    return False

def load_yaml_from_file(file_path):
    """Carga un archivo YAML y lo devuelve como diccionario."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        messagebox.showwarning("Archivo no encontrado", f"El archivo '{file_path}' no existe.")
    except yaml.YAMLError as e:
        messagebox.showerror("Error de YAML", f"Error al leer YAML de '{file_path}': {e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado al cargar el archivo: {e}")
    return None