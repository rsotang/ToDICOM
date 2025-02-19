import pydicom
from collections import defaultdict

# Función para categorizar las etiquetas DICOM específicas para imágenes MRI
def categorize_dicom_tags_mri(dicom_data):
    categories = defaultdict(list)
    
    # Definir las categorías específicas para una imagen MRI
    category_mapping = {
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
    }

    for elem in dicom_data:
        # Procesar valores binarios o largos de forma legible
        value = elem.value
        if isinstance(value, bytes):
            value = f"<Binary data of {len(value)} bytes>"
        elif isinstance(value, str) and len(value) > 50:
            value = value[:50] + '... [truncated]'

        # Verifica si el nombre del elemento se encuentra en las categorías definidas
        added = False
        for category, tags in category_mapping.items():
            if elem.name in tags:
                categories[category].append((elem.name, value))
                added = True
                break
        
        # Si no está en ninguna categoría predefinida, la añadimos a 'Other'
        if not added:
            categories['Other'].append((elem.name, value))
    
    return categories

# Función para imprimir las categorías
def print_categories(categories):
    for category, tags in categories.items():
        print(f"\n{category} Tags:")
        for tag in tags:
            print(f"  {tag[0]}: {tag[1]}")

# Leer el archivo DICOM
def read_dicom(file_path):
    dicom_data = pydicom.dcmread(file_path)
    return dicom_data

# Ruta al archivo DICOM
file_path = 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla MRI/Plantilla_MRI.dcm'

# Leer datos DICOM y agrupar las etiquetas
dicom_data = read_dicom(file_path)
categories = categorize_dicom_tags_mri(dicom_data)

# Imprimir las categorías
print_categories(categories)

