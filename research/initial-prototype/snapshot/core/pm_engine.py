import pandas as pd
import pm4py
from pm4py.visualization.dfg import visualizer as dfg_visualizer


def elabora_log_e_genera_dfg(file_path_o_buffer, col_case, col_act, col_time):
    # 1. Carica il dataset
    df = pd.read_csv(file_path_o_buffer)

    # 2. Pulizia e formattazione date
    df[col_time] = pd.to_datetime(df[col_time], errors="coerce")
    df = df.dropna(subset=[col_case, col_act, col_time])

    # 3. Formattazione standard pm4py
    df = pm4py.format_dataframe(
        df, case_id=col_case, activity_key=col_act, timestamp_key=col_time
    )

    # 4. Calcola il DFG con le durate/tempi reali tra le attività
    dfg_perf, start_activities, end_activities = pm4py.discover_performance_dfg(
        df
    )

    # 5. Genera il grafo Graphviz (usa un dizionario semplice per evitare conflitti)
    gviz = dfg_visualizer.apply(
        dfg_perf,
        log=df,
        variant=dfg_visualizer.Variants.PERFORMANCE,
        parameters={"format": "svg"},
    )



  # Trova l'arco con il tempo medio più alto (il vero collo di bottiglia!)
    worst_transition = ("N/A", "N/A")
    max_seconds = 0
    for (act1, act2), metrics in dfg_perf.items():
        durata = (
            metrics["mean"] if isinstance(metrics, dict) else metrics
        )  # durata in secondi
        if durata > max_seconds:
            max_seconds = durata
            worst_transition = (act1, act2)

    worst_hours = round(max_seconds / 3600, 1)

    kpis = {
        "total_cases": int(df[col_case].nunique()),
        "total_events": int(len(df)),
        "unique_activities": int(df[col_act].nunique()),
        "worst_bottleneck": f"{worst_transition[0]} → {worst_transition[1]}",
        "worst_hours": worst_hours,
    }

    return gviz.source, kpis
