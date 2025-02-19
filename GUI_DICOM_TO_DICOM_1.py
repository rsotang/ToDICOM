import os
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from datetime import datetime
from pydicom.uid import generate_uid
import PySimpleGUI as sg
import time

# Función para cargar las imágenes DICOM
def load_slices_from_dicom(input_folder):
    dicom_files = sorted([os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".dcm")])
    first_slice = pydicom.dcmread(dicom_files[0])
    rows, cols = first_slice.Rows, first_slice.Columns
    slices = len(dicom_files)
    matrix_3d = np.zeros((slices, rows, cols), dtype=np.int16)
    for i, dicom_file in enumerate(dicom_files):
        ds = pydicom.dcmread(dicom_file)
        matrix_3d[i, :, :] = ds.pixel_array
    return matrix_3d

# Función para guardar las imágenes DICOM
def save_slices_from_matrix(dicom_template_path, output_folder, matrix_3d, study_date, patient_name="Anon"):
    template_ds = pydicom.dcmread(dicom_template_path)
    slices, rows, cols = matrix_3d.shape
    if (rows, cols) != (template_ds.Rows, template_ds.Columns):
        print(f"Las dimensiones de la matriz ({rows}x{cols}) no coinciden con la plantilla DICOM ({template_ds.Rows}x{template_ds.Columns}). Ajustando plantilla...")
        template_ds.Rows = rows
        template_ds.Columns = cols
    os.makedirs(output_folder, exist_ok=True)
    new_study_uid = generate_uid()
    new_series_uid = generate_uid()
    for i in range(slices):
        new_ds = template_ds.copy()
        new_ds.PatientName = patient_name
        new_ds.StudyDate = study_date
        new_ds.StudyInstanceUID = new_study_uid
        new_ds.SeriesInstanceUID = new_series_uid
        new_ds.SOPInstanceUID = generate_uid()
        new_ds.InstanceNumber = i + 1
        new_ds.ImagePositionPatient = [0, 0, i]
        new_ds.SliceLocation = i
        new_ds.PixelData = matrix_3d[i].astype(np.int16).tobytes()
        new_ds.RescaleIntercept = 0
        new_ds.RescaleSlope = 1
        output_path = os.path.join(output_folder, f"slice_{i+1:03d}.dcm")
        new_ds.save_as(output_path)
        print(f"Guardado: {output_path}")

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

# Función para crear la ventana de modalidad
def create_modality_window(modality):
    if modality == 'CT':
        opciones = ['Opción CT 1', 'Opción CT 2', 'Opción CT 3']
    elif modality == 'SPECT':
        opciones = ['Opción SPECT 1', 'Opción SPECT 2']
    elif modality == 'PET':
        opciones = ['Opción PET 1', 'Opción PET 2', 'Opción PET 3']
    elif modality == 'MRI':
        opciones = ['Opción MRI 1', 'Opción MRI 2']
    elif modality == 'RTDOSE':
        opciones = ['Opción RTDOSE 1', 'Opción RTDOSE 2', 'Opción RTDOSE 3']
    else:
        opciones = ['Opción Genérica 1', 'Opción Genérica 2']
    layout = [
        [sg.Text(f'Opciones para {modality}')],
        [sg.Text('Seleccione una opción:')]
    ]
    for opcion in opciones:
        layout.append([
            sg.Text(opcion),
            sg.Checkbox('', key=f'-CHECK-{opcion}-', enable_events=True),
            sg.Input('', size=(20, 1), key=f'-INPUT-{opcion}-', disabled=True, background_color='#636363')
        ])
    layout.append([sg.Button('Aceptar'), sg.Button('Cancelar')])
    return sg.Window(f'Opciones de {modality}', layout, finalize=True)

# Función para crear la ventana de progreso
def create_progress_window():
    layout = [
        [sg.Text('Procesando...')],
        [sg.ProgressBar(100, orientation='h', size=(20, 20), key='-PROGRESS-')],
        [sg.Button('Cerrar', key='-CLOSE-', disabled=True)]
    ]
    return sg.Window('Progreso', layout, finalize=True)

