import time
import PySimpleGUI as sg

# Definir el layout de la ventana de opciones
def create_options_window():
    # Definir los textos y calcular su longitud
    textos = [
        'Ubicación plantilla CT:',
        'Ubicación plantilla SPECT:',
        'Ubicación plantilla PET:',
        'Ubicación plantilla MRI:',
        'Ubicación plantilla RTDOSE:'
    ]
    # Calcular el tamaño máximo de los textos
    max_length = max(len(texto) for texto in textos)

    # Crear el layout
    layout = [
        [sg.Text('Opciones avanzadas')],
        [sg.Text(textos[0]),sg.Push(),  sg.Text(textos[1]), sg.Push(), sg.Text(textos[2]),sg.Push(),  sg.Text(textos[3]), sg.Push(), sg.Text(textos[4])],
        [
            sg.Input(size=(max_length, 1), key='-CT-'), 
            sg.Input(size=(max_length, 1), key='-SPECT-'),
            sg.Input(size=(max_length, 1), key='-PET-'),
            sg.Input(size=(max_length, 1), key='-MRI-'),
            sg.Input(size=(max_length, 1), key='-RTDOSE-')
        ],
        [
            sg.FolderBrowse('Seleccionar', target='-CT-'),sg.Push(),
            sg.FolderBrowse('Seleccionar', target='-SPECT-'), sg.Push(),
            sg.FolderBrowse('Seleccionar', target='-PET-'), sg.Push(),
            sg.FolderBrowse('Seleccionar', target='-MRI-'),sg.Push(),
            sg.FolderBrowse('Seleccionar', target='-RTDOSE-')
        ],
        [sg.Button('Guardar'), sg.Button('Salir')]
    ]
    return sg.Window('Opciones', layout, element_justification='c',finalize=True)

##############################################################################

# Definir el layout de la ventana de modalidad
def create_modality_window(modality):
    # Opciones disponibles
   # Definir opciones según la modalidad seleccionada
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
    # Layout dinámico para cada opción
    layout = [
        [sg.Text(f'Opciones para {modality}')],
        [sg.Text('Seleccione una opción:')]
    ]

    # Añadir una fila por cada opción
    for opcion in opciones:
        layout.append([
            sg.Text(opcion),  # Texto de la opción
            sg.Checkbox('', key=f'-CHECK-{opcion}-', enable_events=True),  # Casilla clickable
            sg.Input('', size=(20, 1), key=f'-INPUT-{opcion}-', disabled=True, background_color='#636363')  # Cuadro de texto
        ])

    # Botones de Aceptar y Cancelar
    layout.append([sg.Button('Aceptar'), sg.Button('Cancelar')])

    return sg.Window(f'Opciones de {modality}', layout, finalize=True)

##############################################################################

# Definir el layout de la ventana de progreso
def create_progress_window():
    layout = [
        [sg.Text('Procesando...')],
        [sg.ProgressBar(100, orientation='h', size=(20, 20), key='-PROGRESS-')],
        [sg.Button('Cerrar', key='-CLOSE-', disabled=True)]
    ]
    return sg.Window('Progreso', layout, finalize=True)

# Definir el layout de la ventana principal
layout = [
    [sg.Push(), sg.Text('DICOM_to_DICOM', font=('Helvetica', 16)), sg.Push()],
    [sg.Text('Directorio de entrada:'), sg.Input(size=(10, 10)), sg.FolderBrowse('Seleccionar'), sg.Text('Directorio de salida:'), sg.Input(size=(10, 10)), sg.FolderBrowse('Seleccionar')],
    [],
    [sg.Text('Modalidad de imagen de entrada:'), sg.Combo([' ', 'CT', 'SPECT', 'PET', 'MRI', 'RTDOSE', '.mat'], key='-MODALITY_IN-', enable_events=True), sg.Push(), sg.Text('Modalidad de imagen de salida:'), sg.Combo(['', 'CT', 'SPECT', 'PET', 'MRI', 'RTDOSE'], key='-MODALITY_OUT-', enable_events=True)],
    [],
    [sg.Push(), sg.Push(), sg.Button('Opciones Etiquetas DICOM de Modalidad', key='-MODALITY_OUT_OPTIONS-', disabled=True)],
    [],
    [sg.Button('Opciones', key='-OPTIONS-'), sg.Push(), sg.Button('Iniciar', key='-START-')]
]

##############################################################################
# Crear la ventana principal
window = sg.Window('Software de Procesamiento de Imágenes', layout)

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
                # Aquí puedes guardar las opciones seleccionadas
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

            # Manejar eventos de las casillas
            if mod_event.startswith('-CHECK-'):
                opcion = mod_event.split('-')[2]  # Extraer el nombre de la opción
                input_key = f'-INPUT-{opcion}-'  # Clave del cuadro de texto asociado
                if mod_values[mod_event]:  # Si la casilla está marcada
                    modality_window[input_key].update(disabled=False, background_color='white')  # Habilitar y cambiar color
                else:  # Si la casilla no está marcada
                    modality_window[input_key].update(disabled=True, background_color='#636363')  # Deshabilitar y cambiar color

            # Manejar el botón Aceptar
            if mod_event == 'Aceptar':
                # Recopilar los valores de los cuadros de texto habilitados
                resultados = {}
                for opcion in ['Opción A', 'Opción B', 'Opción C']:
                    if mod_values[f'-CHECK-{opcion}-']:  # Si la casilla está marcada
                        resultados[opcion] = mod_values[f'-INPUT-{opcion}-']  # Guardar el valor del cuadro de texto
                print("Valores seleccionados:", resultados)
                break
        modality_window.close()

    # Iniciar la ejecución de scripts y mostrar la ventana de progreso
    if event == '-START-':
        progress_window = create_progress_window()
        for i in range(100):
            # Simular la ejecución de un script
            time.sleep(0.1)
            progress_window['-PROGRESS-'].update_bar(i + 1)
            progress_window.refresh()
        progress_window['-CLOSE-'].update(disabled=False)
        while True:
            prog_event, prog_values = progress_window.read()
            if prog_event in (sg.WIN_CLOSED, '-CLOSE-'):
                break
        progress_window.close()
        sg.popup('Ejecución completada')

window.close()