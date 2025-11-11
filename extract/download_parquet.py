import os
from datetime import date
import requests

# 📁 Dossier local pour stocker les fichiers téléchargés
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 📅 Dates de janvier 2024 jusqu'au mois précédent
start = date(2024, 1, 1)
today = date.today()

# On ne télécharge que jusqu'au mois précédent
end_year = today.year
end_month = today.month - 1 if today.day < 28 else today.month

total_months = (end_year - start.year) * 12 + end_month - start.month + 1

# 🌐 URL de base
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"

# 📥 Téléchargement de chaque fichier .parquet
for month_offset in range(total_months):
    year = start.year + (start.month + month_offset - 1) // 12
    mon = (start.month + month_offset - 1) % 12 + 1
    filename = f"yellow_tripdata_{year}-{mon:02}.parquet"
    url = f"{BASE_URL}/{filename}"
    local_path = os.path.join(DATA_DIR, filename)

    if os.path.exists(local_path):
        print(f"[✔️] {filename} déjà téléchargé")
        continue

    print(f"[⬇️] Téléchargement de : {filename}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(local_path, "wb") as f:
                f.write(response.content)
            print(f"[✅] Sauvegardé dans {local_path}")
        elif response.status_code == 403:
            print(f"[⚠️] {filename} n'existe pas encore, on passe")
            continue
        else:
            print(f"[❌] Erreur {response.status_code} pour {filename}")
    except Exception as e:
        print(f"[❌] Erreur lors du téléchargement de {filename}: {e}")
