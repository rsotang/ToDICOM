import os
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
from datetime import datetime
from pydicom.uid import generate_uid
from pydicom.dataset import Dataset, FileDataset

def load_slices_from_dicom(input_folder):
    """
    Carga los datos de píxeles de una serie de imágenes DICOM desde una carpeta y los organiza en una matriz 3D.

    Parameters:
    - input_folder (str): Carpeta que contiene las imágenes DICOM.

    Returns:
    - matrix_3d (np.ndarray): Matriz 3D con los datos de imagen (dimensiones: slices x rows x cols).
    """
    # Obtener la lista de archivos DICOM en la carpeta
    dicom_files = sorted([os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".dcm")])

    # Leer el primer archivo para obtener las dimensiones
    first_slice = pydicom.dcmread(dicom_files[0])
    rows, cols = first_slice.Rows, first_slice.Columns
    slices = len(dicom_files)

    # Crear una matriz vacía para almacenar los datos de píxeles
    matrix_3d = np.zeros((slices, rows, cols), dtype=np.int16)

    # Cargar los datos de píxeles de cada archivo DICOM en la matriz 3D
    for i, dicom_file in enumerate(dicom_files):
        ds = pydicom.dcmread(dicom_file)
        matrix_3d[i, :, :] = ds.pixel_array

    return matrix_3d

def save_slices_from_matrix(dicom_template_path, output_folder, matrix_3d, study_date, patient_name="Anon"):
    """
    Vuelca una matriz 3D en una serie de imágenes DICOM usando un archivo DICOM base como plantilla.
    Si las dimensiones de la matriz no coinciden con la plantilla, ajusta la plantilla.
    Genera UIDs únicos para cada imagen DICOM.

    Parameters:
    - dicom_template_path (str): Ruta al archivo DICOM base.
    - output_folder (str): Carpeta donde se guardarán los nuevos archivos DICOM.
    - matrix_3d (np.ndarray): Matriz 3D con los datos de imagen (dimensiones: slices x rows x cols).
    - patient_name (str): Nombre del paciente para los archivos DICOM.
    - study_date (str): Fecha del estudio en formato 'YYYYMMDD'.
    """
    # Cargar el archivo DICOM base como plantilla
    template_ds = pydicom.dcmread(dicom_template_path)

    # Verificar dimensiones de la matriz
    slices, rows, cols = matrix_3d.shape

    # Si las dimensiones no coinciden, ajustar las etiquetas de la plantilla
    if (rows, cols) != (template_ds.Rows, template_ds.Columns):
        print(f"Las dimensiones de la matriz ({rows}x{cols}) no coinciden con la plantilla DICOM ({template_ds.Rows}x{template_ds.Columns}). Ajustando plantilla...")
        template_ds.Rows = rows
        template_ds.Columns = cols

    # Crear el directorio de salida si no existe
    os.makedirs(output_folder, exist_ok=True)

    # Generar nuevos UIDs para el estudio y la serie
    new_study_uid = generate_uid()
    new_series_uid = generate_uid()

    for i in range(slices):
        # Crear una copia del archivo DICOM base
        new_ds = template_ds.copy()

        # Actualizar etiquetas generales
        new_ds.PatientName = patient_name
        new_ds.StudyDate = study_date

        # Actualizar UIDs para cada instancia DICOM, como estamos partiendo de un único corte como plantilla, si no tenemos
        # cuidado la SOP no es único y no se puede importar por compatibilidad, asi que para evitar problemas, cada vez que se
        
        new_ds.StudyInstanceUID = new_study_uid  # Mantener el mismo para todo el estudio
        new_ds.SeriesInstanceUID = new_series_uid  # Mantener el mismo para toda la serie
        new_ds.SOPInstanceUID = generate_uid()  # Diferente para cada corte (slice)

        # Actualizar etiquetas específicas del slice
        new_ds.InstanceNumber = i + 1
        new_ds.ImagePositionPatient = [0, 0, i]  # Asumiendo 1 mm entre cortes (ajustar según sea necesario)
        new_ds.SliceLocation = i  # Ubicación del corte (en mm o unidades propias)

        # Actualizar los datos de píxeles
        new_ds.PixelData = matrix_3d[i].astype(np.int16).tobytes()

        # Actualizar rescale intercept y slope si es necesario
        new_ds.RescaleIntercept = 0
        new_ds.RescaleSlope = 1

        # Nombre del archivo de salida
        output_path = os.path.join(output_folder, f"slice_{i+1:03d}.dcm")

        # Guardar el nuevo archivo DICOM
        new_ds.save_as(output_path)
        print(f"Guardado: {output_path}")


# Ejemplo de uso:
if __name__ == "__main__":
    # Ruta a la plantilla DICOM
    dicom_template = "Plantilla PET/RADIOFISICA.PT.PET_NEURO_FDG_(.5.1.2024.10.23.09.44.14.161.38795067.dcm"

    # Carpeta de salida
    output_dir = "output"

    # Carpeta que contiene los archivos DICOM originales (input folder)
    input_dir = "input"

    # Cargar la matriz 3D a partir de las imágenes DICOM en la carpeta de entrada
    matrix = load_slices_from_dicom(input_dir)

    # Llamar a la función para volcar la matriz en archivos DICOM
    save_slices_from_matrix(dicom_template, output_dir, matrix, study_date=datetime.today(), patient_name="Test Patient")