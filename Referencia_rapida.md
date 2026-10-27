# Referencia rápida · Misión 4

## Python
```python
cliente = {'id_cliente': 104, 'antiguedad_meses': -3, 'abandono': 2}
errores = []
if cliente['antiguedad_meses'] < 0:
    errores.append('Antigüedad negativa')
for error in errores:
    print(error)
# Definir no ejecuta; llamar sí: resultado = validar_cliente(cliente)
from validaciones import validar_cliente
```
`=` asigna; `==` compara. Una función puede devolver una lista. El contador de
clientes con errores aumenta una vez por cliente, no por cada mensaje.

## Configuración y conexión (patrón)
```python
import os
from dotenv import load_dotenv
import mysql.connector
load_dotenv('.env')
conexion = None
cursor = None
try:
    conexion = mysql.connector.connect(
        host=os.environ['DB_HOST'], port=int(os.environ['DB_PORT']),
        user=os.environ['DB_USER'], password=os.environ['DB_PASSWORD'],
        database=os.environ['DB_NAME'])
    cursor = conexion.cursor()
    cursor.execute('SELECT COUNT(*) FROM clientes')
    print(cursor.fetchone()[0])
finally:
    if cursor is not None:
        cursor.close()
    if conexion is not None:
        conexion.close()
```
No publiques `.env`. Si modificas variables, reinicia kernel/proceso.
Usa parámetros `%s` y un tuple para valores de usuario en consultas; no concatenes entradas.
`cursor.fetchall()` recupera todas las filas restantes; `cursor.description` da nombres y metadatos.

## Pandas
```python
import pandas as pd
df = pd.read_csv('datos/dataset_referencia.csv')
print(df.shape)
df.info()
print(df.isna().sum())
print(df['id_cliente'].duplicated(keep=False))
seleccion = df.loc[df['gasto_total'] > 100, ['id_cliente', 'gasto_total']]
seleccion = seleccion.sort_values('gasto_total', ascending=False)
analisis = df.copy()
analisis['sin_operaciones'] = analisis['num_operaciones'].eq(0)
resumen = analisis.groupby('abandono')['gasto_total'].agg(['count', 'mean', 'median'])
```
Convierte tipos con criterio (`pd.to_numeric`); `errors='coerce'` identifica fallos
pero no los corrige. MySQL DECIMAL puede llegar como Decimal/object. Comprueba valores,
no solo dtype. Float sirve aquí para análisis; para contabilidad conserva precisión decimal.
No confundas cero (valor conocido) con NULL (desconocido).

## Matplotlib
```python
import matplotlib.pyplot as plt
medias = df.groupby('abandono')['gasto_total'].mean()
medias = medias.rename(index={0: 'Permanece', 1: 'Abandona'})
fig, ax = plt.subplots(figsize=(6, 4))
ax.bar(medias.index, medias.values)
ax.set(title='Gasto medio por abandono', xlabel='Situación del cliente',
       ylabel='Gasto medio (€)')
fig.tight_layout()
fig.savefig('gasto_por_abandono.png', dpi=150)
plt.close(fig)
```
Comparar medias no demuestra que gastar menos cause abandono. No dibujes grupos ausentes como media cero.

## Diagnóstico
| Síntoma | Revisión |
|---|---|
| ModuleNotFoundError | ¿pip y el kernel pertenecen al mismo entorno? Usa python -m pip. |
| No conecta / conexión rechazada | Servicio MySQL activo, host y puerto. |
| Access denied | Usuario, clave y permisos de lectura en la base. |
| Unknown database | DB_NAME y base creada; reinicia tras restaurar .env. |
| Unknown table/column | Base seleccionada, esquema y nombres de la Misión 3. |
| DataFrame pierde clientes | Revisa LEFT JOIN y filtros sobre operaciones. |
| Exportación bloqueada | Abre el informe; revisa reglas, no fuerces fillna(0). |
