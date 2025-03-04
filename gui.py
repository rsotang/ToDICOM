import PySimpleGUI as sg

def create_info_window():
        # Layout para el primer frame con información de la versión
    frame1_layout = [
        [sg.Text("DICOM_TO_DICOM - HCUV", font='Arial 12 bold ')],
        [sg.Text("Versión: 0.1")],
        [sg.Text("Fecha de versión: 28 de febrero de 2025")]
    ]
    
    # Layout para el segundo frame con texto más largo y scrolleable
    frame2_layout = [
        [sg.Multiline("- - - - - - - - - - - - - - -DOCUMENTACIÓN- - - - - - - - - - - - - - -\n\n"
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
                      "Si se cambia de modalidad estas variables se reinician\n",
                      size=(50, 15), 
                      key="text_area", 
                      autoscroll=True, 
                      expand_x=True, 
                      expand_y=True, disabled=True),]
    ]
    
    # Layout principal con ambos frames en paralelo
    layout = [
        [sg.Frame("Información de la aplicación", frame1_layout),
         sg.Frame("Docs", frame2_layout, size=(400, 200))]
    ]  
        

    
    return sg.Window('Información aplicación', layout, finalize=True)

###############################################################################

# Función para crear la ventana de opciones
def create_options_window(advanced_options):
    textos = [
        'Plantilla CT:',
        'Plantilla SPECT:',
        'Plantilla PET:',
        'Plantilla MRI:',
        'Plantilla RTDOSE:'
    ]
    
    keys = ['-CT-', '-SPECT-', '-PET-', '-MRI-', '-RTDOSE-']
    
    layout = [
        [sg.Text('Ubicaciones de plantillas', font=('Arial', 14), justification='center', expand_x=True)],
        *[[sg.Text(texto, size=(12, 1)), sg.Input(default_text=advanced_options[key[1:-1]], size=(40, 1), key=key), sg.FileBrowse('Seleccionar', target=key)] for texto, key in zip(textos, keys)],
        [sg.Push(), sg.Button('Guardar'), sg.Button('Salir'), sg.Push()]
    ]
    
    return sg.Window('Opciones', layout, finalize=True)


###############################################################################
# Funciónes para crear la ventana de modalidad y las categorías de las etiquetas.
def create_modality_window(categories):
    """Crea la ventana principal con las opciones de categorías."""
    layout = [
        [sg.Text('Seleccione la categoría de etiquetas a editar:', font=('Helvetica', 14))],
        *[[sg.Button(f'Editar etiquetas de {category}', size=(25, 1))] for category in categories],
        [sg.Push(), sg.Button('Salir', size=(10, 1)), sg.Push()]
    ]
    return sg.Window('Categorías de etiquetas DICOM', layout, finalize=True)
###############################################################################
def create_tag_window(category_name, tags):
    """Crea una ventana de PySimpleGUI con las etiquetas DICOM como opciones."""
    
    column_layout = []
    for tag in tags:
        tag_name, tag_id, tag_value = tag
        column_layout.append([
            sg.Text(f'{tag_name} ({tag_id})', size=(30, 1)),  # Texto de la etiqueta
            sg.Checkbox('', key=f'-CHECK-{tag_id}-', enable_events=True),  # Casilla clickable
            sg.Input(str(tag_value), size=(25, 1), key=f'-INPUT-{tag_id}-', background_color='lightgray', disabled=True)  # Cuadro de texto
        ])

    column = sg.Column(column_layout, scrollable=True, vertical_scroll_only=True, size=(600, 400))

    layout = [
        [sg.Text(f'Opciones para {category_name}', font=('Helvetica', 14))],
        [column],  # Columna desplazable
        [sg.Push(), sg.Button('Aceptar', size=(10, 1)), sg.Button('Cancelar', size=(10, 1)), sg.Push()]
    ]

    return sg.Window(f'Editar {category_name}', layout, finalize=True)




