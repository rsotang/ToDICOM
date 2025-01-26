import numpy as np
import pydicom
from pydicom.uid import generate_uid
from pydicom.dataset import Dataset, FileDataset
import os

def load_rtstruct(file_path):
    """Carga un archivo RTSTRUCT DICOM"""
    rtstruct = pydicom.dcmread(file_path)
    return rtstruct

def replace_structure(rtstruct, structure_name, new_structure_matrix):
    """
    Reemplaza la estructura especificada por una nueva matriz en el archivo RTSTRUCT.

    rtstruct: Archivo RTSTRUCT DICOM
    structure_name: Nombre de la estructura a reemplazar
    new_structure_matrix: Matriz nxnxn que representa la nueva estructura
    """
    # Buscar la estructura por nombre
    structure_set_roi_sequence = rtstruct.StructureSetROISequence
    roi_contour_sequence = rtstruct.ROIContourSequence

    found = False
    for i, roi in enumerate(structure_set_roi_sequence):
        if roi.ROIName == structure_name:
            found = True
            break

    if not found:
        raise ValueError(f"Estructura '{structure_name}' no encontrada en el archivo RTSTRUCT")

    # Reemplazar la matriz de la estructura con la nueva matriz (esto varía según el contexto clínico)
    # Aquí vamos a generar una representación muy simple, adaptada a un entorno tridimensional.
    # Asegúrate de que new_structure_matrix tenga las dimensiones correctas y se ajuste a la geometría del paciente.

    # Actualiza el ROI con nuevos puntos (solo ejemplo, en la práctica esto es más complejo)
    new_roi_contour = roi_contour_sequence[i]

    # Generar nuevos puntos para la nueva estructura (dependerá de cómo represente la matriz)
    new_contour_points = []  # Aquí se agregarán los puntos (x, y, z) del nuevo contorno de la matriz

    for z in range(new_structure_matrix.shape[2]):
        for y in range(new_structure_matrix.shape[1]):
            for x in range(new_structure_matrix.shape[0]):
                if new_structure_matrix[x, y, z] > 0:  # Considerar valores no nulos como parte de la estructura
                    new_contour_points.append([float(x), float(y), float(z)])

    # Crear un nuevo ContourData para reemplazar en el ROI
    new_roi_contour.ContourSequence[0].ContourData = np.array(new_contour_points).flatten().tolist()

    return rtstruct

def save_rtstruct(rtstruct, output_file):
    """Guarda el archivo RTSTRUCT DICOM con las modificaciones realizadas"""
    rtstruct.SOPInstanceUID = generate_uid()  # Generar nuevo UID
    rtstruct.save_as(output_file)
    print(f"Archivo RTSTRUCT guardado en {output_file}")

# Ejemplo de uso:
if __name__ == "__main__":
    # Ruta del archivo RTSTRUCT DICOM y matriz de ejemplo
    rtstruct_path = "ruta/a/tu/archivo_rtstruct.dcm"
    output_rtstruct_path = "ruta/a/tu/nuevo_archivo_rtstruct.dcm"

    # Cargar archivo RTSTRUCT DICOM
    rtstruct = load_rtstruct(rtstruct_path)

    # Crear una matriz de ejemplo nxnxn (ajusta según el caso)
    n = 50  # Dimensiones de la matriz
    new_structure_matrix = np.random.randint(0, 2, size=(n, n, n))  # Matriz de 0s y 1s

    # Reemplazar una estructura en RTSTRUCT por la nueva matriz
    structure_name_to_replace = "nombre_de_la_estructura_a_reemplazar"
    rtstruct = replace_structure(rtstruct, structure_name_to_replace, new_structure_matrix)

    # Guardar el nuevo archivo RTSTRUCT modificado
    save_rtstruct(rtstruct, output_rtstruct_path)