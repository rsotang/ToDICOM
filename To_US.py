import re  # Módulo de expresiones regulares

def ordenar_alfanumericamente(lista):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(lista, key=alphanum_key)

mi_lista = ['ExportImg_65.DCM', 'ExportImg_66.DCM', 'ExportImg_67.DCM', 'ExportImg_68.DCM', 'ExportImg_69.DCM', 'ExportImg_70.DCM', 'ExportImg_71.DCM', 'ExportImg_72.DCM', 'ExportImg_73.DCM', 'ExportImg_74.DCM', 'ExportImg_75.DCM', 'ExportImg_76.DCM', 'ExportImg_77.DCM', 'ExportImg_78.DCM', 'ExportImg_79.DCM', 'ExportImg_80.DCM', 'ExportImg_81.DCM', 'ExportImg_1.DCM', 'ExportImg_2.DCM', 'ExportImg_3.DCM', 'ExportImg_4.DCM', 'ExportImg_5.DCM', 'ExportImg_6.DCM', 'ExportImg_7.DCM', 'ExportImg_8.DCM', 'ExportImg_9.DCM', 'ExportImg_10.DCM', 'ExportImg_11.DCM', 'ExportImg_12.DCM', 'ExportImg_13.DCM', 'ExportImg_14.DCM', 'ExportImg_15.DCM', 'ExportImg_16.DCM', 'ExportImg_17.DCM', 'ExportImg_18.DCM', 'ExportImg_19.DCM', 'ExportImg_20.DCM', 'ExportImg_21.DCM', 'ExportImg_22.DCM', 'ExportImg_23.DCM', 'ExportImg_24.DCM', 'ExportImg_25.DCM', 'ExportImg_26.DCM', 'ExportImg_27.DCM', 'ExportImg_28.DCM', 'ExportImg_29.DCM', 'ExportImg_30.DCM', 'ExportImg_31.DCM', 'ExportImg_32.DCM', 'ExportImg_33.DCM', 'ExportImg_34.DCM', 'ExportImg_35.DCM', 'ExportImg_36.DCM', 'ExportImg_37.DCM', 'ExportImg_38.DCM', 'ExportImg_39.DCM', 'ExportImg_40.DCM', 'ExportImg_41.DCM', 'ExportImg_42.DCM', 'ExportImg_43.DCM', 'ExportImg_44.DCM', 'ExportImg_45.DCM', 'ExportImg_46.DCM', 'ExportImg_47.DCM', 'ExportImg_48.DCM', 'ExportImg_49.DCM', 'ExportImg_50.DCM', 'ExportImg_51.DCM', 'ExportImg_52.DCM', 'ExportImg_53.DCM', 'ExportImg_54.DCM', 'ExportImg_55.DCM', 'ExportImg_56.DCM', 'ExportImg_57.DCM', 'ExportImg_58.DCM', 'ExportImg_59.DCM', 'ExportImg_60.DCM', 'ExportImg_61.DCM', 'ExportImg_62.DCM', 'ExportImg_63.DCM', 'ExportImg_64.DCM']
mi_lista_ordenada = ordenar_alfanumericamente(mi_lista)

print(mi_lista_ordenada)