# Evidencias · Misión 4

Nombre(s), fecha, grupo y reparto de roles: Sarah Benedi y Jose Matias Gonzalez; pruebas: 28/10/2026; grupo: no indicado. Reparto de exposición: Sarah explica `validar_dataset`; Matias, la consulta y `extraer_dataset`. Ambos revisamos el flujo completo.
Origen de datos (MySQL / CSV de respaldo), base y entorno: base MySQL de datos sintéticos `ai_customer_m4_demo` y CSV de respaldo; Python 3.14.6, pandas, mysql-connector-python y matplotlib.

## 1. Inspector
Casos: válido → []; antigüedad negativa → un error; cliente 104 con -3 y 2 → dos errores.
Caso id ausente → error. Nº de clientes con errores en la lista: 1 de 3 en los ejemplos del notebook.
Explica por qué no devuelves el resultado tras el primer if: para recoger todos los errores del mismo cliente y no ocultar, por ejemplo, el abandono inválido si ya encontramos una antigüedad negativa.

## 2. Puente Python–MySQL
Recuento de clientes en Workbench / Python: 12 / 12 en la comprobación guardada del 27/10.
Primeras cinco filas (captura sin credenciales): ids 101–105; en el CSV de respaldo: (101, 12, 3, 180, 60, 0), (102, 4, 1, 30, 30, 1), (103, 24, 2, 240, 120, 0), (104, 2, 0, 0, 0, 1), (105, 36, 4, 400, 100, 0). No se incluye una captura de Workbench en este archivo.
Error provocado con DB_NAME, diagnóstico y recuperación: con un nombre de base inexistente MySQL devolvió el error 1049 (`Unknown database`); al volver a `ai_customer_m4_demo`, la prueba guardada recuperó los 12 clientes. En una repetición limpia del notebook el 28/10 apareció otro error, 2017 (`Can't open named pipe`, host `.`), así que esa repetición no llegó a consultar la base.
Explica dónde se cierran cursor y conexión: en `finally`, cerramos el cursor y luego la conexión si seguía abierta, incluso si la consulta falla.

## 3. Dataset
Consulta usada y explicación del LEFT JOIN: se conserva la consulta original de la Misión 3, con `LEFT JOIN operaciones` y agrupación por `c.id_cliente`; así también aparecen clientes sin operaciones, con `COUNT(o.id_operacion) = 0` y agregados convertidos a 0 por `IFNULL`.
shape / tipos / faltantes / duplicados / comparación de ids: 12 × 6; el resultado MySQL guardado tenía los importes `Decimal` como `object` en pandas; 0 faltantes y 0 ids duplicados; los ids 101–112 coinciden con los esperados. En el CSV de respaldo, las seis columnas se leen como `int64`.
Cliente sin operaciones que se conserva y valores obtenidos: por ejemplo, el cliente 104 tiene 0 operaciones, gasto total 0 y ticket medio 0; también se conservan 107 y 112.
Cómo detectaste importes desconocidos antes de la agregación: se consultan las operaciones y se comprueba `importe.isna()` antes de ejecutar la agregación; en la base probada había 0 importes `NULL`. En una simulación controlada con `NULL`, el informe registró los ids de operación 51 y 58 y bloqueó las exportaciones.

## 4. Calidad
| Campo | Regla | Filas afectadas (posición e id) | Evidencia | Acción | Resultado |
|---|---|---|---|---|---|
| `id_cliente` | faltante | fila 3 (id vacío) | valor nulo | revisar el origen; no inventar el id | inválido |
| `gasto_total` | faltante | fila 4 (id 105) | valor nulo | revisar el origen | inválido |
| `id_cliente` | duplicado | filas 0 y 12 (id 101) | mismo id repetido | comprobar el origen antes de eliminar | inválido |
| `gasto_total` | no numérico | fila 7 (id 108) | valor `error` | corregir solo con evidencia del origen | inválido |
| `antiguedad_meses` | no entero | fila 8 (id 109) | valor 2.5 | revisar; no redondear sin evidencia | inválido |
| `num_operaciones` | no entero | fila 5 (id 106) | valor 1.5 | revisar; no redondear sin evidencia | inválido |
| `abandono` | fuera de 0/1 | fila 2 (id 103) | valor 2 | revisar el origen | inválido |
| `id_cliente` | cobertura incompleta | id esperado 104 ausente | no aparece entre los ids recibidos | revisar la fuente y recuperar el dato | inválido |

Filas antes / después: 13 / 13; no corregimos ni eliminamos filas automáticamente.
Correcciones verificadas / incidencias sin resolver: el CSV de referencia pasa. El de incidencias conserva sus valores para poder revisarlos: el informe del reto 4 registró 8 incidencias, incluida la falta del id esperado 104. La antigüedad -4 del id 102 está en el CSV, pero el validador del dataset no la señala; queda como limitación observada.
Resultado con dataset válido / con dataset incorrecto: válido → `valido: true`, 12 filas y CSV/PNG; incorrecto → `valido: false`, 13 filas, 7 incidencias detectadas por el pipeline y solo JSON. La prueba del reto 4 registra además la cobertura incompleta del id 104.
Ruta del informe guardado en la ejecución inválida: `proyecto/salidas/20261028_012430/informe.json`.

## 5. Pandas y gráfico
Filtro gasto > 100, columna sin_operaciones y resumen por abandono: ids filtrados 101, 103, 105 y 109; sin operaciones: 104, 107 y 112. En el CSV de referencia, abandono 0: 6 clientes, media 195 y mediana 210; abandono 1: 6, media 39,17 y mediana 37,5.
Título, ejes y unidad del gráfico: “Gasto medio por situación del cliente”; eje X “Situación del cliente”; eje Y “Gasto medio (€)”.
Una observación sustentada en valores: en esta muestra el gasto medio del grupo que permanece es 195, frente a 39,17 en el grupo que abandona.
Una limitación (muestra, causalidad o grupo ausente): solo hay 12 clientes sintéticos; la diferencia observada no demuestra que el gasto cause el abandono.

## 6. Reproducibilidad y defensa individual
Comando ejecutado desde terminal nueva: desde `proyecto`, `python pipeline.py datos\dataset_referencia.csv`; para la prueba inválida, `python pipeline.py datos\dataset_con_incidencias.csv`.
Ruta de CSV / JSON / PNG y resultado de segunda ejecución: segunda ejecución válida: `proyecto/salidas/20261028_012558/`; contiene `dataset_clientes.csv`, `informe.json` y `gasto_por_abandono.png`, con `valido: true` y 12 filas. La primera quedó en `proyecto/salidas/20261028_012427/` y también fue válida.
Comprobación de que una ejecución inválida no genera CSV ni PNG nuevos: `proyecto/salidas/20261028_012430/` contiene solo `informe.json`; el comando terminó con código 1. No se generaron CSV ni PNG.
Cada integrante: Sarah explica `validar_dataset` y cómo marca faltantes, duplicados y valores fuera de rango; Matias explica el `LEFT JOIN` y cómo `extraer_dataset` comprueba importes `NULL` antes de agregarlos. Ambos revisamos el proyecto. No atribuimos reglas a una sola persona: comprobamos que los datos inválidos bloquean las exportaciones y vimos que la antigüedad negativa del id 102 no se detecta.
Ayuda de IA recibida, fragmento revisado y prueba de verificación: usamos IA como apoyo para revisar el pipeline y preparar pruebas, no como sustituto de la revisión. Revisamos la celda final y la validación del CSV; lo comprobamos ejecutando el CSV de referencia dos veces y el CSV con incidencias una vez, y comprobando los informes y archivos generados.
