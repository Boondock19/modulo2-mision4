# Misión 4 · Proyecto del alumno

## Preparación
1. Conserva MySQL Server y Workbench de la Misión 3. Si no tienes su base, ejecuta
   `sql/crear_demo_mysql.sql` UNA VEZ en Workbench. Crea `ai_customer_m4_demo` sin borrar
   `ai_customer`. Si ya existen las tablas demo, consulta al docente antes de cambiarlas.
2. En terminal, entra en esta carpeta (`proyecto`). Con Conda:
   ```sh
   conda create -n mision4 python=3.12
   conda activate mision4
   python -m pip install -r requirements.txt
   python -m ipykernel install --user --name mision4 --display-name "Python (Misión 4)"
   jupyter lab
   ```
   Alternativa sin Conda: `python -m venv .venv`; activa `.venv` (Windows:
   `.venv\Scripts\activate`, macOS/Linux: `source .venv/bin/activate`) y ejecuta los comandos pip/kernel.
3. Copia `.env.example` como `.env`, configura tu usuario local y selecciona DB_NAME.
   Usa `ai_customer` para tu base de la Misión 3 o `ai_customer_m4_demo` para el kit.
   Puedes guardarlo en `proyecto/` o en la raíz del workspace. `.env` es un archivo de
   texto: no cifra ni protege por sí solo las contraseñas; no lo compartas ni lo entregues.
4. Abre `mision_4.ipynb` y selecciona el kernel Python (Misión 4).

## Archivos
- `mision_4.ipynb`: retos guiados, análisis con Pandas, gráfico y ejecución final del pipeline.
- `validaciones.py`: validación de clientes y calidad/cobertura del dataset.
- `pipeline.py`: extracción desde MySQL, informe JSON y exportaciones condicionales.
- `consulta_dataset.sql`: consulta SQL del dataset; referencia en `sql/consulta_dataset.sql`.
- `sql/consulta_dataset.sql`: consulta de referencia para comparar con la consulta principal.
- `sql/crear_demo_mysql.sql`: crea el esquema demo e inserta clientes y operaciones sintéticos.
- `datos/dataset_referencia.csv`: 12 clientes sintéticos, incluyendo tres sin operaciones.
- `datos/dataset_con_incidencias.csv`: copia deliberadamente incorrecta para Reto 4.
- `informe_prueba.json`: ejemplo del informe del dataset con incidencias.
- `requirements.txt`: dependencias de Python necesarias.
- `.env.example`: plantilla de configuración; copia a `.env` y nunca entregues este último.
- `.gitignore`: evita incluir checkpoints, configuración local y salidas generadas.

## Qué hace el código

- **SQL**: combina clientes y operaciones con `LEFT JOIN`, cuenta operaciones reales y calcula gasto y ticket medio. El agrupamiento incluye todas las columnas seleccionadas que no son agregaciones, y los clientes sin operaciones permanecen en el resultado.
- **`validar_cliente`**: devuelve todos los errores del diccionario del cliente.
- **`validar_dataset`**: comprueba las seis columnas, faltantes, duplicados, valores numéricos finitos, enteros, abandono 0/1 y cobertura de IDs; no modifica ni corrige los datos recibidos.
- **`pipeline.py`**: carga `.env`, comprueba `importe IS NULL`, ejecuta el SQL, valida, siempre guarda `informe.json` y solo exporta CSV/gráfico cuando el informe es válido. Cada corrida tiene carpeta propia.
- **Análisis/gráfico**: el notebook filtra gasto superior a 100 €, calcula count/media/mediana por abandono y compara medias. Esta descripción no demuestra causalidad.

## Comparación con la versión descargada de GitHub

