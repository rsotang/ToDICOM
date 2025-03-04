from datetime import datetime
import PySimpleGUI as sg
import utils
from utils import category_mappings as category_mappings
import pydicom
from pathlib import Path
import sys
import tempfile
import gui

# Base directory para rutas relativas (soporta ejecución como ejecutable)
if getattr(sys, 'frozen', False):
    # Si está congelado en un ejecutable
    BASE_DIR = Path(sys._MEIPASS)
else:
    # Si está ejecutándose como script normal
    BASE_DIR = Path(__file__).resolve().parent

# Carpetas temporales para input/output
temp_dir = Path(tempfile.gettempdir())
input_dir = temp_dir / 'DICOM_TO_DICOM' / 'input'
output_dir = temp_dir / 'DICOM_TO_DICOM' / 'output'

# Asegurarse de que los directorios de input/output existan
input_dir.mkdir(parents=True, exist_ok=True)
output_dir.mkdir(parents=True, exist_ok=True)


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
    [sg.Text('DICOM_TO_DICOM', font=('Helvetica', 18), justification='center', expand_x=True)],
    
    [sg.Frame('Directorios', [
        [sg.Text('Entrada:', size=(15, 1)), 
         sg.Input(default_text=str(input_dir), key='-INPUT_DIR-', size=(40, 1)), 
         sg.FolderBrowse('Seleccionar')],
        [sg.Text('Salida:', size=(15, 1)), 
         sg.Input(default_text=str(output_dir), key='-OUTPUT_DIR-', size=(40, 1)), 
         sg.FolderBrowse('Seleccionar')]
    ])],
    
    [sg.Frame('Configuración de Modalidad', [
        [sg.Text('Modalidad de entrada:', size=(18, 1)), 
         sg.Combo(['DICOM', '.mat', '.npy'], key='-MODALITY_IN-', enable_events=True, size=(15, 1))],
        [sg.Text('Modalidad de salida:', size=(18, 1)), 
         sg.Combo(['', 'CT', 'SPECT', 'PET', 'MRI', 'RTDOSE'], key='-MODALITY_OUT-', enable_events=True, size=(15, 1))],
        [sg.Text('Tipo de Volumen:', size=(18, 1)), 
         sg.Combo(['slices', '3D'], key='-INPUT_MODE-', size=(15, 1))],
        [sg.Button('Opciones Etiquetas DICOM', key='-MODALITY_OUT_OPTIONS-', disabled=True, size=(20, 1))]
    ])],
    
    [sg.Frame('Información archivo', [
        [sg.Checkbox('Actualizar fecha del estudio', key='-UPDATE_DATE-'), 
         sg.Checkbox('Actualizar hora del estudio', key='-UPDATE_TIME-')],
        [sg.Text('Nombre del archivo de salida:', size=(20, 1)), 
         sg.Input(default_text='default_output_name', key='-FILE_OUT_NAME-', size=(25, 1))]
    ])],
    
    [sg.Button('Ubicación Plantillas', key='-OPTIONS-', size=(15, 1)), 
     sg.Button('Info aplicación', key='-INFO-', size=(15, 1)), sg.Push(),
     sg.Button('Iniciar', key='-START-', button_color=('white', 'red'), size=(15, 1))]
]


# Opciones avanzadas con rutas relativas a la base del script o ejecutable
advanced_options = {
    'CT': (BASE_DIR / 'Plantilla CT' / 'Plantilla_CT.dcm').as_posix(),
    'SPECT': (BASE_DIR / 'Plantilla SPECT' / 'Plantilla_SPECT.dcm').as_posix(),
    'PET': (BASE_DIR / 'Plantilla PET' / 'Plantilla_PET.dcm').as_posix(),
    'MRI': (BASE_DIR / 'Plantilla MRI' / 'Plantilla_MRI.dcm').as_posix(),
    'RTDOSE': (BASE_DIR / 'Plantilla RTDOSE' / 'Plantilla_RTDOSE.dcm').as_posix()
}
#print(advanced_options)

# Convertir todas las rutas a string (pydicom y otras librerías esperan cadenas)
advanced_options = {key: str(path) for key, path in advanced_options.items()}

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

    if event == '-INFO-':
        info_window = gui.create_info_window()
        while True:
            info_event, info_values = info_window.read()
            if info_event == sg.WIN_CLOSED:
                break
        info_window.close()
    
    # Abrir ventana de opciones
    if event == '-OPTIONS-':
        options_window = gui.create_options_window(advanced_options)
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

    # Variable global para almacenar la última modalidad seleccionada
    last_modality = None

    # Habilitar botón de opciones de modalidad cuando se selecciona una modalidad
    if event == '-MODALITY_OUT-':
        window['-MODALITY_OUT_OPTIONS-'].update(disabled=False)
        temp_modality = values['-MODALITY_OUT-']
        
        # Verificar si la modalidad ha cambiado
        if temp_modality != last_modality:
            # Reiniciar la variable global categorized_tags
            categorized_tags = {}
            tag_updates = {}
            last_modality = temp_modality  # Actualizar la última modalidad seleccionada

    # Abrir ventana de opciones de modalidad
    if event == '-MODALITY_OUT_OPTIONS-':
        modality = values['-MODALITY_OUT-']
     
        # Leer las etiquetas DICOM
        tags = utils.read_dicom_tags(advanced_options[values['-MODALITY_OUT-']])   
       
        
        #print(category_mappings[modality])
        # Clasificar las etiquetas por categorías usando el mapeo correspondiente
        # Si es la primera vez que se ejecuta o se cambia de modalidad, actualizar categorized_tags
        
        if not categorized_tags:
            categorized_tags = utils.categorize_tags(tags, category_mappings[modality])
            #print(categorized_tags)
        modality_window = gui.create_modality_window(categorized_tags.keys())
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
                tag_window = gui.create_tag_window(category, categorized_tags[category])
    
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
                               
                               tag_updates.update(utils.process_tag_values_and_update_dicom(dicom_template_path, category, categorized_tags, tag_values))
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
                matrix = utils.load_slices_from_dicom(input_dir,input_mode)
            elif values['-MODALITY_IN-'] == '.mat':
                matrix = utils.load_slices_from_mat(input_dir)
                
            elif values['-MODALITY_IN-'] == '.npy':
                matrix = utils.load_slices_from_npy(input_dir)
            
            
            file_name = values['-FILE_OUT_NAME-']
            # Llamar a la función para volcar la matriz en archivos DICOM
            utils.save_slices_from_matrix(dicom_template_path, output_dir,file_name ,matrix,tag_updates)
              
            
            sg.popup('Éxito', 'El script se ejecutó correctamente.')
    
        except Exception as e:
            sg.popup('Error', f'Ocurrió un error al ejecutar el script:\n{str(e)}')
    
#%%      