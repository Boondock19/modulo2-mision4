# Evidencias · Misión 4

> Hemos completado estas evidencias con las pruebas realizadas. No entregamos `.env`,
> contraseñas ni capturas que muestren credenciales.

Integrantes: Sarah Benedi y Jose Matias Gonzalez

Fecha: 27/10/2026

Grupo:

Trabajamos juntos en el notebook, la consulta a MySQL, las validaciones y el pipeline. Fuimos revisando y probando las partes entre los dos.

## Origen y entorno

- Usamos MySQL Workbench con la base `ai_customer_m4_demo`, que contiene datos sintéticos.
- El entorno de esta ejecución fue Python 3.14.6, con `mysql-connector-python`, pandas y matplotlib.
- Comprobamos 12 clientes, 19 operaciones y ningún `importe IS NULL`.
- Comando del reto final, ejecutado desde `proyecto`: `python pipeline.py`.
- Ejecutamos el notebook completo desde un kernel nuevo: las 8 celdas de código terminaron sin errores y el gráfico apareció en el notebook.

## 1. Inspector de clientes

Probamos clientes válidos e inválidos. El cliente con antigüedad -3 y abandono 2 devuelve dos errores; el que no tiene ID devuelve `id ausente`. En los ejemplos del notebook, 1 cliente tiene errores. Revisamos todas las reglas para no ocultar otros problemas del mismo cliente.

## 2. Puente Python–MySQL

Workbench y Python devolvieron 12 clientes. Los cinco primeros por ID son 101, 102, 103, 104 y 105.

Al principio el notebook intentaba conectarse con una configuración antigua del kernel. Recargamos `.env` con `override=True` y comprobamos que conectaba usando el host configurado. También probamos un nombre de base inexistente: MySQL devolvió el error 1049 (`Unknown database`). Al volver a la base correcta, conectó y recuperó los 12 clientes.

El cursor y la conexión se cierran en `finally`, para que también se liberen si una consulta falla.

## 3. Recuperación del dataset (Reto 3)

Usamos `proyecto/consulta_dataset.sql`. Elegimos `LEFT JOIN` para que también aparezcan los clientes que no tienen operaciones. Para ellos, el conteo de operaciones es 0 y los agregados usan `IFNULL`.

El resultado tiene 12 filas y estas seis columnas: `id_cliente`, `antiguedad_meses`, `num_operaciones`, `gasto_total`, `ticket_medio` y `abandono`. No encontramos faltantes, IDs duplicados ni clientes ausentes. Los clientes 104, 107 y 112 tienen cero operaciones y gasto total 0. Antes de agregar comprobamos si había importes `NULL`; encontramos 0.

MySQL devuelve `gasto_total` y `ticket_medio` como `Decimal`, que pandas muestra con tipo `object`. Conservamos esos valores y comprobamos que la validación del pipeline pasa.

## 4. Control de calidad (Reto 4)

Las filas de la tabla son posiciones desde cero en `dataset_con_incidencias.csv`; cuando un ID está vacío, se indica como ausente.

| Campo | Regla | Filas afectadas (posición e ID) | Evidencia | Acción | Resultado |
|---|---|---|---|---|---|
| `id_cliente` | faltante | 3 (ID ausente); además falta el ID esperado 104 | Valor vacío y cobertura incompleta | Revisar el origen; no inventar el ID | Dataset inválido |
| `gasto_total` | faltante | 4 (ID 105) | Valor vacío | Revisar el origen; no reemplazar por cero sin evidencia | Dataset inválido |
| `id_cliente` | duplicado | 0 y 12 (ID 101) | El mismo ID aparece dos veces | Investigar el duplicado; no borrar automáticamente | Dataset inválido |
| `gasto_total` | no numérico | 7 (ID 108) | Valor `error` | Corregir solo con evidencia del origen | Dataset inválido |
| `antiguedad_meses` | no entero | 8 (ID 109) | Valor 2.5 | Revisar; no redondear sin evidencia | Dataset inválido |
| `num_operaciones` | no entero | 5 (ID 106) | Valor 1.5 | Revisar; no redondear sin evidencia | Dataset inválido |
| `abandono` | fuera de 0/1 | 2 (ID 103) | Valor 2 | Revisar el valor de origen | Dataset inválido |

- El archivo con incidencias tiene 13 filas; el de referencia tiene 12. El primero da `valido=False` y el dataset real da `valido=True`.
- No rellenamos ni borramos valores automáticamente: primero dejamos las incidencias registradas y bloqueamos las exportaciones.
- Probamos también un infinito y una columna requerida ausente; ambos hacen que el dataset no pase la validación.
- Una ejecución de conexión fallida guardó su informe en `proyecto/salidas/ejecucion_20261027_175503/informe.json`.
- En la prueba con datos incorrectos, `proyecto/salidas/ejecucion_20261027_180901/` contiene solo `informe.json`; no se crearon CSV ni PNG.

## 5. Pandas y gráfico

- Al filtrar `gasto_total > 100` y ordenar de mayor a menor, aparecen los clientes 105 (400 €), 109 (270 €), 103 (240 €) y 101 (180 €).
- Creamos `sin_operaciones` en una copia para el análisis y mantuvimos las seis columnas originales en el CSV.
- Este es el resumen por abandono:

| Abandono | Clientes | Gasto medio (€) | Mediana (€) |
|---|---:|---:|---:|
| 0 (permanece) | 6 | 195,00 | 210,00 |
| 1 (abandona) | 6 | 39,17 | 37,50 |

- El gráfico compara el gasto medio de los dos grupos e indica el título, los ejes y los euros.
- En estos datos, el grupo que permanece tiene un gasto medio mayor. Como son solo 12 clientes sintéticos, no podemos concluir que el gasto cause el abandono ni generalizar el resultado.

## 6. Reto final, reproducibilidad y defensa

- Ejecutamos `python pipeline.py` desde `proyecto`. Cada ejecución crea una carpeta nueva.
- Ejecutamos el notebook completo desde un kernel nuevo. La corrida final de MySQL quedó en `proyecto/salidas/ejecucion_20261027_183610_262153/`: generó el CSV de 12 filas y 6 columnas, un informe con `valido: true` y el PNG.
- Probamos también `python pipeline.py datos\dataset_referencia.csv` para validar el CSV de referencia sin MySQL. Con `datos\dataset_con_incidencias.csv`, el pipeline termina con error y su carpeta contiene solo el JSON, sin CSV ni PNG.
- Simulamos operaciones con `importe NULL`: el informe registra los IDs de operación afectados, marca el dataset como inválido y no exporta CSV ni PNG.
- Revisamos `validar_dataset` con los datos de referencia y con el CSV de incidencias. La regla de `num_operaciones` detecta el valor 1.5 porque el número de operaciones debe ser entero.
- Usamos asistencia de IA para revisar y completar partes del notebook, la consulta, las validaciones y el pipeline. Después ejecutamos el notebook desde un kernel limpio, contrastamos los 12 clientes con MySQL y comprobamos las exportaciones y el informe.

Hicimos el proyecto entre los dos y revisamos juntos el resultado. Para defenderlo, podemos apoyarnos en las pruebas que hicimos: la consulta devolvió los clientes sin operaciones, la validación detectó los errores del CSV de prueba y el pipeline generó los archivos cuando el dataset fue válido. La diferencia entre los grupos es descriptiva; con estos datos no afirmamos que una cosa cause la otra.
