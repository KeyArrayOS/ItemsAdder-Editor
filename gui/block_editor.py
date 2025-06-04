import tkinter as tk
from tkinter import messagebox, ttk
import yaml
import os
from core import itemsadder

class NewBlockEditor(tk.Toplevel):
    def __init__(self, parent, current_namespace, base_path, block_id=None, blocks_file=None):
        super().__init__(parent)
        self.title("Block Editor")
        self.geometry("800x600")
        self.resizable(True, True)
        self.current_namespace = current_namespace
        self.base_path = base_path
        self.block_id = block_id  # ID del bloque (para edición)
        self.blocks_file = blocks_file  # Archivo blocks.yml (para edición)
        self.radio_placed_model_type_var = tk.StringVar(value="CUBE")
        
        if self.block_id and self.blocks_file:
            self.title(f"Editar Bloque - {self.block_id}")
            self.mode = "edit"
        else:
            self.title(f"Añadir Nuevo Bloque - Namespace: {current_namespace}")
            self.mode = "new"

        self.geometry("1100x700")
        self.is_loading_data = False  # Bandera para evitar actualizaciones durante carga

        main_panel_frame = tk.Frame(self, padx=10, pady=10)
        main_panel_frame.pack(fill=tk.BOTH, expand=True)

        input_fields_frame = tk.LabelFrame(main_panel_frame, text="Propiedades del Bloque", padx=10, pady=10)
        input_fields_frame.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)

        yaml_editor_frame = tk.LabelFrame(main_panel_frame, text="YAML del Bloque", padx=10, pady=10)
        yaml_editor_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.create_input_fields(input_fields_frame)
        self.create_yaml_editor(yaml_editor_frame)
        self.create_buttons(main_panel_frame)

        self.bind_field_changes()

        # Carga inicial del YAML (si estamos editando) o por defecto (si es nuevo)
        if self.mode == "edit":
            self.load_block_data()
        else:
            self.actualizar_yaml_desde_campos()

    def create_input_fields(self, parent_frame):
        current_row = 0
    
        tk.Label(parent_frame, text="Namespace:").grid(row=current_row, column=0, sticky="w", pady=2)
        self.entry_namespace = tk.Entry(parent_frame, width=35)
        self.entry_namespace.grid(row=current_row, column=1, pady=2)
        self.entry_namespace.insert(0, self.current_namespace)
        self.entry_namespace.config(state="readonly")
        current_row += 1

        ttk.Radiobutton(placed_model_frame, text="CUBE", 
                        variable=self.radio_placed_model_type_var, 
                        value="CUBE", 
                        command=self.toggle_texture_fields).pack(side=tk.LEFT)
        ttk.Radiobutton(placed_model_frame, text="CUSTOM", 
                        variable=self.radio_placed_model_type_var, 
                        value="CUSTOM", 
                        command=self.toggle_texture_fields).pack(side=tk.LEFT)

        tk.Label(parent_frame, text="ID del Bloque:").grid(row=current_row, column=0, sticky="w", pady=2)
        self.entry_id = tk.Entry(parent_frame, width=35)
        self.entry_id.grid(row=current_row, column=1, pady=2)
        self.entry_id.insert(0, self.block_id)
        # Si es modo edición, el ID no debería poder cambiarse fácilmente
        if self.mode == "edit":
            self.entry_id.config(state="readonly")
        current_row += 1
        

        tk.Label(parent_frame, text="Nombre a Mostrar:").grid(row=current_row, column=0, sticky="w", pady=2)
        self.entry_display_name = tk.Entry(parent_frame, width=35)
        self.entry_display_name.grid(row=current_row, column=1, pady=2)
        self.entry_display_name.insert(0, "§fMi Nuevo Bloque")
        current_row += 1

        tk.Label(parent_frame, text="Material Base:").grid(row=current_row, column=0, sticky="w", pady=2)
        self.entry_material = tk.Entry(parent_frame, width=35)
        self.entry_material.grid(row=current_row, column=1, pady=2)
        self.entry_material.insert(0, "PAPER")
        current_row += 1

        ttk.Separator(parent_frame, orient='horizontal').grid(row=current_row, columnspan=2, sticky="ew", pady=5)
        current_row += 1

        resource_frame = tk.LabelFrame(parent_frame, text="Recursos (Texturas)", padx=5, pady=5)
        resource_frame.grid(row=current_row, columnspan=2, sticky="ew", pady=5)
        resource_row = 0

        self.chk_generate_var = tk.BooleanVar(value=True)
        tk.Checkbutton(resource_frame, text="Generar Modelo (generate: true)", variable=self.chk_generate_var,
                       command=self.on_field_change).grid(row=resource_row, column=0, columnspan=2, sticky="w")
        resource_row += 1

        self.radio_texture_var = tk.StringVar(value="single")

        tk.Radiobutton(resource_frame, text="Textura Única:", variable=self.radio_texture_var, value="single",
                       command=self.toggle_texture_fields).grid(row=resource_row, column=0, sticky="w")
        self.entry_single_texture = tk.Entry(resource_frame, width=30)
        self.entry_single_texture.grid(row=resource_row, column=1, pady=2)
        self.entry_single_texture.insert(0, "block/new_block.png")
        resource_row += 1

        tk.Radiobutton(resource_frame, text="Texturas por Cara:", variable=self.radio_texture_var, value="multiple",
                       command=self.toggle_texture_fields).grid(row=resource_row, column=0, sticky="w")

        self.texture_entries = {}
        texture_faces = ["down", "east", "north", "south", "up", "west"]
        for i, face in enumerate(texture_faces):
            tk.Label(resource_frame, text=f"  {face.capitalize()}:").grid(row=resource_row + i + 1, column=0, sticky="w", pady=1)
            entry = tk.Entry(resource_frame, width=30)
            entry.grid(row=resource_row + i + 1, column=1, pady=1)
            entry.insert(0, f"block/new_block_{face}.png")
            self.texture_entries[face] = entry
        resource_row += len(texture_faces) + 1
        current_row += 1 + resource_row

        self.toggle_texture_fields()

        ttk.Separator(parent_frame, orient='horizontal').grid(row=current_row, columnspan=2, sticky="ew", pady=5)
        current_row += 1

        specific_props_frame = tk.LabelFrame(parent_frame, text="Propiedades Específicas (Bloque)", padx=5, pady=5)
        specific_props_frame.grid(row=current_row, columnspan=2, sticky="ew", pady=5)
        specific_props_row = 0

        tk.Label(specific_props_frame, text="Tipo de Modelo Colocado:").grid(row=specific_props_row, column=0, sticky="w", pady=2)
        self.radio_placed_model_type_var = tk.StringVar(value="REAL_NOTE")
        ttk.Radiobutton(specific_props_frame, text="REAL_NOTE", variable=self.radio_placed_model_type_var, value="REAL_NOTE",
                        command=self.on_field_change).grid(row=specific_props_row, column=1, sticky="w")
        specific_props_row += 1
        ttk.Radiobutton(specific_props_frame, text="REAL_NOTE_BLOCK", variable=self.radio_placed_model_type_var, value="REAL_NOTE_BLOCK",
                        command=self.on_field_change).grid(row=specific_props_row, column=1, sticky="w")
        specific_props_row += 1

        tk.Label(specific_props_frame, text="Partículas de Rotura:").grid(row=specific_props_row, column=0, sticky="w", pady=2)
        self.entry_break_particles = tk.Entry(specific_props_frame, width=35)
        self.entry_break_particles.grid(row=specific_props_row, column=1, pady=2)
        self.entry_break_particles.insert(0, "ITEM")
        specific_props_row += 1

        self.chk_drop_when_mined_var = tk.BooleanVar(value=False)
        tk.Checkbutton(specific_props_frame, text="Caer al Minar (drop_when_mined: false)", variable=self.chk_drop_when_mined_var,
                       command=self.on_field_change).grid(row=specific_props_row, column=0, columnspan=2, sticky="w")
        specific_props_row += 1

    def create_yaml_editor(self, parent_frame):
        self.yaml_text = tk.Text(parent_frame, wrap=tk.WORD, width=65, height=30, font=("Consolas", 10))
        self.yaml_text.pack(fill=tk.BOTH, expand=True)

        yaml_scrollbar = tk.Scrollbar(parent_frame, command=self.yaml_text.yview)
        yaml_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.yaml_text.config(yscrollcommand=yaml_scrollbar.set)

    def create_buttons(self, parent_frame):
        button_frame = tk.Frame(parent_frame)
        button_frame.pack(pady=10)

        button_update_yaml = tk.Button(button_frame, text="Actualizar YAML desde Campos", command=self.actualizar_yaml_desde_campos)
        button_update_yaml.pack(side=tk.LEFT, padx=5)

        button_update_fields = tk.Button(button_frame, text="Actualizar Campos desde YAML", command=self.actualizar_campos_desde_yaml)
        button_update_fields.pack(side=tk.LEFT, padx=5)

        button_save_block = tk.Button(button_frame, text="Guardar Bloque", command=self.guardar_bloque)
        button_save_block.pack(side=tk.LEFT, padx=5)

    def bind_field_changes(self):
        """Bind all relevant input fields to update the YAML text."""
        self.entry_namespace.bind("<KeyRelease>", self.on_field_change)
        self.entry_id.bind("<KeyRelease>", self.on_field_change)
        self.entry_display_name.bind("<KeyRelease>", self.on_field_change)
        self.entry_material.bind("<KeyRelease>", self.on_field_change)
        self.chk_generate_var.trace_add("write", self.on_field_change)
        self.radio_texture_var.trace_add("write", self.on_field_change)
        self.entry_single_texture.bind("<KeyRelease>", self.on_field_change)
        for entry in self.texture_entries.values():
            entry.bind("<KeyRelease>", self.on_field_change)
        self.radio_placed_model_type_var.trace_add("write", self.on_field_change)
        self.entry_break_particles.bind("<KeyRelease>", self.on_field_change)
        self.chk_drop_when_mined_var.trace_add("write", self.on_field_change)

    def toggle_texture_fields(self):
        if self.radio_texture_var.get() == "single":
            self.entry_single_texture.config(state="normal")
            for entry in self.texture_entries.values():
                entry.config(state="disabled")
        else:
            self.entry_single_texture.config(state="disabled")
            for entry in self.texture_entries.values():
                entry.config(state="normal")
        # No llamar actualizar_yaml_desde_campos aquí para evitar doble actualización
        # si se llama desde on_field_change
        if not self.is_loading_data:  # Solo actualizar si no estamos cargando datos
            self.actualizar_yaml_desde_campos()

    def on_field_change(self, *args):
        # Evitar actualizaciones si la ventana está en proceso de cargar datos
        if self.is_loading_data:
            return
        self.actualizar_yaml_desde_campos()

    def actualizar_yaml_desde_campos(self):
        namespace = self.entry_namespace.get()
        block_id = self.entry_id.get()
        display_name = self.entry_display_name.get()
        material = self.entry_material.get()
        generate = self.chk_generate_var.get()
        placed_model_type = self.radio_placed_model_type_var.get()
        break_particles = self.entry_break_particles.get()
        drop_when_mined = self.chk_drop_when_mined_var.get()

        block_data = {
            "info": {
                "namespace": namespace
            },
            "items": {
                block_id: {
                    "display_name": display_name,
                    "permission": block_id,  # Corregido: no necesita ser una cadena formateada
                    "resource": {
                        "generate": generate,
                        "material": material
                    },
                    "specific_properties": {
                        "block": {
                            "drop_when_mined": drop_when_mined,
                            "placed_model": {
                                "type": placed_model_type,
                                "break_particles": break_particles
                            }
                        }
                    }
                }
            }
        }

        if self.radio_texture_var.get() == "single":
            single_texture_path = self.entry_single_texture.get()
            if single_texture_path:
                block_data["items"][block_id]["resource"]["texture"] = single_texture_path
        else:
            # Usar un diccionario en lugar de lista para las texturas
            textures_dict = {}
            for face, entry in self.texture_entries.items():
                if entry.get():
                    textures_dict[face] = entry.get()
            if textures_dict:
                block_data["items"][block_id]["resource"]["textures"] = textures_dict

        self.yaml_text.delete(1.0, tk.END)
        try:
            # Usar dump con Dumper para mantener el orden
            formatted_yaml = yaml.dump(block_data, indent=4, allow_unicode=True, sort_keys=False)
            self.yaml_text.insert(tk.END, formatted_yaml)
        except Exception as e:
            self.yaml_text.insert(tk.END, f"Error al generar YAML: {e}")

    def load_block_data(self):
        """Carga los datos del bloque desde el archivo YAML y actualiza los campos."""
        if not self.blocks_file or not self.block_id:
            return
            
        self.is_loading_data = True
        block_details = itemsadder.load_block_data(self.block_id, self.blocks_file)
        if block_details:
            try:
                # No editar el namespace en el editor, solo mostrarlo
                self.entry_namespace.config(state="normal")
                self.entry_namespace.delete(0, tk.END)
                self.entry_namespace.insert(0, self.current_namespace)
                self.entry_namespace.config(state="readonly")

                if self.mode == "new":
                    self.entry_id.config(state="normal")
                    self.entry_id.delete(0, tk.END)
                    self.entry_id.insert(0, self.block_id)
                    self.entry_id.config(state="readonly")
                else:
                    # En modo edición, el ID ya está establecido y es de solo lectura
                    pass

                self.entry_display_name.delete(0, tk.END)
                self.entry_display_name.insert(0, block_details.get("display_name", ""))

                resource = block_details.get("resource", {})
                self.entry_material.delete(0, tk.END)
                self.entry_material.insert(0, resource.get("material", ""))

                self.chk_generate_var.set(resource.get("generate", False))

                # Manejar texturas (puede ser cadena única o diccionario)
                if "texture" in resource:
                    self.radio_texture_var.set("single")
                    self.entry_single_texture.delete(0, tk.END)
                    self.entry_single_texture.insert(0, resource["texture"])
                elif "textures" in resource:
                    if isinstance(resource["textures"], dict):
                        self.radio_texture_var.set("multiple")
                        for face, entry in self.texture_entries.items():
                            if face in resource["textures"]:
                                entry.delete(0, tk.END)
                                entry.insert(0, resource["textures"][face])
                    elif isinstance(resource["textures"], list):
                        # Manejar formato antiguo (lista)
                        self.radio_texture_var.set("multiple")
                        texture_faces = ["down", "east", "north", "south", "up", "west"]
                        for i, face in enumerate(texture_faces):
                            entry = self.texture_entries.get(face)
                            if entry and i < len(resource["textures"]):
                                entry.delete(0, tk.END)
                                entry.insert(0, resource["textures"][i])
                self.toggle_texture_fields()

                specific_properties = block_details.get("specific_properties", {})
                block_props = specific_properties.get("block", {})
                placed_model = block_props.get("placed_model", {})

                self.radio_placed_model_type_var.set(placed_model.get("type", "REAL_NOTE"))
                self.entry_break_particles.delete(0, tk.END)
                self.entry_break_particles.insert(0, placed_model.get("break_particles", ""))

                self.chk_drop_when_mined_var.set(block_props.get("drop_when_mined", False))

                # Llenar el Text widget YAML
                self.yaml_text.delete(1.0, tk.END)
                # Generamos el YAML solo para este bloque (como si fuera un archivo independiente)
                block_only_data = {
                    "info": {
                        "namespace": self.current_namespace
                    },
                    "items": {
                        self.block_id: block_details
                    }
                }
                formatted_yaml = yaml.dump(block_only_data, indent=4, allow_unicode=True, sort_keys=False)
                self.yaml_text.insert(tk.END, formatted_yaml)

            except Exception as e:
                messagebox.showerror("Error al cargar datos", f"Ocurrió un error al procesar los datos cargados: {e}")
            finally:
                self.is_loading_data = False
        else:
            self.is_loading_data = False
            
        if 'placed_model_type' in self.block_data:
            self.radio_placed_model_type_var.set(self.block_data['placed_model_type'])

    def actualizar_campos_desde_yaml(self):
        self.is_loading_data = True  # Temporalmente deshabilitar on_field_change
        yaml_content = self.yaml_text.get(1.0, tk.END)
        try:
            loaded_data = yaml.safe_load(yaml_content)

            if not loaded_data or not isinstance(loaded_data, dict):
                messagebox.showwarning("Formato YAML", "El YAML cargado no es un diccionario válido.")
                return

            info = loaded_data.get("info", {})
            items = loaded_data.get("items", {})

            namespace_from_yaml = info.get("namespace", "")
            # No editamos el namespace_from_yaml en el campo, solo lo mostramos

            # Obtener el primer bloque
            block_ids = list(items.keys())
            if not block_ids:
                messagebox.showwarning("Formato YAML", "No se encontró ningún ID de bloque en el YAML cargado.")
                return
                
            first_block_id = block_ids[0]
            block_details = items[first_block_id]

            # Actualizar campos
            # self.entry_namespace.config(state="normal")
            # self.entry_namespace.delete(0, tk.END)
            # self.entry_namespace.insert(0, namespace_from_yaml)
            # self.entry_namespace.config(state="readonly")

            # Si estamos editando un bloque existente, su ID no debería cambiar desde el YAML
            if self.mode == "new":
                self.entry_id.config(state="normal")
                self.entry_id.delete(0, tk.END)
                self.entry_id.insert(0, first_block_id)
                self.entry_id.config(state="normal")  # Para que el usuario lo pueda cambiar si lo quiere de forma manual
                # Aunque en la creacion es importante que sea el ID que se guarde.
            # else: # En modo edición, el ID permanece el del archivo original

            self.entry_display_name.delete(0, tk.END)
            self.entry_display_name.insert(0, block_details.get("display_name", ""))

            resource = block_details.get("resource", {})
            self.entry_material.delete(0, tk.END)
            self.entry_material.insert(0, resource.get("material", ""))

            self.chk_generate_var.set(resource.get("generate", False))

            # Manejar texturas (puede ser cadena única o diccionario)
            if "texture" in resource:
                self.radio_texture_var.set("single")
                self.entry_single_texture.delete(0, tk.END)
                self.entry_single_texture.insert(0, resource["texture"])
            elif "textures" in resource:
                if isinstance(resource["textures"], dict):
                    self.radio_texture_var.set("multiple")
                    for face, entry in self.texture_entries.items():
                        if face in resource["textures"]:
                            entry.delete(0, tk.END)
                            entry.insert(0, resource["textures"][face])
                elif isinstance(resource["textures"], list):
                    # Manejar formato antiguo (lista)
                    self.radio_texture_var.set("multiple")
                    texture_faces = ["down", "east", "north", "south", "up", "west"]
                    for i, face in enumerate(texture_faces):
                        entry = self.texture_entries.get(face)
                        if entry and i < len(resource["textures"]):
                            entry.delete(0, tk.END)
                            entry.insert(0, resource["textures"][i])
            self.toggle_texture_fields()

            specific_properties = block_details.get("specific_properties", {})
            block_props = specific_properties.get("block", {})
            placed_model = block_props.get("placed_model", {})

            self.radio_placed_model_type_var.set(placed_model.get("type", "REAL_NOTE"))
            self.entry_break_particles.delete(0, tk.END)
            self.entry_break_particles.insert(0, placed_model.get("break_particles", ""))

            self.chk_drop_when_mined_var.set(block_props.get("drop_when_mined", False))

            messagebox.showinfo("Carga exitosa", "Campos actualizados desde YAML.")
        except yaml.YAMLError as e:
            messagebox.showerror("Error de YAML", f"Error al parsear YAML: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error inesperado al cargar YAML: {e}")
        finally:
            self.is_loading_data = False  # Restablecer el flag

    def guardar_bloque(self):
        yaml_content = self.yaml_text.get(1.0, tk.END).strip()
        
        if self.mode == "new":
            block_id = self.entry_id.get().strip()
            if not block_id:
                messagebox.showwarning("ID de Bloque Requerido", "Por favor, ingrese un ID para el bloque antes de guardar.")
                return
        else:
            block_id = self.block_id

        # Guardar usando la nueva función
        if itemsadder.save_block_to_file(block_id, yaml_content, self.base_path, self.current_namespace):
            if self.mode == "new":
                self.mode = "edit"
                self.block_id = block_id
                self.title(f"Editar Bloque - {block_id}")
                self.entry_id.config(state="readonly")
            messagebox.showinfo("Éxito", f"Bloque '{block_id}' guardado exitosamente.")