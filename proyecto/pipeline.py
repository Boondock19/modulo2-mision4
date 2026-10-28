"""Reto final: completa este script y ejecútalo desde una terminal nueva."""
from pathlib import Path
from datetime import datetime
import json
import os
import sys
from dotenv import load_dotenv
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # sin ventanas: solo guardamos el PNG
import matplotlib.pyplot as plt
import mysql.connector
from mysql.connector import Error
from validaciones import validar_dataset

BASE = Path(__file__).resolve().parent


def extraer_dataset():
    # Lee .env. Conecta a MySQL. Comprueba importes NULL en operaciones.
    # Ejecuta consulta_dataset.sql. Recupera también los ids de clientes.
    # Cierra cursor y conexión en finally, incluso si hay una excepción.

    env_path = next((path for path in (BASE / ".env", BASE.parent / ".env") if path.is_file()), None)
    if env_path is None:
        raise FileNotFoundError(
            "No existe .env en proyecto ni en la carpeta raíz. Copia .env.example como .env "
            "y rellena tus credenciales."
        )
    load_dotenv(env_path, override=True)
    config = {
        "host": os.getenv("DB_HOST"),
        "port": int(os.getenv("DB_PORT", 3306)),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME"),
    }

    if not all(config[key] for key in ["host", "user", "password", "database"]):
        raise ValueError("Faltan variables de entorno en .env: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME.")

    conexion = None
    cursor = None

    try:

        # 2. Conectar con mysql
        conexion = mysql.connector.connect(**config)
        cursor = conexion.cursor()

        # 3. Validar importes NULL en operaciones ANTES de agregar:
        # SUM/AVG ignoran los NULL y IFNULL los convertiría en 0.
        cursor.execute("SELECT id_operacion, id_cliente, importe FROM operaciones")
        df_operaciones = pd.DataFrame(cursor.fetchall(),
                                      columns=[d[0] for d in cursor.description])
        df_importes_null = df_operaciones[df_operaciones['importe'].isna()]
        print("Operaciones con importe NULL:", len(df_importes_null))
        if not df_importes_null.empty:
            print(df_importes_null)
        print("-------------------------")

        # 4. Ejecutar la consulta del archivo consulta_dataset.sql
        consulta = (BASE / "consulta_dataset.sql").read_text(encoding="utf-8")
        cursor.execute(consulta)
        df_resultado_query = pd.DataFrame(cursor.fetchall(),
                                          columns=[d[0] for d in cursor.description])

        print(df_resultado_query)
        print("-------------------------")
        print("SHAPE: ",df_resultado_query.shape)
        print("-------------------------")
        df_resultado_query.info()
        print("-------------------------")
        print(df_resultado_query.isna().sum())

        # 5. Recuperar los ids de clientes (ids esperados para la cobertura)
        cursor.execute("SELECT id_cliente FROM clientes ORDER BY id_cliente")
        ids_clientes = [fila[0] for fila in cursor.fetchall()]

        return df_resultado_query, ids_clientes, df_importes_null

    finally:
    # 6. Cerrar recursos SIEMPRE, también si algo falló
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()
        print("Se ha cerrado la conexion")


def generar_grafico(df, ruta):
    # Gasto medio por abandono. DECIMAL de MySQL llega como object: convertimos.
    gasto = pd.to_numeric(df["gasto_total"])
    medias = gasto.groupby(df["abandono"]).mean()

    # Si falta un grupo no lo dibujamos como 0: su media es desconocida.
    for grupo in [0, 1]:
        if grupo not in medias.index:
            print(f"Aviso: no hay clientes con abandono={grupo}; no se dibuja su barra")

    medias = medias.rename(index={0: "Permanece", 1: "Abandona"})
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(medias.index, medias.values)
    ax.set(title="Gasto medio por situación del cliente",
           xlabel="Situación del cliente",
           ylabel="Gasto medio (€)")
    fig.tight_layout()
    fig.savefig(ruta, dpi=150)
    plt.close(fig)


def main():
    # Crea una carpeta nueva para cada ejecución en salidas/.
    # Extrae -> valida -> escribe informe (también si falla).
    # Solo si el informe es válido: exporta CSV y gráfico.

    # 1. Una carpeta por ejecución (fecha y hora), nunca se sobrescribe
    carpeta = BASE / "salidas" / datetime.now().strftime("%Y%m%d_%H%M%S")
    carpeta.mkdir(parents=True, exist_ok=False)

    # 2. Extraer data
    try:
        if len(sys.argv) > 1:
            origen = sys.argv[1]
            df = pd.read_csv(BASE / origen)
            ids_clientes = None
            df_importes_null = pd.DataFrame()
        else:
            df, ids_clientes, df_importes_null = extraer_dataset()
            origen = "MySQL: " + str(os.getenv("DB_NAME"))  # .env ya cargado al extraer
    except Exception as e:
        # Si la extracción falla también dejamos informe
        informe = {"valido": False, "filas": 0, "columnas": [],
                   "incidencias": [{"regla": "extraccion", "campo": None,
                                    "filas": [], "accion": f"revisar conexión/consulta: {e}"}]}
        guardar_informe(informe, carpeta)
        print("Extracción fallida. Informe en:", carpeta)
        sys.exit(1)

    # 3. Validar
    informe = validar_dataset(df, ids_clientes)
    if not df_importes_null.empty:
        informe["incidencias"].append({
            "regla": "importe_null", "campo": "operaciones.importe",
            "filas": [int(i) for i in df_importes_null["id_operacion"]],
            "accion": "revisar origen; NULL no equivale a 0"})
        informe["valido"] = False
    informe["origen"] = origen

    # 4. Guardar informe 
    guardar_informe(informe, carpeta)

    # 5. Exportar solo si pasa la validación
    if informe["valido"]:
        df.to_csv(carpeta / "dataset_clientes.csv", index=False)
        generar_grafico(df, carpeta / "gasto_por_abandono.png")
        print("Validación OK. CSV y gráfico en:", carpeta)
    else:
        print(f"Validación fallida ({len(informe['incidencias'])} incidencias). "
              "Exportación bloqueada. Informe en:", carpeta)
        sys.exit(1)


def guardar_informe(informe, carpeta):
    with open(carpeta / "informe.json", "w", encoding="utf-8") as f:
        json.dump(informe, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
