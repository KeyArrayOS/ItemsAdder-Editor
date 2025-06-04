import os
import yaml
from tkinter import messagebox
import shutil

def get_blocks_file_path(base_path, namespace):
    """Devuelve la ruta completa al archivo blocks.yml del namespace"""
    return os.path.join(
        base_path,
        "contents",
        namespace,
        "items_packs",
        namespace,
        "blocks.yml"
    )

def find_namespaces(base_path):
    """Devuelve la lista de namespaces (carpetas) dentro de contents/"""
    contents_dir = os.path.join(base_path, "contents")
    if not os.path.exists(contents_dir):
        return []
    return [name for name in os.listdir(contents_dir) 
            if os.path.isdir(os.path.join(contents_dir, name))]

def create_namespace_structure(base_path, namespace):
    """Crea la estructura de carpetas para un nuevo namespace"""
    # Directorios principales
    dirs = [
        os.path.join("contents", namespace, "items_packs", namespace),
        os.path.join("contents", namespace, "resourcepack", "assets", namespace, "textures", "block"),
        os.path.join("contents", namespace, "resourcepack", "assets", namespace, "models", "block"),
        os.path.join("contents", namespace, "resourcepack", "assets", namespace, "sounds"),
        os.path.join("contents", namespace, "resourcepack", "assets", namespace, "lang"),
    ]
    
    for d in dirs:
        full_dir = os.path.join(base_path, d)
        os.makedirs(full_dir, exist_ok=True)
    
    # Crear archivo blocks.yml inicial
    blocks_file = get_blocks_file_path(base_path, namespace)
    if not os.path.exists(blocks_file):
        with open(blocks_file, 'w', encoding='utf-8') as f:
            f.write("info:\n  namespace: {}\nitems:\n".format(namespace))
    
    return blocks_file

def find_blocks_in_namespace(base_path, namespace):
    """Busca todos los bloques en el archivo blocks.yml del namespace"""
    blocks_file = get_blocks_file_path(base_path, namespace)
    
    if not os.path.exists(blocks_file):
        return []
    
    try:
        with open(blocks_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
            if not data or not isinstance(data, dict) or "items" not in data:
                return []
            
            # Devolvemos lista de (block_id, blocks_file)
            return [(block_id, blocks_file) for block_id in data["items"].keys()]
            
    except yaml.YAMLError as e:
        messagebox.showerror("Error de YAML", f"Error al leer {blocks_file}:\n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error inesperado al leer {blocks_file}:\n{e}")
    
    return []

def save_block_to_file(block_id, yaml_content, base_path, namespace):
    """Guarda un bloque en el archivo blocks.yml del namespace"""
    blocks_file = get_blocks_file_path(base_path, namespace)
    
    # Cargar el archivo existente o crear uno nuevo
    if os.path.exists(blocks_file):
        try:
            with open(blocks_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
        except:
            data = {}
    else:
        data = {
            "info": {
                "namespace": namespace
            },
            "items": {}
        }
    
    # Parsear el nuevo contenido del bloque
    try:
        new_data = yaml.safe_load(yaml_content)
        if not new_data or "items" not in new_data or not new_data["items"]:
            messagebox.showerror("Error", "El formato del bloque es inválido")
            return False
        
        # Obtener el bloque del YAML (debería tener solo un bloque)
        new_block_id, new_block_data = next(iter(new_data["items"].items()))
        
        # Actualizar el bloque existente o agregar uno nuevo
        if "items" not in data:
            data["items"] = {}
        
        data["items"][block_id] = new_block_data
        
        # Guardar el archivo completo
        with open(blocks_file, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, indent=4, allow_unicode=True, sort_keys=False)
        
        return True
        
    except yaml.YAMLError as e:
        messagebox.showerror("Error de YAML", f"El contenido del bloque es inválido:\n{e}")
    except Exception as e:
        messagebox.showerror("Error", f"Error al guardar el bloque:\n{e}")
    
    return False

def load_block_data(block_id, blocks_file):
    """Carga los datos de un bloque específico desde el archivo blocks.yml"""
    try:
        with open(blocks_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            
            if not data or "items" not in data or block_id not in data["items"]:
                return None
                
            return data["items"][block_id]
            
    except Exception as e:
        messagebox.showerror("Error", f"Error al cargar el bloque:\n{e}")
        return None