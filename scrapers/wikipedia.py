import pandas as pd
import requests
from bs4 import BeautifulSoup

def scrape(url):
    # Simuler un vrai navigateur
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 1. Récupérer le HTML
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        raise Exception(f"Erreur : {response.status_code}")
    
    print("✅ Page récupérée avec succès")

    # 2. Parser le HTML
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 3. Trouver le tableau
    table = soup.find("table", class_=lambda x: x and "wikitable" in x)
    print("✅ Tableau trouvé")

    # Afficher toutes les classes de tous les tableaux trouvés
    tables = soup.find_all("table")
    print(f"Nombre de tableaux trouvés : {len(tables)}")
    for i, t in enumerate(tables):
        print(f"Tableau {i} : class = {t.get('class')}")

    # 4. Extraire les noms des colonnes (th)
    headers_list = []
    for th in table.find_all("th"):
        headers_list.append(th.text.strip())
    
    print(f"✅ Colonnes trouvées : {headers_list}")

    # 5. Extraire les lignes de données (tr > td)
    rows = []
    for tr in table.find_all("tr")[1:]:  # [1:] pour ignorer la ligne des headers
        cells = tr.find_all("td")
        if cells:
            row = [cell.text.strip() for cell in cells]
            rows.append(row)
    
    print(f"✅ {len(rows)} lignes extraites")

    # 6. Créer un DataFrame pandas
    df = pd.DataFrame(rows, columns=headers_list[:len(rows[0])])
    
    return df