# Layout de la ventana principal
layout = [
    [sg.Push(), sg.Text('DICOM_to_DICOM', font=('Helvetica', 16)), sg.Push()],
    [sg.Text('Directorio de entrada:'), sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/input', key= '-INPUT_DIR-',size=(10, 10)), sg.FolderBrowse('Seleccionar'), sg.Text('Directorio de salida:'), sg.Input(default_text='D:/Utilidades/DICOM_TO_DICOM/ToDICOM/output', key='-OUTPUT_DIR-', size=(10, 10)), sg.FolderBrowse('Seleccionar')],
    [],
    [sg.Text('Modalidad de imagen de entrada:'), sg.Combo([' ', 'CT', 'SPECT', 'PET', 'MRI', 'RTDOSE', '.mat'], key='-MODALITY_IN-', enable_events=True), sg.Push(), sg.Text('Modalidad de imagen de salida:'), sg.Combo(['', 'CT', 'SPECT', 'PET', 'MRI', 'RTDOSE'], key='-MODALITY_OUT-', enable_events=True)],
    [],
    [sg.Push(), sg.Push(), sg.Button('Opciones Etiquetas DICOM de Modalidad', key='-MODALITY_OUT_OPTIONS-', disabled=True)],
    [],
    [sg.Button('Opciones', key='-OPTIONS-'), sg.Push(), sg.Button('Iniciar', key='-START-')]
]

# Crear la ventana principal
window = sg.Window('Software de Procesamiento de Imágenes', layout)

# Variables globales para almacenar los valores de las opciones avanzadas
advanced_options = {
    '-CT-': 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla CT/Plantilla_CT.dcm',
    '-SPECT-': 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla SPECT/Plantilla_SPECT.dcm',
    '-PET-': 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla PET/Plantilla_PET.dcm',
    '-MRI-': 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla MRI/Plantilla_MRI.dcm',
    '-RTDOSE-': 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/PLantilla RTDose/Plantilla_RTDOSE.dcm'
}

# Bucle de eventos
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
                advanced_options['-CT-'] = opt_values['-CT-']
                advanced_options['-SPECT-'] = opt_values['-SPECT-']
                advanced_options['-PET-'] = opt_values['-PET-']
                advanced_options['-MRI-'] = opt_values['-MRI-']
                advanced_options['-RTDOSE-'] = opt_values['-RTDOSE-']
                sg.popup('Opciones guardadas')              
                break
        options_window.close()

    # Habilitar botón de opciones de modalidad cuando se selecciona una modalidad
    if event == '-MODALITY_OUT-':
        window['-MODALITY_OUT_OPTIONS-'].update(disabled=False)

    # Abrir ventana de opciones de modalidad
    if event == '-MODALITY_OUT_OPTIONS-':
        modality = values['-MODALITY_OUT-']
        modality_window = create_modality_window(modality)
        while True:
            mod_event, mod_values = modality_window.read()
            if mod_event in (sg.WIN_CLOSED, 'Cancelar'):
                break
            if mod_event.startswith('-CHECK-'):
                opcion = mod_event.split('-')[2]
                input_key = f'-INPUT-{opcion}-'
                if mod_values[mod_event]:
                    modality_window[input_key].update(disabled=False, background_color='white')
                else:
                    modality_window[input_key].update(disabled=True, background_color='#636363')
            if mod_event == 'Aceptar':
                resultados = {}
                for opcion in mod_values:
                    if opcion.startswith('-CHECK-') and mod_values[opcion]:
                        opcion_nombre = opcion.split('-')[2]
                        resultados[opcion_nombre] = mod_values[f'-INPUT-{opcion_nombre}-']
                print("Valores seleccionados:", resultados)
                break
        modality_window.close()

    # Iniciar la ejecución de scripts y mostrar la ventana de progreso
    if event == '-START-':
        input_dir = values['-INPUT_DIR-']
        output_dir = values['-OUTPUT_DIR-']
        modality = values['-MODALITY_OUT-']
        try:
            if modality == 'CT':
                dicom_template_path = advanced_options['-CT-']
            elif modality == 'SPECT':
                dicom_template_path = advanced_options['-SPECT-']
            elif modality == 'PET':
                dicom_template_path = advanced_options['-PET-']
            elif modality == 'MRI':
                dicom_template_path = advanced_options['-MRI-']
            elif modality == 'RTDOSE':
                dicom_template_path = advanced_options['-RTDOSE-']
            else:
                dicom_template_path = ''
        except Exception as e:
            sg.popup('Error', f'Ocurrió un error al obtener la plantilla:\n{str(e)}')
            continue
    
        if not input_dir or not output_dir or not dicom_template_path:
            sg.popup('Error', 'Por favor, complete todos los campos obligatorios.')
            continue
    
        # Mostrar la ventana de progreso
        progress_window = create_progress_window()
    
        try:
            # Cargar la matriz 3D a partir de las imágenes DICOM en la carpeta de entrada
            matrix = load_slices_from_dicom(input_dir)
    
            # Llamar a la función para volcar la matriz en archivos DICOM
            save_slices_from_matrix(dicom_template_path, output_dir, matrix, study_date=datetime.today().strftime('%Y%m%d'), patient_name="Test Patient")
    
            # Simular progreso
            for i in range(100):
                time.sleep(0.01)
                progress_window['-PROGRESS-'].update_bar(i + 1)
                progress_window.refresh()
    
            # Habilitar el botón de cerrar
            progress_window['-CLOSE-'].update(disabled=False)
    
            sg.popup('Éxito', 'El script se ejecutó correctamente.')
    
        except Exception as e:
            sg.popup('Error', f'Ocurrió un error al ejecutar el script:\n{str(e)}')
    
        # Cerrar la ventana de progreso
        while True:
            prog_event, prog_values = progress_window.read()
            if prog_event in (sg.WIN_CLOSED, '-CLOSE-'):
                break
        progress_window.close()