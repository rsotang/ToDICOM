import scipy.io

def cargar_matriz_3d(path_archivo, nombre_variable):
    """
    Carga una matriz 3D desde un archivo .mat.

    Args:
        path_archivo (str): Ruta al archivo .mat.
        nombre_variable (str): Nombre de la variable dentro del archivo .mat.

    Returns:
        numpy.ndarray: La matriz 3D cargada.
        None: Si no se encuentra la variable en el archivo.
    """
    try:
        # Cargar el archivo .mat
        mat_data = scipy.io.loadmat(path_archivo)

        # Intentar extraer la variable especificada
        matriz = mat_data.get(nombre_variable)

        if matriz is not None:
            return matriz
        else:
            print(f"La variable '{nombre_variable}' no se encontró en el archivo.")
            return None
    except Exception as e:
        print(f"Error al cargar el archivo .mat: {e}")
        return None