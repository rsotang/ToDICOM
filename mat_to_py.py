import scipy.io

# Ruta al archivo .mat
mat_file_path = "ruta_al_archivo.mat"

# Carga del archivo .mat
mat_data = scipy.io.loadmat(mat_file_path)

# Asume que la matriz está almacenada con una clave conocida
# Sustituye 'nombre_de_la_matriz' por el nombre exacto de la variable en el archivo .mat
matriz_3d = mat_data.get('nombre_de_la_matriz')

# Verifica si se cargó correctamente
if matriz_3d is not None:
    print("Matriz 3D cargada con éxito:")
    print(matriz_3d)
else:
    print("No se encontró la matriz con el nombre especificado en el archivo .mat")