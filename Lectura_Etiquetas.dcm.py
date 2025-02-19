import pydicom
import PySimpleGUI as sg

def read_dicom_tags(dicom_file):
    """Lee todas las etiquetas DICOM de un archivo DICOM."""
    dataset = pydicom.dcmread(dicom_file)
    tags = []
    for elem in dataset:
        tags.append((elem.name, elem.tag, elem.value))
    return tags

def categorize_tags(tags):
    """Clasifica las etiquetas DICOM en categorías."""
    categories = {
        'Date-Time': [],
        'Image': [],
        'Patient': [],
        'Study': [],
        'Series': [],
        'Other': []
    }
    for tag in tags:
        tag_name, tag_id, tag_value = tag
        if 'Date' or 'Time' in tag_name:
            categories['Date-Time'].append(tag)
        elif 'Image' in tag_name:
            categories['Image'].append(tag)
        elif 'Patient' or 'Patient\'s'in tag_name:
            categories['Patient'].append(tag)
        elif 'Study' in tag_name:
            categories['Study'].append(tag)
        elif 'Series' in tag_name:
            categories['Series'].append(tag)
        else:
            categories['Other'].append(tag)
    return categories

def create_main_window():
    """Crea la ventana principal con las opciones de categorías."""
    layout = [
        [sg.Text('Seleccione la categoría de etiquetas a editar:')],
        [sg.Button('Editar etiquetas de fechas y tiempos')],
        [sg.Button('Editar etiquetas de imagen')],
        [sg.Button('Editar etiquetas de paciente')],
        [sg.Button('Editar etiquetas del estudio')],
        [sg.Button('Editar etiquetas de la serie')],
        [sg.Button('Editar otras etiquetas')],
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
            sg.Input(str(tag_value), size=(20, 1), key=f'-INPUT-{tag_id}-', disabled=True, background_color='#636363')  # Cuadro de texto
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

def main():
    # Ruta al archivo DICOM
    dicom_file = 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla CT/Plantilla_CT.dcm'

    # Leer las etiquetas DICOM
    tags = read_dicom_tags(dicom_file)

    # Clasificar las etiquetas por categorías
    categorized_tags = categorize_tags(tags)

    # Crear la ventana principal
    main_window = create_main_window()

    tag_window = None

    # Bucle de eventos de la ventana principal
    while True:
        event, values = main_window.read()
        if event == sg.WIN_CLOSED or event == 'Cancelar':
            break
        elif event == 'Editar etiquetas de fechas y tiempos':
            tag_window = create_tag_window('Etiquetas de adquisición', categorized_tags['Date-Time'])
        elif event == 'Editar etiquetas de imagen':
            tag_window = create_tag_window('Etiquetas de imagen', categorized_tags['Image'])
        elif event == 'Editar etiquetas de paciente':
            tag_window = create_tag_window('Etiquetas de paciente', categorized_tags['Patient'])
        elif event == 'Editar etiquetas del estudio':
            tag_window = create_tag_window('Etiquetas del estudio', categorized_tags['Study'])
        elif event == 'Editar etiquetas de la serie':
            tag_window = create_tag_window('Etiquetas de la serie', categorized_tags['Series'])
        elif event == 'Editar otras etiquetas':
            tag_window = create_tag_window('Otras etiquetas', categorized_tags['Other'])

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
                    for tag in categorized_tags['Date-Time']:  # Cambiar según la categoría
                        tag_name, tag_id, _ = tag
                        if tag_values[f'-CHECK-{tag_id}-']:
                            print(f'{tag_name}: {tag_values[f'-INPUT-{tag_id}-']}')
                    break
                # Habilitar/deshabilitar el cuadro de texto cuando se marca/desmarca la casilla
                for tag in categorized_tags['Date-Time']:  # Cambiar según la categoría
                    tag_name, tag_id, _ = tag
                    if tag_event == f'-CHECK-{tag_id}-':
                        tag_window[f'-INPUT-{tag_id}-'].update(disabled=not tag_values[f'-CHECK-{tag_id}-'])

    main_window.close()

if __name__ == '__main__':
    main()