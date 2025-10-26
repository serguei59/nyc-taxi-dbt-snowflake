import os
from datetime import datetime
import requests

# 📁 Dossier local pour stocker les fichiers téléchargés
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 📅 Dates de janvier 2024 jusqu'à aujourd'hui
start = datetime(2024, 1, 1)
end = datetime.today()

# 🌐 URL de base
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

# 📥 Téléchargement de chaque fichier .parquet
for month in range((end.year - start.year) * 12 + end.month - start.month + 1):
    year = start.year + (start.month + month - 1) // 12
    mon = (start.month + month - 1) % 12 + 1
    filename = f"yellow_tripdata_{year}-{mon:02}.parquet"
    url = f"{BASE_URL}/{filename}"
    local_path = os.path.join(DATA_DIR, filename)

    if os.path.exists(local_path):
        print(f"[✔️] {filename} déjà téléchargé")
        continue

    print(f"[⬇️] Téléchargement de : {filename}")
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(local_path, "wb") as f:
            f.write(response.content)
        print(f"[✅] Sauvegardé dans {local_path}")
    else:
        print(f"[❌] Erreur {response.status_code} pour {filename}")
