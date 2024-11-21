import os
import pydicom
from scipy.ndimage import zoom
import re  # Módulo de expresiones regulares

def ordenar_alfanumericamente(lista):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(lista, key=alphanum_key)

# Define las rutas a las carpetas
carpeta_origen = "SPECT Symbia"

carpeta_plantilla = "PET"
carpeta_destino = "prueba"

# Obtiene las listas de archivos en las carpetas
archivos_carpeta_origen = os.listdir(carpeta_origen)
archivos_carpeta_plantilla = os.listdir(carpeta_plantilla)

archivos_carpeta_origen= ordenar_alfanumericamente(archivos_carpeta_origen)
archivos_carpeta_plantilla= ordenar_alfanumericamente(archivos_carpeta_plantilla)

#print(archivos_carpeta1)

#print(archivos_carpeta2)

# Itera sobre los archivos en las carpetas
for item in range(len(archivos_carpeta_origen)):
    # Carga las dos imágenes
    ds_origen = pydicom.dcmread(os.path.join(carpeta_origen, archivos_carpeta_origen[item]))
    ds_plantilla = pydicom.dcmread(os.path.join(carpeta_plantilla, archivos_carpeta_plantilla[item]))

    # Accede a la data de los píxeles
    pixel_data_origen = ds_origen.pixel_array
    pixel_data_plantilla = ds_plantilla.pixel_array

    # Calcula los factores de zoom para cada dimensión
    zoom_factor_y = pixel_data_plantilla.shape[0] / pixel_data_origen.shape[0]
    zoom_factor_x = pixel_data_plantilla.shape[1] / pixel_data_origen.shape[1]

    # Usa la función zoom de SciPy para cambiar la resolución de la imagen
    pixel_data_origen_resized = zoom(pixel_data_origen, (zoom_factor_y, zoom_factor_x))

    # Actualiza la data de los píxeles en la segunda imagen con la data de los píxeles redimensionada de la primera imagen
    ds_plantilla.PixelData = pixel_data_origen_resized.tobytes()

    # Actualiza también las etiquetas que indican las dimensiones de la imagen
    ds_plantilla.Rows, ds_plantilla.Columns = pixel_data_origen_resized.shape

    #Parece que hay un problema con la ordenacion de los frames de los stacks, en el poster del HUBU lo mencionan
    #Quizas haya que renombrar la etiqueta dle frame number según la iteración del bucle para asegurarnos, o algo por el estilo


    #Creo que la ordenación de los frames tiene que ver con el orden de la lectura de los nombres de los archivos, i.e , se lee
    # export_1, despues export_10 en vez de export_2. Tengo que comprobarlo. Si es así se puede reajustar el nombre de los       archivos , o ya si que sí cambiar el nombre de las etiquetas de frame y total frame


    ds_plantilla[0x0054, 0x0081].value = len(archivos_carpeta_origen)
    ds_plantilla[0x0054, 0x1330].value = item

  #Aun habiendo cambiado eso parece que el problema parte más del orden de importación
  #Para ello he sorteado los nombres con expresiones regulares
    # Guarda la imagen modificada en la carpeta de destino
    ds_plantilla.save_as(os.path.join(carpeta_destino, archivos_carpeta_origen[item]))
    #print(archivos_carpeta1[item])
    #print(archivos_carpeta2[item])
print('\n sacabo')