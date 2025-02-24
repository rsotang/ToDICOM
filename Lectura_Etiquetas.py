import PySimpleGUI as sg
from D_to_D_aux_functions.categorized_tags import category_mappings as category_mappings
import D_to_D_aux_functions.categorized_tags as aux
import pydicom

def update_dicom_tag(dicom_file, tag_updates):
    """Actualiza múltiples etiquetas DICOM en el archivo con los valores proporcionados."""
    # Cargar el archivo DICOM
    dicom_data = pydicom.dcmread(dicom_file)

    # Iterar sobre las actualizaciones de las etiquetas
    for tag_id, new_value in tag_updates.items():
        # Buscar la etiqueta por su ID (tag_id)
        tag = dicom_data.get(tag_id)

        if tag is not None:
            # Actualizar el valor de la etiqueta
            tag.value = new_value
        else:
            # Si la etiqueta no existe, agregarla (esto depende del uso, pero generalmente las etiquetas deben existir)
            dicom_data.add_new(tag_id, 'LO', new_value)  # 'LO' es el tipo de VR de la etiqueta (en este caso string)

    # Guardar los cambios en el archivo DICOM
    dicom_data.save_as('D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla CT/nuevo_archivo.dcm')
    
def process_tag_values_and_update_dicom(dicom_file, category, categorized_tags, tag_values):
    """Procesa los valores seleccionados y prepara las etiquetas DICOM correspondientes para ser actualizadas."""
    tag_updates = {}  # Diccionario para almacenar las actualizaciones de las etiquetas

    # Iterar sobre las etiquetas de la categoría
    for tag in categorized_tags[category]:
        tag_name, tag_id, _ = tag
        if tag_values.get(f'-CHECK-{tag_id}-', False):  # Verificar si la casilla está marcada
            new_value = tag_values[f'-INPUT-{tag_id}-']
            # Almacenar el valor actualizado para esta etiqueta en el diccionario
            tag_updates[tag_id] = new_value

    # Llamar a la función para actualizar todas las etiquetas de una sola vez
    return tag_updates
def create_main_window(categories):
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

def select_modality():
    """Crea una ventana para seleccionar la modalidad de imagen."""
    layout = [
        [sg.Text('Seleccione la modalidad de imagen:')],
        [sg.Button('CT')],
        [sg.Button('PET')],
        [sg.Button('MRI')],
        [sg.Button('SPECT')],
        [sg.Button('RTDOSE')],
        [sg.Button('Cancelar')]
    ]
    return sg.Window('Selección de Modalidad', layout, finalize=True)


def main():
    # Ruta al archivo DICOM
    dicom_file = 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla CT/Plantilla_CT-modified.dcm' 
    

    modality_window = select_modality()
    modality = None
    while True:
        event, values = modality_window.read()
        if event == sg.WIN_CLOSED or event == 'Cancelar':
            modality_window.close()
            return
        elif event in ['CT', 'PET', 'MRI','SPECT','RTDOSE']:
            modality = event
            modality_window.close()
            break
   
    # Leer las etiquetas DICOM
    tags = aux.read_dicom_tags(dicom_file)
    

    # Clasificar las etiquetas por categorías usando el mapeo correspondiente
    categorized_tags = aux.categorize_tags(tags, category_mappings[modality])
    

    # Crear la ventana principal con botones dinámicos
    main_window = create_main_window(categorized_tags.keys())

    tag_window = None

    # Bucle de eventos de la ventana principal
    while True:
        event, values = main_window.read()
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
                    # Aquí puedes procesar los valores seleccionados y actualizarlos en el DICOM
                    print("Valores seleccionados:")
                    for tag in categorized_tags[category]:  # Iterar por las etiquetas de la categoría
                        tag_name, tag_id, _ = tag
                        if tag_values[f'-CHECK-{tag_id}-']:
                            print(f'{tag_name}: {tag_values[f'-INPUT-{tag_id}-']}')
                    
                    # Procesar los valores y actualizar el archivo DICOM
                    tag_updates = process_tag_values_and_update_dicom(dicom_file, category, categorized_tags, tag_values)
                    
                    update_dicom_tag(dicom_file, tag_updates)
                    
                    break
                    
                # Habilitar/deshabilitar el cuadro de texto cuando se marca/desmarca la casilla
                for tag in categorized_tags[category]:  # Cambiar según la categoría
                    tag_name, tag_id, _ = tag
                    if tag_event == f'-CHECK-{tag_id}-':
                        tag_window[f'-INPUT-{tag_id}-'].update(disabled=not tag_values[f'-CHECK-{tag_id}-'])
                        

    main_window.close()

if __name__ == '__main__':
    main()