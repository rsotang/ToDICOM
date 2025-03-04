import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import filedialog

def create_info_window():
    root = tk.Tk()
    root.title('Información aplicación')

    # Frame para la información de la versión
    frame1 = ttk.LabelFrame(root, text="Información de la aplicación")
    frame1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    ttk.Label(frame1, text="DICOM_TO_DICOM - HCUV", font=('Arial', 12, 'bold')).grid(row=0, column=0, sticky="w")
    ttk.Label(frame1, text="Versión: 0.1").grid(row=1, column=0, sticky="w")
    ttk.Label(frame1, text="Fecha de versión: 28 de febrero de 2025").grid(row=2, column=0, sticky="w")

    # Frame para la documentación
    frame2 = ttk.LabelFrame(root, text="Docs")
    frame2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    text_area = scrolledtext.ScrolledText(frame2, wrap=tk.WORD, width=50, height=15, state='disabled')
    text_area.grid(row=0, column=0, sticky="nsew")

    text_area.config(state='normal')
    text_area.insert(tk.INSERT, "- - - - - - - - - - - - - - -DOCUMENTACIÓN- - - - - - - - - - - - - - -\n\n"
                      "Este script permite crear objetos DICOM a partir de otros objetos DICOM o matrices 3D.\n\n"
                      "El flujo de trabajo es el siguiente: \n \n"
                      "Selección del directorio donde se encuentran los archivos que queremos manipular\n"
                      "Seleccion del directorio donde se depositan los nuevos archivos\n"
                      "Selección de la modalidad de entrada:\n\n"
                      "   DICOM para imagenes que queramos cambiar de modalidad\n"
                      "   .mat para matrices 3D creadas con MATLAB\n"
                      "   .npy para matrices creadas como variables de Numpy en python\n\n"
                      "Especificación del tipo de volumen:\n\n"
                      "   slices si el volumen se encuentra en un archivo por corte\n"
                      "   3D si el volumen tiene todas sus slices en un único archivo\n\n"
                      "El botón Opciones etiquetas DICOM permite editar las etiquetas DICOM de la plantilla para generar un archivo nuevo personalizado \n"
                      "Aparecen agrupadas en paquetes, y con valores por defecto\n"
                      "Adicionalmente se pueden actualizar las fechas y horas del estudio al momento de ejecución del script, en las etiquetas DICOM correspondiente sin su edición manual\n"
                      "\n\n"
                      "El funcionamiento del script consta de los siguientes pasos\n"
                      "Primero se extrae/importa la información de los datos de entrada y se vuelcan en una matriz temporal\n"
                      "Cuando se abre la ventana de opciones se leen las etiquetas DICOM de la plantilla y se categorizan. \n  "
                      "Cada vez que se cambia alguna etiqueta se almacena en un diccionario temporal.\n"
                      "Cuando damos a iniciar se cambian las etiquetas del diccionario y la matriz con funciones de pydicom\n"
                      "Si se cambia de modalidad estas variables se reinician\n")
    text_area.config(state='disabled')

    root.mainloop()

###############################################################################

# Función para crear la ventana de opciones
def create_options_window(advanced_options):
    root = tk.Tk()
    root.title('Opciones')

    ttk.Label(root, text='Ubicaciones de plantillas', font=('Arial', 14)).grid(row=0, column=0, columnspan=3, pady=10)

    textos = [
        'Plantilla CT:',
        'Plantilla SPECT:',
        'Plantilla PET:',
        'Plantilla MRI:',
        'Plantilla RTDOSE:'
    ]
    
    keys = ['-CT-', '-SPECT-', '-PET-', '-MRI-', '-RTDOSE-']
    
    entries = {}
    for i, (texto, key) in enumerate(zip(textos, keys)):
        ttk.Label(root, text=texto).grid(row=i+1, column=0, padx=5, pady=5)
        entry = ttk.Entry(root, width=40)
        entry.grid(row=i+1, column=1, padx=5, pady=5)
        entry.insert(0, advanced_options[key[1:-1]])
        entries[key] = entry
        ttk.Button(root, text='Seleccionar', command=lambda k=key: browse_file(entries[k])).grid(row=i+1, column=2, padx=5, pady=5)

    ttk.Button(root, text='Guardar', command=lambda: save_options(entries)).grid(row=len(textos)+1, column=1, pady=10)
    ttk.Button(root, text='Salir', command=root.destroy).grid(row=len(textos)+1, column=2, pady=10)

    def browse_file(entry):
        filename = filedialog.askopenfilename()
        entry.delete(0, tk.END)
        entry.insert(0, filename)

    def save_options(entries):
        for key, entry in entries.items():
            advanced_options[key[1:-1]] = entry.get()
        print("Opciones guardadas:", advanced_options)

    root.mainloop()


###############################################################################
# Funciónes para crear la ventana de modalidad y las categorías de las etiquetas.

def create_modality_window(categories):
    root = tk.Tk()
    root.title('Categorías de etiquetas DICOM')

    ttk.Label(root, text='Seleccione la categoría de etiquetas a editar:', font=('Helvetica', 14)).grid(row=0, column=0, pady=10)

    for i, category in enumerate(categories):
        ttk.Button(root, text=f'Editar etiquetas de {category}', command=lambda c=category: edit_category(c)).grid(row=i+1, column=0, pady=5)

    ttk.Button(root, text='Salir', command=root.destroy).grid(row=len(categories)+1, column=0, pady=10)

    def edit_category(category):
        print(f"Editando categoría: {category}")
        # Aquí puedes abrir una nueva ventana para editar las etiquetas de la categoría seleccionada

    root.mainloop()
    
###############################################################################
def create_tag_window(category_name, tags):
    root = tk.Tk()
    root.title(f'Editar {category_name}')

    ttk.Label(root, text=f'Opciones para {category_name}', font=('Helvetica', 14)).grid(row=0, column=0, pady=10)

    canvas = tk.Canvas(root)
    canvas.grid(row=1, column=0, sticky="nsew")

    scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollbar.grid(row=1, column=1, sticky="ns")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    frame = ttk.Frame(canvas)
    canvas.create_window((0, 0), window=frame, anchor="nw")

    entries = {}
    for i, (tag_name, tag_id, tag_value) in enumerate(tags):
        ttk.Label(frame, text=f'{tag_name} ({tag_id})', size=(30, 1)).grid(row=i, column=0, padx=5, pady=5)
        chk_var = tk.BooleanVar()
        ttk.Checkbutton(frame, variable=chk_var, command=lambda id=tag_id: toggle_entry(entries[id], chk_var)).grid(row=i, column=1, padx=5, pady=5)
        entry = ttk.Entry(frame, width=25)
        entry.grid(row=i, column=2, padx=5, pady=5)
        entry.insert(0, str(tag_value))
        entry.config(state='disabled')
        entries[tag_id] = (entry, chk_var)

    ttk.Button(root, text='Aceptar', command=lambda: save_tags(entries)).grid(row=2, column=0, pady=10)
    ttk.Button(root, text='Cancelar', command=root.destroy).grid(row=2, column=1, pady=10)

    def toggle_entry(entry, chk_var):
        entry[0].config(state='normal' if chk_var.get() else 'disabled')

    def save_tags(entries):
        for tag_id, (entry, chk_var) in entries.items():
            if chk_var.get():
                print(f"Guardando {tag_id}: {entry.get()}")

    root.mainloop()




