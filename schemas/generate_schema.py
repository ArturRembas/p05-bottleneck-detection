import json
from pathlib import Path
import sys

# Trova la cartella principale del progetto in automatico
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT_DIR))

from api.main import app

# Percorso di salvataggio del file
output_path = ROOT_DIR / "schemas" / "openapi_v0.2.json"
output_path.parent.mkdir(parents=True, exist_ok=True)

with open(output_path, "w", encoding="utf-8") as f:
    json.dump(app.openapi(), f, indent=2)

print(f"OpenAPI 3.1 schema successfully saved to: {output_path}")
