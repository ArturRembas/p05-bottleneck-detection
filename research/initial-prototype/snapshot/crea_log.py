from datetime import datetime, timedelta
import random
import pandas as pd

random.seed(42)

activities = [
    "Cutting",
    "CNC_Milling",
    "Welding",
    "Surface_Coating",
    "Quality_Check",
]
rows = []
base_time = datetime(2026, 10, 1, 8, 0, 0)

print("Generazione di 1000 ordini industriali in corso...")

for case_id in range(1001, 2001):
    case_name = f"ORD_{case_id}"
    current_time = base_time + timedelta(
        minutes=random.randint(0, 10000)
    )  # Distribuiti su giorni

    for act in activities:
        # INIETTIAMO IL BOTTLENECK: La saldatura ha code lunghe (da 3 a 5 ore di attesa)
        if act == "Welding":
            current_time += timedelta(
                minutes=random.randint(180, 300)
            )  # 3-5 ore!
        else:
            current_time += timedelta(
                minutes=random.randint(15, 45)
            )  # Fasi normali veloci

        rows.append(
            {
                "Case_ID": case_name,
                "Activity": act,
                "Timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "Resource": f"Station_{act[:3]}",
            }
        )

df = pd.DataFrame(rows)
df.to_csv("log_manifattura_1000_ordini.csv", index=False)
print("Fatto! File creato: 'log_manifattura_1000_ordini.csv' (5.000 eventi).")
