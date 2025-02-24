import os
import numpy as np
import pydicom
from pydicom.uid import generate_uid
from collections import defaultdict

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
def save_slices_from_matrix(dicom_template_path, output_folder, file_name,matrix_3d,tag_updates):
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
        for tag_id, new_value in tag_updates.items():
            # Buscar la etiqueta por su ID (tag_id)
            tag = new_ds.get(tag_id)

            if tag is not None:
                # Actualizar el valor de la etiqueta
                tag.value = new_value
            else:
                # Si la etiqueta no existe, agregarla (esto depende del uso, pero generalmente las etiquetas deben existir)
                new_ds.add_new(tag_id, 'LO', new_value)  # 'LO' es el tipo de VR de la etiqueta (en este caso string)
        
        
        new_ds.RescaleIntercept = 0
        new_ds.RescaleSlope = 1
        
        new_ds.StudyInstanceUID = new_study_uid
        new_ds.SeriesInstanceUID = new_series_uid
        new_ds.SOPInstanceUID = generate_uid()
        new_ds.InstanceNumber = i + 1
        new_ds.ImagePositionPatient = [0, 0, i]
        new_ds.SliceLocation = i
        new_ds.PixelData = matrix_3d[i].astype(np.int16).tobytes()
        
        output_path = os.path.join(output_folder, file_name+f"_{i+1:03d}.dcm")
        new_ds.save_as(output_path)
        print(f"Guardado: {output_path}")

def read_dicom_tags(dicom_file):
    """Lee todas las etiquetas DICOM de un archivo DICOM, incluyendo secuencias anidadas."""
    dataset = pydicom.dcmread(dicom_file)
    tags = []

    def process_sequence(sequence):
        """Función recursiva para manejar secuencias anidadas."""
        for item in sequence:
            for elem in item:
                read_element(elem)
    
    def read_element(elem):
        """Lee un elemento y lo agrega a la lista de etiquetas."""
        value = elem.value
        if isinstance(value, bytes):
            value = f"<Binary data of {len(value)} bytes>"
        elif isinstance(value, pydicom.Sequence):
            process_sequence(value)
        else:
            tags.append((elem.name, elem.tag, value))
    
        for elem in dataset:
            read_element(elem)
    
    return tags

def update_dicom_tag(dicom_file, tag_updates,output_path):
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
    dicom_data.save_as(output_path)
    
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