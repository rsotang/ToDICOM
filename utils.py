import os
import numpy as np
import pydicom
from pydicom.uid import generate_uid
from collections import defaultdict
import scipy.io
import matplotlib.pyplot as plt


def load_slices_from_dicom(input_folder, mode='slices'):
    if mode == 'slices':
        return load_multiple_slices(input_folder)
    elif mode == '3D':
        return load_single_multislice_dicom(input_folder)
    else:
        raise ValueError("Modo no soportado. Use 'slices' o '3D'.")

def load_multiple_slices(input_folder):
    dicom_files = sorted([os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".dcm")])
    first_slice = pydicom.dcmread(dicom_files[0])
    rows, cols = first_slice.Rows, first_slice.Columns
    slices = len(dicom_files)
    matrix_3d = np.zeros((slices, rows, cols), dtype=np.int16)
    for i, dicom_file in enumerate(dicom_files):
        ds = pydicom.dcmread(dicom_file)
        matrix_3d[i, :, :] = ds.pixel_array
    return matrix_3d

def load_single_multislice_dicom(input_folder):
    dicom_files = [os.path.join(input_folder, f) for f in os.listdir(input_folder) if f.endswith(".dcm")]
    if len(dicom_files) != 1:
        raise ValueError("La carpeta debe contener exactamente un archivo DICOM para el modo '3d'.")
    dicom_file = dicom_files[0]
    ds = pydicom.dcmread(dicom_file)
    if not hasattr(ds, 'NumberOfFrames') or ds.NumberOfFrames <= 1:
        raise ValueError("El archivo DICOM no es multislice o no contiene múltiples frames.")
    rows, cols = ds.Rows, ds.Columns
    slices = ds.NumberOfFrames
    matrix_3d = np.zeros((slices, rows, cols), dtype=np.int16)
    matrix_3d[:, :, :] = ds.pixel_array
    return matrix_3d

def plot_slices(volume):
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Cortes en los planos XY, XZ, YZ
    slice_x = volume[volume.shape[0] // 2, :, :]
    slice_y = volume[:, volume.shape[1] // 2, :]
    slice_z = volume[:, :, volume.shape[2] // 2]
    
    axes[0].imshow(slice_x, cmap='gray')
    axes[0].set_title("Corte XY")
    
    axes[1].imshow(slice_y, cmap='gray')
    axes[1].set_title("Corte XZ")
    
    axes[2].imshow(slice_z, cmap='gray')
    axes[2].set_title("Corte YZ")
    
    plt.show()



def load_slices_from_mat(input_dir): #se asume que la matriz ya va en 3D
   
    try:
        input_file = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".mat")]
        if len(input_file) != 1:
           raise ValueError("La carpeta debe contener exactamente un archivo para el modo '3d'.")
        # Cargar el archivo .mat
        mat_data = scipy.io.loadmat(input_file)

        # Intentar extraer la variable asumiendo que siempre va a ocupar la cuarta posición del diccionario 
        matriz = list(mat_data.values())[3]

        if matriz is not None:
            return matriz
        
    except Exception as e:
        print(f"Error al cargar el archivo .mat: {e}")
        return None
    
def load_slices_from_npy(input_dir): #se asume que la matriz ya va en 3D
   
    try:
        input_file = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.endswith(".npy")]
        if len(input_file) != 1:
           raise ValueError("La carpeta debe contener exactamente un archivo para el modo '3d'.")
        # Cargar el archivo .npy
        matriz = np.load(input_file)     
        

        if matriz is not None:
            return matriz
        
    except Exception as e:
        print(f"Error al cargar el archivo .npy: {e}")
        return None
    
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

def categorize_tags(tags, category_mapping):
    """Clasifica las etiquetas DICOM en categorías, manejando etiquetas anidadas."""
    categories = defaultdict(list)

    for tag in tags:
        #print(tag,'iteración')
        tag_name, tag_id, tag_value = tag
        added = False
        # Verificar si la etiqueta pertenece a alguna categoría
        for category, keywords in category_mapping.items():
            if any(keyword in tag_name for keyword in keywords):
                categories[category].append(tag)
                added = True
                #print(tag,'añadida')
                break
        
        # Si no encaja en ninguna categoría conocida, agregar a "Other"
        if not added:
            categories['Other'].append(tag)

    return categories

