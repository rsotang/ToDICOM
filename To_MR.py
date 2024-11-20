import os
import pydicom
from scipy.ndimage import zoom
import re  # Módulo de expresiones regulares

def ordenar_alfanumericamente(lista):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(lista, key=alphanum_key)

# Define las rutas a las carpetas
carpeta1 = "Reso vieja"

carpeta2 = "Plantilla reso"
carpeta_destino = "prueba"

# Obtiene las listas de archivos en las carpetas
archivos_carpeta1 = os.listdir(carpeta1)
archivos_carpeta2 = os.listdir(carpeta2)

archivos_carpeta1= ordenar_alfanumericamente(archivos_carpeta1)
archivos_carpeta2= ordenar_alfanumericamente(archivos_carpeta2)

#print(archivos_carpeta1)

#print(archivos_carpeta2)

# Itera sobre los archivos en las carpetas teniendo en cuenta que habra que portear de menos elementos a mas
num_files=len(archivos_carpeta2)
for item in range(len(archivos_carpeta1)):
    # Carga las dos imágenes
    ds1 = pydicom.dcmread(os.path.join(carpeta1, archivos_carpeta1[num_files-item]))
    ds2 = pydicom.dcmread(os.path.join(carpeta2, archivos_carpeta2[item]))

    # Accede a la data de los píxeles
    pixel_data1 = ds1.pixel_array
    pixel_data2 = ds2.pixel_array

    # Calcula los factores de zoom para cada dimensión
    zoom_factor_y = pixel_data2.shape[0] / pixel_data1.shape[0]
    zoom_factor_x = pixel_data2.shape[1] / pixel_data1.shape[1]

    # Usa la función zoom de SciPy para cambiar la resolución de la imagen
    pixel_data1_resized = zoom(pixel_data1, (zoom_factor_y, zoom_factor_x))

    # Actualiza la data de los píxeles en la segunda imagen con la data de los píxeles redimensionada de la primera imagen
    ds2.PixelData = pixel_data1_resized.tobytes()

    # Actualiza también las etiquetas que indican las dimensiones de la imagen
    ds2.Rows, ds2.Columns = pixel_data1_resized.shape

    #Parece que hay un problema con la ordenacion de los frames de los stacks, en el poster del HUBU lo mencionan
    #Quizas haya que renombrar la etiqueta dle frame number según la iteración del bucle para asegurarnos, o algo por el estilo


    #Creo que la ordenación de los frames tiene que ver con el orden de la lectura de los nombres de los archivos, i.e , se lee
    # export_1, despues export_10 en vez de export_2. Tengo que comprobarlo. Si es así se puede reajustar el nombre de los       archivos , o ya si que sí cambiar el nombre de las etiquetas de frame y total frame


   # ds2[0x0054, 0x0081].value = len(archivos_carpeta1)
   # ds2[0x0054, 0x1330].value = item

    # Guarda la imagen modificada en la carpeta de destino
    ds2.save_as(os.path.join(carpeta_destino, archivos_carpeta1[item]))
    #print(archivos_carpeta1[item])
    #print(archivos_carpeta2[item])
print('\n sacabo')