Se comparó con la rama [`main` del repositorio de Jose](https://github.com/Boondock19/modulo2-mision4/tree/main), incluido el commit [`bb5f47c`](https://github.com/Boondock19/modulo2-mision4/commit/bb5f47cad075152294383d304b1b2822fcde2e3f) (“Completado reto final, corrección de nombre de columnas reto 3”). Ese commit añade el pipeline y cambia la celda del Reto 3 para mostrar los nombres de las columnas. Integramos esas ideas con los arreglos que ya habíamos hecho y con nuestra configuración local.

| Archivo | Versión GitHub | Versión de esta carpeta |
|---|---|---|
| `pipeline.py` | La versión inicial estaba pendiente; el commit de Jose añadió extracción, comprobación de importes nulos, generación del gráfico y entrada CSV opcional | Conserva lo anterior y usa nuestra carga robusta de `.env`; el informe identifica IDs de operaciones con importe `NULL`; los datasets inválidos finalizan con error y no se exportan |
| `validaciones.py` | La rama de Jose no modificó este archivo respecto a la plantilla inicial | detecta infinitos, `None` y columnas requeridas ausentes; registra errores sin corregir silenciosamente |
| `consulta_dataset.sql` | La consulta principal original agrupaba solo por ID | agrupa también por antigüedad y abandono para ser explícita con los campos seleccionados |
| `mision_4.ipynb` | El commit de Jose corrige los nombres de columnas del DataFrame del Reto 3 y contiene resultados de su base (30 clientes) | conserva esa corrección, recarga `.env` evitando valores antiguos del kernel, completa el Reto 3 y añade la ejecución final; se ejecuta con nuestra base demo (12 clientes), sin copiar resultados de otra base |
| README y evidencias | instrucciones y campos vacíos | describe el código y completa evidencias con valores observados; los roles se declaran como trabajo conjunto |
| `.gitignore` | ignoraba checkpoints del notebook | además ignora `.env` y las salidas locales |

El gráfico **no se quitó**: se mantienen `ax.bar(...)`, el título y los ejes. El pipeline guarda `gasto_por_abandono.png`; en el notebook se muestra explícitamente la figura. La opción CSV permite probar el control de calidad sin MySQL, pero no sustituye la evidencia de conexión a la base.

## Ejecución final
Desde esta carpeta (`proyecto`), ejecuta `python pipeline.py`. Cada ejecución genera
una carpeta nueva bajo `salidas/` con informe JSON y, solo cuando pasa la validación,
`dataset_clientes.csv` y `gasto_por_abandono.png`.

## Completa antes de entregar
- Entorno comprobado en esta ejecución: Python 3.14.6; dependencias de `requirements.txt`.
- Base y origen: `ai_customer_m4_demo`, MySQL local con datos sintéticos.
- Comando: `python pipeline.py` desde `proyecto`; resultados en `proyecto/salidas/ejecucion_.../`.
- Para probar el CSV de referencia sin MySQL: `python pipeline.py datos\dataset_referencia.csv`. El CSV con incidencias también bloquea la exportación y termina con error.
- Reglas e incidencias: el dataset de referencia pasa; el CSV con incidencias contiene faltantes, duplicado, dato no numérico, valores no enteros y abandono fuera de {0, 1}. Se conserva el dato de origen y se bloquean exportaciones cuando no es válido.
- Observación: la media del gasto es 195,00 € para abandono=0 y 39,17 € para abandono=1. Limitación: muestra sintética de 12 clientes; no demuestra causalidad ni permite generalizar.
- Ayuda de IA: se revisó el notebook, el SQL, el pipeline y la plantilla. Verificación: ejecución de Reto 3 y del pipeline contra MySQL, informe válido con 12 filas; prueba con datos incorrectos bloqueó CSV/PNG.
- Integrantes, grupo y fecha: Sarah Benedi y Jose Matias Gonzalez, grupo 27, 27/10/2026. El trabajo se hizo conjuntamente.

No entregues `.env`, claves ni capturas que las muestren. Entrega `.env.example` sin
credenciales reales. Reinicia el kernel y ejecuta el notebook de principio a fin.
