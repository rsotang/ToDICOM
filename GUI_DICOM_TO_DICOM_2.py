from datetime import datetime
import PySimpleGUI as sg
import D_to_D_aux_functions.load_and_save_slices as aux
import D_to_D_aux_functions.categorized_tags as aux_tags
from  D_to_D_aux_functions.categorized_tags import category_mappings as category_mappings



# Función para crear la ventana de opciones
def create_options_window():
    textos = [
        'Ubicación plantilla CT:',
        'Ubicación plantilla SPECT:',
        'Ubicación plantilla PET:',
        'Ubicación plantilla MRI:',
        'Ubicación plantilla RTDOSE:'
    ]
    max_length = max(len(texto) for texto in textos)
    layout = [
        [sg.Text('Opciones avanzadas')],
        [sg.Text(textos[0]),sg.Push(),  sg.Text(textos[1]), sg.Push(), sg.Text(textos[2]),sg.Push(),  sg.Text(textos[3]), sg.Push(), sg.Text(textos[4])],
        [
            sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla CT/Plantilla_CT.dcm',size=(max_length, 1), key='-CT-'), 
            sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla SPECT/Plantilla_SPECT.dcm',size=(max_length, 1), key='-SPECT-'),
            sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla PET/Plantilla_PET.dcm',size=(max_length, 1), key='-PET-'),
            sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla MRI/Plantilla_MRI.dcm',size=(max_length, 1), key='-MRI-'),
            sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/PLantilla RTDose/Plantilla_RTDOSE.dcm',size=(max_length, 1), key='-RTDOSE-')
        ],
        [
            sg.FileBrowse('Seleccionar', target='-CT-'),sg.Push(),
            sg.FileBrowse('Seleccionar', target='-SPECT-'), sg.Push(),
            sg.FileBrowse('Seleccionar', target='-PET-'), sg.Push(),
            sg.FileBrowse('Seleccionar', target='-MRI-'),sg.Push(),
            sg.FileBrowse('Seleccionar', target='-RTDOSE-')
        ],
        [sg.Button('Guardar'), sg.Button('Salir')]
    ]
    return sg.Window('Opciones', layout, element_justification='c',finalize=True)

# Funciónes para crear la ventana de modalidad y las categorias de las etiquetas.

def create_modality_window(categories):
    """Crea la ventana principal con las opciones de categorías."""
    layout = [
        [sg.Text('Seleccione la categoría de etiquetas a editar:')],
        *[[sg.Button(f'Editar etiquetas de {category}')] for category in categories],
        [sg.Button('Cancelar')]
    ]
    return sg.Window('Categorías de etiquetas DICOM', layout, finalize=True)

def create_tag_window(category_name, tags):
    """Crea una ventana de PySimpleGUI con las etiquetas DICOM como opciones."""
    
    column_layout = []
    # Añadir una fila por cada etiqueta DICOM
    for tag in tags:
        tag_name, tag_id, tag_value = tag
        column_layout.append([
            sg.Text(f'{tag_name} ({tag_id})', size=(25, 1)),  # Texto de la etiqueta
            sg.Checkbox('', key=f'-CHECK-{tag_id}-', enable_events=True),  # Casilla clickable
            sg.Input(str(tag_value), size=(20, 1), key=f'-INPUT-{tag_id}-', background_color='black',disabled=True)  # Cuadro de texto
        ])

    # Hacer que la columna sea desplazable
    column = sg.Column(column_layout, scrollable=True, vertical_scroll_only=True, size=(600, 400))

    # Diseño final de la ventana
    layout = [
        [sg.Text(f'Opciones para {category_name}')],
        [column],  # Añadir la columna desplazable
        [sg.Button('Aceptar'), sg.Button('Cancelar')]
    ]

    return sg.Window(f'Editar {category_name}', layout, finalize=True)
#%% LAYOUTS VENTANA PRINCIPAL Y RUTAS DE LAS PLANTILLAS, TEMA ESTETICO DEL GUI 

new_theme = {"BACKGROUND": '#DAE0E6', "TEXT": sg.COLOR_SYSTEM_DEFAULT, "INPUT": sg.COLOR_SYSTEM_DEFAULT,
             "TEXT_INPUT": sg.COLOR_SYSTEM_DEFAULT, "SCROLL": sg.COLOR_SYSTEM_DEFAULT,
             "BUTTON": sg.OFFICIAL_PYSIMPLEGUI_BUTTON_COLOR, "PROGRESS": sg.COLOR_SYSTEM_DEFAULT, "BORDER": 1,
             "SLIDER_DEPTH": 1, "PROGRESS_DEPTH": 0
             }

sg.theme_add_new('MyTheme', new_theme)
sg.theme('MyTheme')

# Layout de la ventana principal
layout = [
    [sg.Push(), sg.Text('DICOM_to_DICOM', font=('Helvetica', 16)), sg.Push()],
    [sg.Text('Directorio de entrada:'), sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/input', key= '-INPUT_DIR-',size=(10, 10)), sg.FolderBrowse('Seleccionar'), sg.Text('Directorio de salida:'), sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/output', key='-OUTPUT_DIR-', size=(10, 10)), sg.FolderBrowse('Seleccionar')],
    [],
    [sg.Text('Modalidad de imagen de entrada:'), sg.Combo([' ', 'CT', 'SPECT', 'PET', 'MRI', 'RTDOSE', '.mat'], key='-MODALITY_IN-', enable_events=True), sg.Push(), sg.Text('Modalidad de imagen de salida:'), sg.Combo(['', 'CT', 'SPECT', 'PET', 'MRI', 'RTDOSE'], key='-MODALITY_OUT-', enable_events=True)],
    [],
    [sg.Push(), sg.Push(), sg.Button('Opciones Etiquetas DICOM de Modalidad', key='-MODALITY_OUT_OPTIONS-', disabled=True)],
    [sg.Push(), sg.Push(), sg.Text('Nombre del archivo'),sg.Input(default_text='default_output_name',key='-FILE_OUT_NAME-',size=(20,10))],
    [sg.Button('Opciones', key='-OPTIONS-'), sg.Push(), sg.Button('Iniciar', key='-START-')]
]

