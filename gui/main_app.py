import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import os
from .project_page import ProjectPage
from config_manager import load_config, save_config
from core import itemsadder

class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.config = load_config()
        self.title("ItemsAdder Editor - Proyectos")
        self.geometry("500x400")

        # No cargamos proyectos desde config, se leerán del sistema de archivos
        self.base_path = self.config.get("itemsadder_base_path", "")
        self.projects = []  # Se llenará al actualizar

        self.main_frame = tk.Frame(self, padx=20, pady=20)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.main_frame, text="Selecciona el Directorio Base de ItemsAdder", 
                font=("Helvetica", 12)).pack(pady=5)
        
        # Mostrar la ruta actual
        current_path = self.base_path if self.base_path else "No configurada"
        self.path_label = tk.Label(self.main_frame, text=f"Ruta actual: {current_path}", 
                                 wraplength=450)
        self.path_label.pack(pady=5)
        
        tk.Button(self.main_frame, text="Seleccionar Carpeta ItemsAdder", 
                 command=self.select_itemsadder_path).pack(pady=5)

        ttk.Separator(self.main_frame, orient='horizontal').pack(fill=tk.X, pady=10)

        tk.Label(self.main_frame, text="Gestionar Proyectos (Namespaces)", 
                font=("Helvetica", 14, "bold")).pack(pady=10)

        self.project_list_frame = tk.Frame(self.main_frame)
        self.project_list_frame.pack(pady=10, fill=tk.X)
        self.update_project_list()

        button_add_project = tk.Button(self.main_frame, text="Añadir Nuevo Proyecto", 
                                     command=self.add_new_project)
        button_add_project.pack(pady=10)

    def select_itemsadder_path(self):
        """Permite al usuario seleccionar la carpeta base de ItemsAdder."""
        selected_path = filedialog.askdirectory(title="Seleccionar la Carpeta que contiene 'contents/'")
        if selected_path:
            # Verificar si la carpeta 'contents' existe dentro de la ruta seleccionada
            contents_path = os.path.join(selected_path, "contents")
            if os.path.isdir(contents_path):
                # Actualizar configuración
                self.base_path = selected_path
                self.config["itemsadder_base_path"] = selected_path
                save_config(self.config)
                
                self.path_label.config(text=f"Ruta actual: {selected_path}")
                self.update_project_list()  # Actualizar lista de proyectos
                messagebox.showinfo("Ruta ItemsAdder", "¡Ruta de ItemsAdder configurada exitosamente!")
            else:
                messagebox.showwarning("Ruta Inválida", 
                                      "La carpeta seleccionada no parece contener la estructura de ItemsAdder (no se encontró 'contents/').")

    def update_project_list(self):
        for widget in self.project_list_frame.winfo_children():
            widget.destroy()

        # Obtener la lista de proyectos (namespaces) desde el sistema de archivos
        if not self.base_path:
            tk.Label(self.project_list_frame, text="Selecciona una ruta base para ver los proyectos.").pack()
            return

        self.projects = itemsadder.find_namespaces(self.base_path)
        if not self.projects:
            tk.Label(self.project_list_frame, text="No hay proyectos. ¡Añade uno!").pack()
        else:
            for project_name in self.projects:
                btn = tk.Button(self.project_list_frame, text=project_name,
                              command=lambda name=project_name: self.open_project(name))
                btn.pack(fill=tk.X, pady=2)

    def add_new_project(self):
        if not self.base_path:
            messagebox.showwarning("Ruta Base Requerida", "Por favor, selecciona la carpeta raíz de ItemsAdder primero.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Añadir Nuevo Proyecto")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()

        tk.Label(dialog, text="Nombre del Nuevo Proyecto (Namespace):").pack(pady=10)
        entry_name = tk.Entry(dialog, width=30)
        entry_name.pack(pady=5)
        entry_name.focus_set()  # Pone el foco en el campo de entrada

        def confirm_add():
            new_name = entry_name.get().strip()
            if not new_name:
                messagebox.showwarning("Entrada Vacía", "Por favor, ingresa un nombre para el proyecto.")
                return

            # Crear la estructura de carpetas y archivos
            try:
                itemsadder.create_namespace_structure(self.base_path, new_name)
                self.update_project_list()  # Actualizar lista
                dialog.destroy()
                messagebox.showinfo("Proyecto Añadido", f"Proyecto '{new_name}' creado exitosamente.")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear el proyecto: {e}")

        button_confirm = tk.Button(dialog, text="Crear Proyecto", command=confirm_add)
        button_confirm.pack(pady=5)

        self.wait_window(dialog)

    def open_project(self, project_name):
        if not self.base_path:
            messagebox.showwarning("Ruta Base Requerida", 
                                  "Por favor, selecciona la carpeta raíz de ItemsAdder antes de abrir un proyecto.")
            return

        self.withdraw()
        ProjectPage(self, project_name, self.base_path)