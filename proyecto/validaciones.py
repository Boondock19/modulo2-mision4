"""Reto 1 y Reto 4. Completa las funciones sin cambiar el dato recibido."""
import pandas as pd


def validar_cliente(cliente):
    # Devuelve una lista con TODOS los errores.
    # Reglas: id presente, antigüedad >= 0 y abandono en {0, 1}.
    errores = []
    if "id_cliente" not in cliente:
        errores.append("id ausente")
    if "antiguedad_meses" not in cliente or cliente["antiguedad_meses"] < 0:
        errores.append("antiguedad invalida")
    if "abandono" not in cliente or cliente["abandono"] not in [0, 1]:
        errores.append("abandono invalido")
    return errores

def registrar(incidencias, df, regla, campo, mascara, accion):
    # Añade una incidencia solo si la máscara marca alguna fila.
    filas = df.index[mascara].tolist()
    if filas:
        incidencias.append({'regla': regla, 'campo': campo,
                            'filas': [int(f) for f in filas],
                            'accion': accion})


def validar_dataset(df, ids_esperados=None):
    # Devuelve un informe serializable como JSON:
    # valido, filas, columnas, incidencias (regla, campo, filas, accion).
    # Además de tipos/rangos, comprueba unicidad y cobertura de clientes.
    COLUMNAS = ['id_cliente', 'antiguedad_meses', 'num_operaciones',
            'gasto_total', 'ticket_medio', 'abandono']
    df = df.copy()
    incidencias = []

    for col in COLUMNAS:
        registrar(incidencias, df, 'faltante', col, df[col].isna(),
                  'revisar origen;')

    #  revisar ids duplicados
    registrar(incidencias, df, 'duplicado', 'id_cliente',
              df.duplicated(subset=['id_cliente'], keep=False),
              'eliminar duplicados;')

    # revisar que los valores que deberían ser numéricos sean finitos
    numeros = {}
    for col in COLUMNAS:
        convertido = pd.to_numeric(df[col], errors='coerce')
        no_numerico = convertido.isna() & df[col].notna()   # tenía valor pero no es número
        registrar(incidencias, df, 'no_numerico', col, no_numerico, 'revisar valor en origen')
        # TODO: añadir también los infinitos con np.isinf(convertido)
        numeros[col] = convertido

    # Validar que los valores que se esperan que sean enteros, lo sean
    for col in ['id_cliente', 'antiguedad_meses', 'num_operaciones', 'abandono']:
        valores = pd.to_numeric(df[col], errors='coerce')
        no_entero = valores.notna() & (valores % 1 != 0)
        registrar(incidencias, df, 'no_entero', col, no_entero,
                'revisar origen; no redondear sin evidencia')

    #  Validar que abandono esté entre 0 y 1
    registrar(incidencias,df, 'no entre 0 y 1', 'abandono', ~df['abandono'].isin([0, 1]),
              'revisar origen;')

    #  Validar cobertura de ids esperados
    if ids_esperados is not None:
        ids_esperados = set(ids_esperados)
        ids_presentes = set(df['id_cliente'].dropna().unique())
        ids_faltantes = ids_esperados - ids_presentes
        if ids_faltantes:
            incidencias.append({'regla': 'faltante', 'campo': 'id_cliente',
                                'filas': list(ids_faltantes),
                                'accion': 'revisar origen;'})
            
    return {'valido': len(incidencias) == 0, 'filas': len(df),
            'columnas': list(df.columns), 'incidencias': incidencias}
