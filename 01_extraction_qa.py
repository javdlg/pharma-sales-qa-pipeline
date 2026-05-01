import pandas as pd

file_path = "data_raw/salesdaily.csv"


def process_pharma_sales(file_path):
    print("Iniciando pipeline ETL: Extraccion y transformacion")

    # 1. Extraccion
    try:
        df = pd.read_csv(file_path)
        print(f"Archivo cargado. Filas originales: {len(df)}")
    except FileNotFoundError:
        print("Error: Archivo no encontrado.")

    # 2. Transformacion estructural (unipivot/melt)
    print("Tranformando formato ancho a largo (unipivot)...")

    # Columnas que no son medicamentos (variables de contexto)
    id_vars = ["datum", "Year", "Month", "Hour", "Weekday Name"]

    # Columnas que si son medicamentos y les aplicaremos melt
    value_vars = ["M01AB", "M01AE", "N02BA", "N02BE", "N05B", "N05C", "R03", "R06"]

    # Aplicamos melt
    df_long = pd.melt(
        df,
        id_vars=id_vars,
        value_vars=value_vars,
        var_name="codigo_atc",
        value_name="cantidad_vendida",
    )

    # 3. Limpieza y QA en el nuevo formato
    audit_log = []
    initial_rows = len(df_long)

    # Renombramos columnas para estandarizar
    df_long = df_long.rename(
        columns={
            "datum": "fecha",
            "Year": "anio",
            "Month": "mes",
            "Hour": "hora",
            "Weekday Name": "dia_semana",
        }
    )

    # QA: Verificar si hay ventas negativas (anomalia)
    ventas_negativas = len(df_long[df_long["cantidad_vendida"] < 0])
    if ventas_negativas > 0:
        df_long = df_long[df_long["cantidad_vendida"] >= 0]
        audit_log.append(
            f"Se eliminaron {ventas_negativas} registros con ventas negativas (posible error de sistema)."
        )

    # QA: Formatear fecha correctamente
    df_long["fecha"] = pd.to_datetime(df_long["fecha"], errors="coerce")
    fechas_nulas = df_long["fecha"].isnull().sum()
    if fechas_nulas > 0:
        df_long = df_long.dropna(subset=["fecha"])
        audit_log.append(
            f"Se eliminaron {fechas_nulas} registros con formato de fecha inválido."
        )

    final_rows = len(df_long)

    # Reporte
    print("\nReporte de audiroria QA:")
    print(f"Estructura final: {df_long.shape[0]} filas, {df_long.shape[1]} columnas")
    if not audit_log:
        print("- Los datos no presentaron anomalias criticas en esta validacion")
    for log in audit_log:
        print(f"- {log}")
    print(f"Porcentaje de retencion: {round((final_rows / initial_rows) * 100, 2)}")

    return df_long
