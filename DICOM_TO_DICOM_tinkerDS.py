import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import utils
from utils import category_mappings as category_mappings
import pydicom
from pathlib import Path
import sys
import tempfile
import gui_tkinter
from functools import partial

# Base directory para rutas relativas (soporta ejecución como ejecutable)
if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys._MEIPASS)
else:
    BASE_DIR = Path(__file__).resolve().parent

advanced_options = {
    'CT': (BASE_DIR / 'Plantilla CT' / 'Plantilla_CT.dcm').as_posix(),
    'SPECT': (BASE_DIR / 'Plantilla SPECT' / 'Plantilla_SPECT.dcm').as_posix(),
    'PET': (BASE_DIR / 'Plantilla PET' / 'Plantilla_PET.dcm').as_posix(),
    'MRI': (BASE_DIR / 'Plantilla MRI' / 'Plantilla_MRI.dcm').as_posix(),
    'RTDOSE': (BASE_DIR / 'Plantilla RTDOSE' / 'Plantilla_RTDOSE.dcm').as_posix()
}

advanced_options = {key: str(path) for key, path in advanced_options.items()}

categorized_tags = {}
tag_updates = {}

def open_info_window():
    gui_tkinter.create_info_window()

def open_options_window():
    options_window = gui_tkinter.create_options_window(advanced_options)
    options_window.mainloop()

def open_modality_window():
    modality = modality_out_combobox.get()
    if not modality:
        messagebox.showerror("Error", "Por favor, seleccione una modalidad de salida.")
        return

    global categorized_tags
    categorized_tags = {}

    tags = utils.read_dicom_tags(advanced_options[modality])
    categorized_tags = utils.categorize_tags(tags, category_mappings[modality])

    modality_window = tk.Toplevel(root)
    modality_window.title("Categorías de etiquetas DICOM")

    ttk.Label(modality_window, text="Seleccione la categoría de etiquetas a editar:", font=('Helvetica', 14)).grid(row=0, column=0, pady=10)

    for i, category in enumerate(categorized_tags.keys()):
        ttk.Button(modality_window, text=f'Editar etiquetas de {category}', 
                   command=lambda c=category: open_tag_window(c, categorized_tags[c])).grid(row=i+1, column=0, pady=5)

    ttk.Button(modality_window, text="Salir", command=modality_window.destroy).grid(row=len(categorized_tags)+1, column=0, pady=10)
    
