import os
import numpy as np
import pydicom
from pydicom.dataset import Dataset, FileDataset
import mat_to_py
from skimage.transform import resize

def save_slices_from_matrix(dicom_template_path, output_folder, matrix_3d, study_date,patient_name="Anon"):
    """
    Vuelca una matriz 3D en una serie de imágenes DICOM usando un archivo DICOM base como plantilla.

    Parameters:
    - dicom_template_path (str): Ruta al archivo DICOM base.
    - output_folder (str): Carpeta donde se guardarán los nuevos archivos DICOM.
    - matrix_3d (np.ndarray): Matriz 3D con los datos de imagen (dimensiones: slices x rows x cols).
    - patient_name (str): Nombre del paciente para los archivos DICOM.
    - study_date (str): Fecha del estudio en formato 'YYYYMMDD'.
    """
    # Cargar el archivo DICOM base como plantilla
    template_ds = pydicom.dcmread(dicom_template_path)

    # Obtener dimensiones de la plantilla DICOM
    template_rows, template_cols = template_ds.Rows, template_ds.Columns

    # Verificar dimensiones de la matriz
    slices, rows, cols = matrix_3d.shape
    # Si las dimensiones no coinciden, redimensionar la matriz 3D
    if (rows, cols) != (template_rows, template_cols):
        print(f"Redimensionando la matriz de ({rows}, {cols}) a ({template_rows}, {template_cols})")
        # Redimensionar cada corte de la matriz 3D al tamaño del DICOM (usando bilineal para mantener intensidad)
        resized_matrix = np.zeros((slices, template_rows, template_cols), dtype=matrix_3d.dtype)
        for i in range(slices):
            resized_matrix[i] = resize(matrix_3d[i], (template_rows, template_cols), preserve_range=True)
        matrix_3d = resized_matrix.astype(np.int16)  # Convertir de nuevo a int16
    else:
        print("Dimensiones de la matriz coinciden con la plantilla DICOM, no es necesario redimensionar.")


    # Crear el directorio de salida si no existe
    os.makedirs(output_folder, exist_ok=True)

    for i in range(slices):
        # Crear una copia del archivo DICOM base
        new_ds = template_ds.copy()

        # Actualizar etiquetas generales
        new_ds.PatientName = patient_name
        new_ds.StudyDate = study_date
        #FileModadate
        #Acquisition Date
        #Content Date
        #study time
        # Manufacturer
        #Refering pysician name
        #Patient name
        #Patient ID
        #Deidentificaciont metho  
      
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
    dicom_template = "Plantilla RTDOSE/RD.uQgXjHGKInSjzodqlgFYe7n5N.A3.5646.S18.dcm"

    # Carpeta de salida
    output_dir = "slices_output"

    # Crear una matriz 3D ficticia (100 slices de 512x512 píxeles)
    matrix = mat_to_py.cargar_matriz_3d('Validation_CT100.mat', 'volumeCT100')

    # Llamar a la función
    save_slices_from_matrix(dicom_template, output_dir, matrix, study_date="20241120", patient_name="Test Patient")