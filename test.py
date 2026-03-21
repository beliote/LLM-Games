import os
import requests
from dotenv import load_dotenv

# Charge tes identifiants depuis le .env
load_dotenv()

endpoint = os.getenv("AI_ENDPOINT")
api_key = os.getenv("AI_API_KEY")

# On interroge la route standard qui liste les modèles
url = f"{endpoint}/models"
headers = {"Authorization": f"Bearer {api_key}"}

print(f"Interrogation du serveur : {url}...\n")

try:
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        modeles = data.get('data', [])
        print("✅ MODÈLES DISPONIBLES SUR LE SSP CLOUD :")
        for m in modeles:
            # L'ID est le nom exact à mettre dans ton .env
            print(f" -> {m.get('id')}")
    else:
        print(f"❌ Erreur {response.status_code} : {response.text}")
        print("Vérifie que ton AI_ENDPOINT finit bien par /v1 et que ta clé est correcte.")

except Exception as e:
    print(f"Erreur de connexion : {e}")