advanced_options = {
    'CT': 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla CT/Plantilla_CT.dcm',
    'SPECT': 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla SPECT/Plantilla_SPECT.dcm',
    'PET': 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla PET/Plantilla_PET.dcm',
    'MRI': 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla MRI/Plantilla_MRI.dcm',
    'RTDOSE': 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/PLantilla RTDose/Plantilla_RTDOSE.dcm'
}

# Crear la ventana principal
window = sg.Window('Software de Procesamiento de Imágenes', layout)

# Variables globales para almacenar los valores de las opciones avanzadas

# Bucle de eventos
#%%

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break

    # Abrir ventana de opciones
    if event == '-OPTIONS-':
        options_window = create_options_window()
        while True:
            opt_event, opt_values = options_window.read()
            if opt_event in (sg.WIN_CLOSED, 'Salir'):
                break
            if opt_event == 'Guardar':
                advanced_options['CT'] = opt_values['CT']
                advanced_options['SPECT'] = opt_values['SPECT']
                advanced_options['PET'] = opt_values['PET']
                advanced_options['MRI'] = opt_values['MRI']
                advanced_options['RTDOSE'] = opt_values['RTDOSE']
                sg.popup('Opciones guardadas')              
                break
        options_window.close()

    # Habilitar botón de opciones de modalidad cuando se selecciona una modalidad
    if event == '-MODALITY_OUT-':
        window['-MODALITY_OUT_OPTIONS-'].update(disabled=False)

    # Abrir ventana de opciones de modalidad
    if event == '-MODALITY_OUT_OPTIONS-':
        modality = values['-MODALITY_OUT-']
        # Leer las etiquetas DICOM
        tags = aux_tags.read_dicom_tags(advanced_options[values['-MODALITY_OUT-']])   
        
        # Clasificar las etiquetas por categorías usando el mapeo correspondiente
        categorized_tags = aux_tags.categorize_tags(tags, category_mappings[modality])
        
        
        modality_window = create_modality_window(categorized_tags.keys())
        tag_window = None
        tag_updates={}
        try:
            dicom_template_path = advanced_options[values['-MODALITY_OUT-']]        
           
        except Exception as e:
            sg.popup('Error', f'Ocurrió un error al obtener la plantilla:\n{str(e)}')
            continue
        
        while True:
            event, values = modality_window.read()
            if event == sg.WIN_CLOSED or event == 'Cancelar':
                break
            elif event.startswith('Editar etiquetas de '):
                category = event.replace('Editar etiquetas de ', '')
                tag_window = create_tag_window(category, categorized_tags[category])

            # Si se abrió una ventana de edición de etiquetas
            if tag_window:
                while True:
                    tag_event, tag_values = tag_window.read()
                    if tag_event == sg.WIN_CLOSED or tag_event == 'Cancelar':
                        tag_window.close()
                        tag_window = None
                        break
                    elif tag_event == 'Aceptar':
                        # Aquí puedes procesar los valores seleccionados
                        print("Valores seleccionados:")
                        for tag in categorized_tags[category]:  # Cambiar según la categoría
                            tag_name, tag_id, _ = tag
                            if tag_values[f'-CHECK-{tag_id}-']:
                                print(f'{tag_name}: {tag_values[f'-INPUT-{tag_id}-']}')
                                tag_updates.update(aux.process_tag_values_and_update_dicom(dicom_template_path, category, categorized_tags, tag_values))
                        break
                    # Habilitar/deshabilitar el cuadro de texto cuando se marca/desmarca la casilla
                    for tag in categorized_tags[category]:  # Cambiar según la categoría
                        tag_name, tag_id, _ = tag
                        if tag_event == f'-CHECK-{tag_id}-':
                            tag_window[f'-INPUT-{tag_id}-'].update(disabled=not tag_values[f'-CHECK-{tag_id}-'], background_color='white')

        modality_window.close()

    # Iniciar la ejecución de scripts y mostrar la ventana de progreso
    if event == '-START-':
        input_dir = values['-INPUT_DIR-']
        output_dir = values['-OUTPUT_DIR-']
        modality = values['-MODALITY_OUT-']
        
    
        if not input_dir or not output_dir or not dicom_template_path:
            sg.popup('Error', 'Por favor, complete todos los campos obligatorios.')
            continue    
    
    
        try:
            # Cargar la matriz 3D a partir de las imágenes DICOM en la carpeta de entrada
            matrix = aux.load_slices_from_dicom(input_dir)
            file_name = values['-FILE_OUT_NAME-']
            # Llamar a la función para volcar la matriz en archivos DICOM
            aux.save_slices_from_matrix(dicom_template_path, output_dir,file_name ,matrix,tag_updates)
              
            
            sg.popup('Éxito', 'El script se ejecutó correctamente.')
    
        except Exception as e:
            sg.popup('Error', f'Ocurrió un error al ejecutar el script:\n{str(e)}')
    
#%%      