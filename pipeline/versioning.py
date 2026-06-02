import os
import subprocess
import pandas as pd
from datetime import datetime

def get_next_version(subject, clean_dir="data/clean"):
    """Détermine automatiquement le prochain numéro de version"""
    
    # 1. Lister tous les fichiers CSV existants pour ce sujet
    # Ex: ["population_v1.0.csv", "population_v2.0.csv"]
    existing = [
        f for f in os.listdir(clean_dir)
        if f.startswith(subject) and f.endswith(".csv")
    ]
    
    # 2. Si aucun fichier existant → première version
    if not existing:
        return "v1.0"
    
    # 3. Extraire les numéros de version existants
    # "population_v2.0.csv" → 2.0
    versions = []
    for f in existing:
        try:
            version_str = f.replace(f"{subject}_v", "").replace(".csv", "")
            versions.append(float(version_str))
        except:
            pass
    
    # 4. Incrémenter la version la plus haute
    # 2.0 → 3.0
    next_version = max(versions) + 1.0
    return f"v{int(next_version)}.0"



def save_and_version(df, subject, clean_dir="data/clean"):
    """Sauvegarde le dataset propre et le versionne avec DVC"""
    
    # 1. Créer le dossier clean s'il n'existe pas
    os.makedirs(clean_dir, exist_ok=True)
    
    # 2. Déterminer la version automatiquement
    version = get_next_version(subject, clean_dir)
    print(f"🏷️  Version : {version}")
    
    # 3. Construire le nom du fichier
    # Ex: "population_v1.0.csv"
    filename = f"{subject}_{version}.csv"
    filepath = os.path.join(clean_dir, filename)
    
    # 4. Sauvegarder le DataFrame en CSV
    df.to_csv(filepath, index=False)
    print(f"💾 Fichier sauvegardé : {filepath}")
    
    # 5. Tracker le fichier avec DVC
    subprocess.run(["dvc", "add", filepath], check=True)
    print(f"✅ Fichier tracké par DVC")
    
    # 6. Committer avec Git
    subprocess.run(["git", "add", f"{filepath}.dvc"], check=True)
    subprocess.run([
        "git", "commit", "-m",
        f"Add {subject} dataset {version}"
    ], check=True)
    print(f"✅ Commit Git créé")
    
    # 7. Créer un tag Git pour la version
    tag = f"{subject}_{version}"
    subprocess.run(["git", "tag", tag], check=True)
    print(f"✅ Tag créé : {tag}")
    
    return filepath, version