def open_tag_window(category_name, tags):
    tag_window = tk.Toplevel(root)
    tag_window.title(f'Editar {category_name}')

    ttk.Label(tag_window, text=f'Opciones para {category_name}', font=('Helvetica', 14)).grid(row=0, column=0, pady=10)

    canvas = tk.Canvas(tag_window)
    canvas.grid(row=1, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(tag_window, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=1, column=1, sticky="ns")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    entries = {}
    for i, (tag_name, tag_id, tag_value) in enumerate(tags):
        ttk.Label(frame, text=f'{tag_name} ({tag_id})', width=30).grid(row=i, column=0, padx=5, pady=5)
        chk_var = tk.BooleanVar()
        
        ttk.Checkbutton(frame, variable=chk_var, 
                        command=partial(toggle_entry, entries, tag_id, chk_var)).grid(row=i, column=1, padx=5, pady=5)
        
        entry = ttk.Entry(frame, width=25)
        entry.grid(row=i, column=2, padx=5, pady=5)
        entry.insert(0, str(tag_value))
        entry.config(state='disabled')
        entries[tag_id] = (entry, chk_var)

    ttk.Button(tag_window, text='Aceptar', command=lambda: save_tags(entries, category_name, tags, tag_window)).grid(row=2, column=0, pady=10)
    ttk.Button(tag_window, text='Cancelar', command=tag_window.destroy).grid(row=2, column=1, pady=10)

def toggle_entry(entries, tag_id, chk_var):
    entry = entries[tag_id][0]
    entry.config(state='normal' if chk_var.get() else 'disabled')

def save_tags(entries, category_name, tags, window):
    global categorized_tags, tag_updates
    for tag in tags:
        tag_name, tag_id, _ = tag
        if entries[tag_id][1].get():
            new_value = entries[tag_id][0].get()
            for idx, (name, id_, _) in enumerate(categorized_tags[category_name]):
                if id_ == tag_id:
                    categorized_tags[category_name][idx] = (name, id_, new_value)
            tag_updates[pydicom.tag.Tag(tag_id)] = new_value
    messagebox.showinfo("Éxito", "Etiquetas actualizadas correctamente.")
    window.destroy()

def start_processing():
    input_dir = input_dir_entry.get()
    output_dir = output_dir_entry.get()
    modality = modality_out_combobox.get()
    input_mode = input_mode_combobox.get()

    if not input_dir or not output_dir or not modality or not input_mode:
        messagebox.showerror("Error", "Por favor, complete todos los campos.")
        return

    try:
        dicom_template_path = advanced_options[modality]
    except Exception as e:
        messagebox.showerror("Error", f'Ocurrió un error al obtener la plantilla:\n{str(e)}')
        return

    try:
        if update_date_var.get() or update_time_var.get():
            now = datetime.now()
            current_date = now.strftime('%Y%m%d')
            current_time = now.strftime('%H%M%S')

            for category, tags in categorized_tags.items():
                for idx, (tag_name, tag_id, tag_value) in enumerate(tags):
                    if tag_name == 'Study Date' and update_date_var.get():
                        tag_updates[pydicom.tag.Tag('StudyDate')] = current_date
                    elif tag_name == 'Study Time' and update_time_var.get():
                        tag_updates[pydicom.tag.Tag('StudyTime')] = current_time

        if modality_in_combobox.get() == 'DICOM':
            matrix = utils.load_slices_from_dicom(input_dir, input_mode)
        elif modality_in_combobox.get() == '.mat':
            matrix = utils.load_slices_from_mat(input_dir)
        elif modality_in_combobox.get() == '.npy':
            matrix = utils.load_slices_from_npy(input_dir)

        file_name = file_out_name_entry.get()
        utils.save_slices_from_matrix(dicom_template_path, output_dir, file_name, matrix, tag_updates)

        messagebox.showinfo("Éxito", "El script se ejecutó correctamente.")

    except Exception as e:
        messagebox.showerror("Error", f'Ocurrió un error al ejecutar el script:\n{str(e)}')
        
def on_closing():
    if messagebox.askokcancel("Salir", "¿Quieres salir de la aplicación?"):
        root.quit()
        root.destroy()
        
################################################################################        
root = tk.Tk()
root.title("Software de Procesamiento de Imágenes")
# Set the theme with the theme_use method
# Create a style
style = ttk.Style(root)

# Set the theme with the theme_use method
style.theme_use('alt')  # put the theme name here, that you want to use

root.protocol("WM_DELETE_WINDOW", on_closing)

main_frame = ttk.Frame(root, padding="10")
main_frame.grid(row=0, column=0, sticky="nsew")

ttk.Label(main_frame, text="Entrada:").grid(row=0, column=0, sticky="w")
input_dir_entry = ttk.Entry(main_frame, width=40)
input_dir_entry.grid(row=0, column=1, sticky="ew")
ttk.Button(main_frame, text="Seleccionar", 
           command=lambda: [input_dir_entry.delete(0, tk.END), 
                            input_dir_entry.insert(0, filedialog.askdirectory())]
           ).grid(row=0, column=2)

ttk.Label(main_frame, text="Salida:").grid(row=1, column=0, sticky="w")
output_dir_entry = ttk.Entry(main_frame, width=40)
output_dir_entry.grid(row=1, column=1, sticky="ew")
ttk.Button(main_frame, text="Seleccionar", 
           command=lambda: [output_dir_entry.delete(0, tk.END), 
                            output_dir_entry.insert(0, filedialog.askdirectory())]
           ).grid(row=1, column=2)

ttk.Label(main_frame, text="Modalidad de entrada:").grid(row=2, column=0, sticky="w")
modality_in_combobox = ttk.Combobox(main_frame, values=['DICOM', '.mat', '.npy'], state="readonly")
modality_in_combobox.grid(row=2, column=1, sticky="ew")
modality_in_combobox.current(0)

ttk.Label(main_frame, text="Modalidad de salida:").grid(row=3, column=0, sticky="w")
modality_out_combobox = ttk.Combobox(main_frame, values=['', 'CT', 'SPECT', 'PET', 'MRI', 'RTDOSE'], state="readonly")
modality_out_combobox.grid(row=3, column=1, sticky="ew")
modality_out_combobox.current(0)

ttk.Label(main_frame, text="Tipo de Volumen:").grid(row=4, column=0, sticky="w")
input_mode_combobox = ttk.Combobox(main_frame, values=['slices', '3D'], state="readonly")
input_mode_combobox.grid(row=4, column=1, sticky="ew")
input_mode_combobox.current(0)

ttk.Button(main_frame, text="Opciones de etiquetas DICOM",command=lambda: open_modality_window()).grid(row=3, column=2)

update_date_var = tk.BooleanVar()
update_time_var = tk.BooleanVar()
ttk.Checkbutton(main_frame, text="Actualizar fecha del estudio", variable=update_date_var).grid(row=6, column=0, sticky="w")
ttk.Checkbutton(main_frame, text="Actualizar hora del estudio", variable=update_time_var).grid(row=6, column=1, sticky="w")

ttk.Label(main_frame, text="Nombre del archivo de salida:").grid(row=7, column=0, sticky="w")
file_out_name_entry = ttk.Entry(main_frame, width=25)
file_out_name_entry.grid(row=7, column=1, sticky="ew")
file_out_name_entry.insert(0, 'default_output_name')

ttk.Button(main_frame, text="Ubicación Plantillas", command=open_options_window).grid(row=8, column=0, sticky="ew")
ttk.Button(main_frame, text="Info aplicación", command=open_info_window).grid(row=8, column=1, sticky="ew")
ttk.Button(main_frame, text="Iniciar", command=start_processing, style="Accent.TButton").grid(row=8, column=2, sticky="ew")

style = ttk.Style()
style.configure("Accent.TButton", foreground="white", background="red")

root.mainloop()