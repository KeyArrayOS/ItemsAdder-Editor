import tkinter as tk
from tkinter import messagebox
import os
from .block_editor import NewBlockEditor
from core import itemsadder

class ProjectPage(tk.Toplevel):
    def __init__(self, master, namespace_name, base_path):
        super().__init__(master)
        self.namespace_name = namespace_name
        self.base_path = base_path
        self.title(f"Proyecto: {self.namespace_name}")
        self.geometry("800x600")

        self.main_frame = tk.Frame(self, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.main_frame, text=f"Contenido del Proyecto: {self.namespace_name}", 
                font=("Helvetica", 16, "bold")).pack(pady=10)

        # Frame para la lista de recursos
        resource_list_frame = tk.LabelFrame(self.main_frame, text="Recursos del Proyecto", 
                                          padx=10, pady=10)
        resource_list_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Frame para bloques
        self.block_list_frame = tk.LabelFrame(resource_list_frame, text="Bloques", 
                                           padx=5, pady=5)
        self.block_list_frame.pack(fill=tk.X, pady=5)
        self.block_widgets = []

        # Frames para otros tipos de recursos
        self.item_list_frame = tk.LabelFrame(resource_list_frame, text="Ítems (Próximamente)", 
                                          padx=5, pady=5)
        self.item_list_frame.pack(fill=tk.X, pady=5)

        self.entity_list_frame = tk.LabelFrame(resource_list_frame, text="Entidades (Próximamente)", 
                                            padx=5, pady=5)
        self.entity_list_frame.pack(fill=tk.X, pady=5)

        # Cargar recursos existentes
        self.load_existing_resources()

        # Botón para añadir nuevo recurso
        add_resource_button = tk.Button(self.main_frame, text="Añadir Nuevo Recurso", 
                                      command=self.open_add_resource_dialog)
        add_resource_button.pack(pady=10)

        # Botón para volver
        back_button = tk.Button(self.main_frame, text="Volver al Menú Principal", 
                              command=self.destroy_and_show_main)
        back_button.pack(pady=5)

    def load_existing_resources(self):
        """Carga y muestra los recursos existentes en el proyecto"""
        # Limpiar widgets anteriores
        for widget in self.block_widgets:
            widget.destroy()
        self.block_widgets = []

        # Obtener bloques del namespace
        blocks = itemsadder.find_blocks_in_namespace(self.base_path, self.namespace_name)
        
        if not blocks:
            tk.Label(self.block_list_frame, text="No se encontraron bloques en este proyecto.").pack()
            return
            
        for block_id, blocks_file in blocks:
            btn = tk.Button(self.block_list_frame, text=f"Bloque: {block_id}",
                          command=lambda bid=block_id, bf=blocks_file: self.edit_existing_block(bid, bf))
            btn.pack(fill=tk.X, pady=1)
            self.block_widgets.append(btn)

    def edit_existing_block(self, block_id, blocks_file):
        """Abre el editor para un bloque existente"""
        NewBlockEditor(self, 
                      current_namespace=self.namespace_name,
                      base_path=self.base_path,
                      block_id=block_id,
                      blocks_file=blocks_file)

    def open_add_resource_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Seleccionar Tipo de Recurso")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="¿Qué tipo de recurso quieres añadir?", 
               font=("Helvetica", 10)).pack(pady=10)

        button_block = tk.Button(dialog, text="Bloque", 
                               command=lambda: [dialog.destroy(), self.add_new_block()])
        button_block.pack(pady=5)

        self.wait_window(dialog)

    def add_new_block(self):
        """Abre el editor para crear un nuevo bloque"""
        editor = NewBlockEditor(self, 
                              current_namespace=self.namespace_name,
                              base_path=self.base_path)
        self.wait_window(editor)
        self.load_existing_resources()  # Actualizar lista después de cerrar

    def destroy_and_show_main(self):
        self.destroy()
        self.master.deiconify()