#%% MAPAS DE CATEGRIA 

category_mappings = {
'CT': {
    'Patient': [
        'Patient\'s Name', 'Patient ID', 'Patient\'s Birth Date', 'Patient\'s Sex',
        'Patient\'s Weight', 'Patient\'s Position'
    ],
    'Study': [
        'Study Instance UID', 'Study Date', 'Study Time', 'Study ID', 'Accession Number',
        'Referring Physician Name', 'Study Description', 'Instance Creation Date', 'Instance Creation Time',
        'Content Date', 'Content Time'
    ],
    'Series': [
        'Series Instance UID', 'Series Number', 'Modality', 'Series Date',
        'Series Time', 'OperatorsName', 'Protocol Name', 'Body Part Examined',
        'Scanning Sequence','Series Description'
    ],
    'Image': [
        'SOP Class UID', 'SOP Instance UID', 'Instance Number', 'Image Type',
        'Photometric Interpretation', 'Rows', 'Columns', 'Pixel Spacing',
        'Bits Allocated', 'Bits Stored', 'High Bit', 'Rescale Intercept', 
        'Rescale Slope',  'Slice Thickness', 'Slice Location',
        'Window Center', 'Window Width', 'Pixel Representation'
    ],
    'Acquisition': [
        'Acquisition Number', 'Acquisition Date', 'Acquisition Time', 'Exposure Time', 'KVP',
        'X-Ray Tube Current', 'Exposure', 'Reconstruction Diameter', 'Table Height',
        'RotationDirection', 'Field Of View Shape', 'Field Of View Dimensions', 'Scan Options',
        'Data Collection Diameter','Gantry/Detector Tilt', 'Rotation Direction','Filter Type',
        'Generator Power', 'Focal Spot(s)', 'Convolution Kernel', 'Patient Position', 'CTDIvol',
        'Image Position (Patient)', 'Image Orientation (Patient)', 'Frame of Reference UID',
        'Position Reference Indicator','Filter Type'
    ],
    'Device': [
        'Manufacturer', 'Manufacturer Model Name', 'Station Name', 'Device Serial Number',
        'Software Versions', 'Institution Name', 'Institution Address', 'Manufacturer\'s Model Name'
    ],
    'Other': []
},
'MRI': {
    'Patient': [
        'Patient\'s Name', 'Patient ID', 'Patient\'s Birth Date', 'Patient\'s Sex',
        'Patient\'s Weight', 'Patient\'s Position'
    ],
    'Study': [
        'Study Instance UID', 'Study Date', 'Study Time', 'Study ID', 'Accession Number',
        'Referring Physician Name', 'Study Description', 'Instance Creation Date', 'Instance Creation Time',
        'Content Date', 'Content Time'
    ],
    'Series': [
        'Series Instance UID', 'Series Number', 'Modality', 'Series Date',
        'Series Time', 'Operators Name', 'Protocol Name', 'Body Part Examined',
        'Scanning Sequence','Series Description', 'Sequence Variant', 'Scan Options', 'Imaging Frequency',
        'Magnetic Field Strength', 'Echo Train Length', 'Inversion Time'
    ],
    'Image': [
        'SOP Class UID', 'SOP Instance UID', 'Instance Number', 'Image Type',
        'Photometric Interpretation', 'Rows', 'Columns', 'Pixel Spacing',
        'Bits Allocated', 'Bits Stored', 'High Bit', 'Rescale Intercept', 
        'Rescale Slope',  'Slice Thickness', 'Slice Location',
        'Window Center', 'Window Width', 'Pixel Representation', 'Flip Angle'
    ],
    'Acquisition': [
        'Acquisition Number', 'Acquisition Date', 'Acquisition Time',
        'Reconstruction Diameter', 'Table Height', 'Field Of View Shape', 'Field Of View Dimensions', 'Scan Options',
        'Data Collection Diameter', 'Convolution Kernel', 'Patient Position',
        'Image Position (Patient)', 'Image Orientation (Patient)', 'Frame of Reference UID',
        'Position Reference Indicator','TR', 'TE',
        'TI', 'Echo Time', 'Repetition Time', 'Number Of Averages', 'Phase Encoding Direction',
        'Acquisition Matrix', 'Percent Sampling', 'Percent Phase Field of View', 
        'Pixel Bandwidth', 'Contrast/Bolus Agent', 'MR Acquisition Type'
    ],
    'Device': [
        'Manufacturer', 'Manufacturer Model Name', 'Station Name', 'Device Serial Number',
        'Software Versions', 'Institution Name', 'Institution Address', 'Manufacturer\'s Model Name'
    ],
    'Other': []
    },  
'PET': { 
    'Patient': [
        'Patient\'s Name', 'Patient ID', 'Patient\'s Birth Date', 'Patient\'s Sex',
        'Patient\'s Weight', 'Patient\'s Position'
    ],
    'Study': [
        'Study Instance UID', 'Study Date', 'Study Time', 'Study ID', 'Accession Number',
        'Referring Physician Name', 'Study Description', 'Instance Creation Date', 'Instance Creation Time',
        'Content Date', 'Content Time'
    ],
    'Series': [
        'Series Instance UID', 'Series Number', 'Modality', 'Series Date',
        'Series Time', 'Operators Name', 'Protocol Name', 'Body Part Examined',
        'Series Description'
    ],
    'Image': [
        'SOP Class UID', 'SOP Instance UID', 'Instance Number', 'Image Type',
        'Photometric Interpretation', 'Rows', 'Columns', 'Pixel Spacing',
        'Bits Allocated', 'Bits Stored', 'High Bit', 'Rescale Intercept', 
        'Rescale Slope', 'Slice Thickness', 'Slice Location',
        'Window Center', 'Window Width', 'Pixel Representation', 'Image Position (Patient)',
        'Image Orientation (Patient)',
    ],
    'Acquisition': [
        'Acquisition Number', 'Acquisition Date', 'Acquisition Time',
        'Reconstruction Diameter', 'Table Height', 'Field Of View Shape', 'Field Of View Dimensions',
        'Data Collection Diameter', 'Convolution Kernel', 'Patient Position',
        'Attenuation Correction Method', 'Scatter Correction Method', 'Frame Reference Time', 'Decay Correction',
        'Random Correction Method', 'Collimator Type', 'Actual Frame Duration', 'Energy Window Lower Limit', 'Energy Window Upper Limit'
    ],
    'Radiopharmaceutical': [
        'Radiopharmaceutical', 'Radiopharmaceutical Start Time', 'Radionuclide Total Dose', 
        'Radionuclide Half Life', 'Radionuclide Positron Fraction', 'Units', 'Counts Source',
        'Decay Factor', 'Dose Calibration Factor', 'Scatter Fraction Factor', 'Radiopharmaceutical Start DateTime',
        'Radiopharmaceutical Stop DateTime'
    ],
    'Device': [
        'Manufacturer', 'Manufacturer Model Name', 'Station Name', 'Device Serial Number',
        'Software Versions', 'Institution Name', 'Institution Address', 'Manufacturer\'s Model Name'
    ],
    'Other': []
    },  
'SPECT': { 
    'Patient': [
        'Patient\'s Name', 'Patient ID', 'Patient\'s Birth Date', 'Patient\'s Sex',
        'Patient\'s Weight', 'Patient\'s Position'
    ],
    'Study': [
        'Study Instance UID', 'Study Date', 'Study Time', 'Study ID', 'Accession Number',
        'Referring Physician Name', 'Study Description', 'Instance Creation Date', 'Instance Creation Time',
        'Content Date', 'Content Time'
    ],
    'Series': [
        'Series Instance UID', 'Series Number', 'Modality', 'Series Date',
        'Series Time', 'Operators Name', 'Protocol Name', 'Body Part Examined',
        'Series Description'
    ],
    'Image': [
        'SOP Class UID', 'SOP Instance UID', 'Instance Number', 'Image Type',
        'Photometric Interpretation', 'Rows', 'Columns', 'Pixel Spacing',
        'Bits Allocated', 'Bits Stored', 'High Bit', 'Rescale Intercept', 
        'Rescale Slope', 'Slice Thickness', 'Slice Location',
        'Window Center', 'Window Width', 'Pixel Representation', 'Image Position (Patient)',
        'Image Orientation (Patient)',
    ],
    'Acquisition': [
        'Acquisition Number', 'Acquisition Date', 'Acquisition Time',
        'Reconstruction Diameter', 'Table Height', 'Field Of View Shape', 'Field Of View Dimensions',
        'Data Collection Diameter', 'Convolution Kernel', 'Patient Position',
        'Attenuation Correction Method', 'Scatter Correction Method', 'Frame Reference Time', 'Decay Correction',
        'Random Correction Method', 'Collimator Type', 'Actual Frame Duration', 'Energy Window Lower Limit', 'Energy Window Upper Limit'
    ],
    'Radiopharmaceutical': [
        'Radiopharmaceutical', 'Radiopharmaceutical Start Time', 'Radionuclide Total Dose', 
        'Radionuclide Half Life', 'Radionuclide Positron Fraction', 'Units', 'Counts Source',
        'Decay Factor', 'Dose Calibration Factor', 'Scatter Fraction Factor', 'Radiopharmaceutical Start DateTime',
        'Radiopharmaceutical Stop DateTime','Counts Accumulated', 'Count Rate'
    ],
    'Device': [
        'Manufacturer', 'Manufacturer Model Name', 'Station Name', 'Device Serial Number',
        'Software Versions', 'Institution Name', 'Institution Address', 'Manufacturer\'s Model Name'
    ],
    'Other': []
    },  
'RTDOSE': { 
    'Patient': [
        'Patient\'s Name', 'Patient ID', 'Patient\'s Birth Date', 'Patient\'s Sex',
        'Patient\'s Weight', 'Patient\'s Position'
    ],
    'Study': [
        'Study Instance UID', 'Study Date', 'Study Time', 'Study ID', 'Accession Number',
        'Referring Physician Name', 'Study Description', 'Instance Creation Date', 'Instance Creation Time',
        'Content Date', 'Content Time'
    ],
    'Series': [
        'Series Instance UID', 'Series Number', 'Modality', 'Series Date',
        'Series Time', 'OperatorsName', 'Protocol Name', 'Body Part Examined',
        'Scanning Sequence','Series Description'
    ],
    'Image': [
        'SOP Class UID', 'SOP Instance UID', 'Instance Number', 'Image Type',
        'Photometric Interpretation', 'Rows', 'Columns', 'Pixel Spacing',
        'Bits Allocated', 'Bits Stored', 'High Bit', 'Rescale Intercept', 
        'Rescale Slope',  'Slice Thickness', 'Slice Location',
        'Window Center', 'Window Width', 'Pixel Representation'
    ],
    'Dose': [
         'Dose Units', 'Dose Type', 'Dose Summation Type', 'Dose Grid Scaling', 'DVH Normalization Point',
         'DVH Normalization Dose Value', 'Beam Dose', 'Beam Meter set', 'Beam Dose Point Depth', 'Beam DosePoint SSD',
         'Referenced RT Plan Sequence', 'Dose Reference UID'
     ],
     'Grid': [
         'Rows', 'Columns', 'Number Of Frames', 'Grid Frame Off set Vector', 'Pixel Spacing',
         'SliceThickness', 'Dose Grid Scaling',
         'Grid Frame Off set Vector', 'Frame Of Reference UID', 'Plane Position Sequence', 
         
     ],
    'Other': []
    }  
}

  
  
  
  
  
  