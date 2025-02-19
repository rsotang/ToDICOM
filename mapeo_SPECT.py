from collections import defaultdict
import pydicom

# Función para categorizar las etiquetas DICOM específicas para imágenes PET
def categorize_dicom_tags_pet(dicom_data):
    categories = defaultdict(list)
    
    # Definir las categorías específicas para una imagen PET
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
            'Series Description'
        ],
        'Image': [
            'SOP Class UID', 'SOP Instance UID', 'Instance Number', 'Image Type',
            'Photometric Interpretation', 'Rows', 'Columns', 'Pixel Spacing',
            'Bits Allocated', 'Bits Stored', 'High Bit', 'Rescale Intercept', 
            'Rescale Slope', 'Slice Thickness', 'Slice Location',
            'Window Center', 'Window Width', 'Pixel Representation'
        ],
        'Acquisition': [
            'Acquisition Number', 'Acquisition Date', 'Acquisition Time',
            'Reconstruction Diameter', 'Table Height', 'Field Of View Shape', 'Field Of View Dimensions',
            'Data Collection Diameter', 'Convolution Kernel', 'Patient Position',
            'Attenuation Correction Method', 'Scatter Correction Method', 'Frame Reference Time', 'Decay Correction',
            'Random Correction Method', 'Collimator Type', 'Actual Frame Duration'
        ],
        'Radiopharmaceutical': [
            'Radiopharmaceutical', 'Radiopharmaceutical Start Time', 'Radionuclide Total Dose', 
            'Radionuclide Half Life', 'Radionuclide Positron Fraction', 'Units', 'Counts Source',
            'Decay Factor', 'Dose Calibration Factor', 'Scatter Fraction Factor'
        ],
        'Device': [
            'Manufacturer', 'Manufacturer Model Name', 'Station Name', 'Device Serial Number',
            'Software Versions', 'Institution Name', 'Institution Address', 'Manufacturer\'s Model Name'
        ],
        'Other': []
    }

    def add_sequence_tags(sequence, category):
        """Helper function to recursively add tags from a DICOM sequence"""
        for item in sequence:
            for elem in item:
                value = elem.value
                if isinstance(value, bytes):
                    value = f"<Binary data of {len(value)} bytes>"
                elif isinstance(value, str) and len(value) > 50:
                    value = value[:50] + '... [truncated]'
                categories[category].append((elem.name, value))

    for elem in dicom_data:
        value = elem.value
        if isinstance(value, bytes):
            value = f"<Binary data of {len(value)} bytes>"
        elif isinstance(value, str) and len(value) > 50:
            value = value[:50] + '... [truncated]'

        added = False

        # Verifica si el nombre del elemento se encuentra en las categorías definidas
        for category, tags in category_mapping.items():
            if elem.name in tags:
                categories[category].append((elem.name, value))
                added = True
                break

        
        # Si encontramos la secuencia del radiofármaco, recorremos las etiquetas anidadas
        if elem.name == 'Radiopharmaceutical Information Sequence':
            for item in elem:
                for sub_elem in item:
                    if sub_elem.name == 'Radionuclide Code Sequence':
                        continue  # Omitir esta etiqueta y pasar a la siguiente
                    add_sequence_tags([sub_elem], 'Radiopharmaceutical')
            added = True

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
file_path = 'D:/Utilidades/DICOM_TO_DICOM/ToDICOM/Plantilla PET/Plantilla_PET.dcm'

# Leer datos DICOM y agrupar las etiquetas
dicom_data = read_dicom(file_path)
categories = categorize_dicom_tags_pet(dicom_data)

# Imprimir las categorías
print_categories(categories)

