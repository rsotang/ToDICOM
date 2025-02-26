from datetime import datetime
import PySimpleGUI as sg
import D_to_D_aux_functions.load_and_save_slices as aux
import D_to_D_aux_functions.categorized_tags as aux_tags
from  D_to_D_aux_functions.categorized_tags import category_mappings as category_mappings
import pydicom
import numpy as np


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
        [sg.Push(), sg.Button('Salir')]
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
    [sg.Push(), sg.Text('DICOM_TO_DICOM', font=('Helvetica', 18)), sg.Push()],
    [sg.Text('Directorio de entrada:'), sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/input', key= '-INPUT_DIR-',size=(10, 10)), sg.FolderBrowse('Seleccionar'), sg.Text('Directorio de salida:'), sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/output', key='-OUTPUT_DIR-', size=(10, 10)), sg.FolderBrowse('Seleccionar')],
    [],
    [sg.Text('Modalidad de imagen de entrada:'), sg.Combo([ 'DICOM', '.mat','.npy'], key='-MODALITY_IN-', enable_events=True), sg.Push(), sg.Text('Modalidad de imagen de salida:'), sg.Combo(['', 'CT', 'SPECT', 'PET', 'MRI', 'RTDOSE'], key='-MODALITY_OUT-', enable_events=True)],
    [],
    [sg.Text('Tipo de Volumen'), sg.Combo(['slices','3D'],key='-INPUT_MODE-'),sg.Push(), sg.Button('Opciones Etiquetas DICOM de Modalidad', key='-MODALITY_OUT_OPTIONS-', disabled=True)],
    [sg.Push(), sg.Push(), sg.Text('Nombre del archivo'),sg.Input(default_text='default_output_name',key='-FILE_OUT_NAME-',size=(20,10))],
    [sg.Push(), sg.Push(),sg.Checkbox('Actualizar fecha del estudio', key='-UPDATE_DATE-')],
    [sg.Push(), sg.Push(),sg.Checkbox('Actualizar hora del estudio', key='-UPDATE_TIME-')],
    [sg.Button('Opciones', key='-OPTIONS-'), sg.Push(), sg.Button('Iniciar', key='-START-', button_color='red')]
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
categorized_tags={}# ESTO ESRÁ DEFINIDO COMO GLOBAL PERO NO SE SI TIENE SENTIDO HACERLO
tag_updates={}

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
            if opt_event == 'Guardar' and opt_event is True:
                advanced_options['CT'] = opt_values['CT']
                advanced_options['SPECT'] = opt_values['SPECT']
                advanced_options['PET'] = opt_values['PET']
                advanced_options['MRI'] = opt_values['MRI']
                advanced_options['RTDOSE'] = opt_values['RTDOSE']
                sg.popup('Opciones guardadas')
                options_window.close()
                break
            elif opt_event == 'Guardar':
                options_window.close()
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
        # Si es la primera vez que se ejecuta o se cambia de modalidad, actualizar categorized_tags
        
        
        if not  categorized_tags:
            categorized_tags = aux_tags.categorize_tags(tags, category_mappings[modality])
        
        
        modality_window = create_modality_window(categorized_tags.keys())
        tag_window = None
        
        
        try:
            dicom_template_path = advanced_options[values['-MODALITY_OUT-']]        
           
        except Exception as e:
            sg.popup('Error', f'Ocurrió un error al obtener la plantilla:\n{str(e)}')
            continue
        
        while True:
            event, values = modality_window.read()
            if event == sg.WIN_CLOSED or event == 'Salir':
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
                        for tag in categorized_tags[category]:
                           tag_name, tag_id, _ = tag
                           
                           if tag_values[f'-CHECK-{tag_id}-']:
                               tag_window[f'-CHECK-{tag_id}-'].update(False)
                               tag_window[f'-INPUT-{tag_id}-'].update(disabled=True, background_color='black')
                               new_value = tag_values[f'-INPUT-{tag_id}-']
                               # Actualizar tag_updates
                               print(f'{tag_name}: {tag_values[f"-INPUT-{tag_id}-"]}')
                               
                               tag_updates.update(aux.process_tag_values_and_update_dicom(dicom_template_path, category, categorized_tags, tag_values))
                               # Actualizar categorized_tags
                               
                               for idx, (name, id_, _) in enumerate(categorized_tags[category]):
                                   if id_ == tag_id:
                                       categorized_tags[category][idx] = (name, id_, new_value)
                        tag_window.close()
                        
                        break
                        
                    
                    # Habilitar/deshabilitar el cuadro de texto cuando se marca/desmarca la casilla
                    for tag in categorized_tags[category]:  # Cambiar según la categoría
                        tag_name, tag_id, _ = tag
                        if tag_event == f'-CHECK-{tag_id}-':
                            tag_window[f'-INPUT-{tag_id}-'].update(disabled=not tag_values[f'-CHECK-{tag_id}-'], background_color='white')

        modality_window.close()

    # Iniciar la ejecución de scripts 
    if event == '-START-':
        input_dir = values['-INPUT_DIR-']
        output_dir = values['-OUTPUT_DIR-']
        modality = values['-MODALITY_OUT-']
        input_mode = values['-INPUT_MODE-']
        try:
            dicom_template_path = advanced_options[values['-MODALITY_OUT-']]        
           
        except Exception as e:
            sg.popup('Error', f'Ocurrió un error al obtener la plantilla:\n{str(e)}')
            continue
        
    
        if not input_dir or not output_dir or not values['-MODALITY_OUT-'] or not values['-MODALITY_IN-'] or not values['-INPUT_MODE-']:
            sg.popup('Error', 'Por favor, complete todos los campos')
            continue    
    
    
        try:           
            # Verificar si se deben actualizar la fecha y/o la hora
            if values['-UPDATE_DATE-'] or values['-UPDATE_TIME-']:
                # Obtener la fecha y hora actuales
                now = datetime.now()
                current_date = now.strftime('%Y%m%d')  # Formato DICOM para fecha (AAAAMMDD)
                current_time = now.strftime('%H%M%S')   # Formato DICOM para hora (HHMMSS)
                
                # Actualizar las etiquetas correspondientes en categorized_tags
                for category, tags in categorized_tags.items():
                    for idx, (tag_name, tag_id, tag_value) in enumerate(tags):
                        if tag_name == 'Study Date' and values['-UPDATE_DATE-']:
                            tag_updates[pydicom.tag.Tag('StudyDate')]= current_date
                        elif tag_name == 'Study Time' and values['-UPDATE_TIME-']:
                            tag_updates[pydicom.tag.Tag('StudyTime')]= current_time
                            
                            
            # Cargar la matriz 3D a partir del input en la carpeta de entrada
            if values['-MODALITY_IN-'] == 'DICOM':
                matrix = aux.load_slices_from_dicom(input_dir,input_mode)
            elif values['-MODALITY_IN-'] == '.mat':
                matrix = aux.load_slices_from_mat(input_dir)
                
            elif values['-MODALITY_IN-'] == '.npy':
                matrix = aux.load_slices_from_npy(input_dir)
            
            
            file_name = values['-FILE_OUT_NAME-']
            # Llamar a la función para volcar la matriz en archivos DICOM
            aux.save_slices_from_matrix(dicom_template_path, output_dir,file_name ,matrix,tag_updates)
              
            
            sg.popup('Éxito', 'El script se ejecutó correctamente.')
    
        except Exception as e:
            sg.popup('Error', f'Ocurrió un error al ejecutar el script:\n{str(e)}')
    
#%%      