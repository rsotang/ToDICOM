import pydicom
from collections import defaultdict
import PySimpleGUI as sg

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
            # Si es una secuencia, procesarla recursivamente
            process_sequence(value)
        else:
            tags.append((elem.name, elem.tag, value))

    for elem in dataset:
        read_element(elem)
    
    return tags

def categorize_tags(tags, category_mapping):
    """Clasifica las etiquetas DICOM en categorías, manejando etiquetas anidadas."""
    categories = defaultdict(list)

    for tag in tags:
        tag_name, tag_id, tag_value = tag
        added = False
        # Verificar si la etiqueta pertenece a alguna categoría
        for category, keywords in category_mapping.items():
            if any(keyword in tag_name for keyword in keywords):
                categories[category].append(tag)
                added = True
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

  
  
  
  
  
  
  