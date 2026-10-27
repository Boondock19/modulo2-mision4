"""Reto final: completa este script y ejecútalo desde una terminal nueva."""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from dotenv import load_dotenv

try:
    import mysql.connector
    from mysql.connector import Error
except ModuleNotFoundError as exc:  # pragma: no cover - depende del entorno
    raise RuntimeError(
        "Falta mysql-connector-python. Instálalo con: python -m pip install -r requirements.txt"
    ) from exc

from validaciones import validar_dataset

BASE = Path(__file__).resolve().parent
SQL_QUERY_PATH = BASE / "consulta_dataset.sql"


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
        "autocommit": False,
    }

    if not all(config[key] for key in ["host", "user", "password", "database"]):
        raise ValueError("Faltan variables de entorno en .env: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME.")

    conexion = None
    cursor = None
    try:
        conexion = mysql.connector.connect(**config)
        cursor = conexion.cursor()

        cursor.execute(
            "SELECT id_operacion FROM operaciones "
            "WHERE importe IS NULL ORDER BY id_operacion"
        )
        ids_operaciones_nulas = [int(fila[0]) for fila in cursor.fetchall()]

        query = SQL_QUERY_PATH.read_text(encoding="utf-8")
        cursor.execute(query)
        columnas = [columna[0] for columna in cursor.description]
        filas = cursor.fetchall()
        df = pd.DataFrame(filas, columns=columnas)

        cursor.execute("SELECT id_cliente FROM clientes ORDER BY id_cliente")
        ids_esperados = [int(fila[0]) for fila in cursor.fetchall()]
        return df, ids_esperados, ids_operaciones_nulas
    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None and conexion.is_connected():
            conexion.close()


def _guardar_informe(ruta, informe):
    with open(ruta, "w", encoding="utf-8") as fichero:
        json.dump(informe, fichero, ensure_ascii=False, indent=2)


def _guardar_grafico(df, ruta):
    analisis = df.copy()
    analisis["sin_operaciones"] = analisis["num_operaciones"].eq(0)

    resumen = analisis.groupby("abandono")["gasto_total"].agg(["count", "mean", "median"])
    for grupo in [0, 1]:
        if grupo not in resumen.index:
            print(f"Aviso: no hay clientes con abandono={grupo}; su media no es 0, es desconocida")

    medias = resumen["mean"].rename(index={0: "Permanece", 1: "Abandona"})

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(medias.index, medias.values)
    ax.set_title("Gasto medio por situación del cliente")
    ax.set_xlabel("Situación del cliente")
    ax.set_ylabel("Gasto medio (€)")
    fig.tight_layout()
    fig.savefig(ruta, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main(argv=None):
    # Crea una carpeta nueva para cada ejecución en salidas/.
    # Extrae -> valida -> escribe informe (también si falla).
    # Solo si el informe es válido: exporta CSV y gráfico.
    parser = argparse.ArgumentParser(description="Extrae y valida el dataset de clientes.")
    parser.add_argument(
        "dataset_csv",
        nargs="?",
        help="CSV local a validar en vez de consultar MySQL (ruta relativa a proyecto).",
    )
    args = parser.parse_args([] if argv is None else argv)

    salidas = BASE / "salidas"
    salidas.mkdir(exist_ok=True)
    carpeta_ejecucion = salidas / datetime.now().strftime("ejecucion_%Y%m%d_%H%M%S_%f")
    carpeta_ejecucion.mkdir(parents=True, exist_ok=False)

    df = None
    ids_esperados = None
    ids_operaciones_nulas = []
    origen = None
    informe = {
        "valido": False,
        "filas": 0,
        "columnas": [],
        "incidencias": [{
            "regla": "error",
            "campo": "extract",
            "filas": [],
            "accion": "revisar origen;"
        }],
    }
    error_pipeline = None

    try:
        if args.dataset_csv:
            ruta_csv = Path(args.dataset_csv)
            if not ruta_csv.is_absolute():
                ruta_csv = BASE / ruta_csv
            df = pd.read_csv(ruta_csv)
            origen = f"CSV: {ruta_csv}"
        else:
            df, ids_esperados, ids_operaciones_nulas = extraer_dataset()
            origen = f"MySQL: {os.getenv('DB_NAME')}"

        informe = validar_dataset(df, ids_esperados)
        informe["origen"] = origen
        if ids_operaciones_nulas:
            informe["incidencias"].append({
                "regla": "importe_null",
                "campo": "operaciones.importe",
                "filas": list(range(len(ids_operaciones_nulas))),
                "ids_operacion": ids_operaciones_nulas,
                "accion": "revisar origen; NULL no equivale a 0",
            })
            informe["valido"] = False
    except Exception as exc:
        error_pipeline = exc
        print(f"Error en el pipeline: {exc}")
        informe = {
            "valido": False,
            "filas": 0 if df is None else len(df),
            "columnas": list(df.columns) if df is not None else [],
            "incidencias": [{
                "regla": "error",
                "campo": "extract",
                "filas": [],
                "accion": str(exc)
            }],
        }
    finally:
        _guardar_informe(carpeta_ejecucion / "informe.json", informe)

    print(f"Informe guardado en: {carpeta_ejecucion / 'informe.json'}")
    if error_pipeline is not None:
        raise RuntimeError(
            f"No se pudo completar el pipeline. Consulta el informe en {carpeta_ejecucion}."
        ) from error_pipeline

    if not informe.get("valido"):
        raise ValueError(
            f"El dataset no pasó la validación. No se exportaron CSV ni PNG. "
            f"Consulta el informe en {carpeta_ejecucion}."
        )

    df.to_csv(carpeta_ejecucion / "dataset_clientes.csv", index=False)
    _guardar_grafico(df, carpeta_ejecucion / "gasto_por_abandono.png")
    return carpeta_ejecucion


if __name__ == "__main__":
    main(sys.argv[1:])
