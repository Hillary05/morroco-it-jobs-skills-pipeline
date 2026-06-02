import pandas as pd

def check_no_empty_country(df):
    """Vérifie qu'aucun pays n'est vide"""
    
    # 1. Récupérer le nom de la première colonne (c'est toujours le nom du pays)
    country_col = df.columns[0]
    
    # 2. Compter les valeurs vides avec isna().sum()
    # isna() retourne True pour chaque valeur vide, sum() les additionne
    empty_count = df[country_col].isna().sum()
    
    # 3. Si on trouve des valeurs vides → échec
    if empty_count > 0:
        return {
            "success": False,
            "message": f"❌ {empty_count} lignes sans nom de pays trouvées"
        }
    
    # 4. Sinon → succès
    return {
        "success": True,
        "message": "✅ Aucun pays vide trouvé"
    }


def check_positive_population(df):
    """Vérifie que toutes les valeurs de population sont positives"""
    
    # 1. Vérifier si la colonne Population existe
    # Si elle n'existe pas sur cette page → on ignore cette vérification
    if "Population" not in df.columns:
        return {
            "success": True,
            "message": "✅ Pas de colonne Population à vérifier"
        }
    
    # 2. Chercher les valeurs négatives ou égales à zéro
    # df["Population"] < 0 retourne True pour chaque valeur négative
    # .sum() compte le nombre de True
    negative_count = (df["Population"] < 0).sum()
    
    # 3. Chercher aussi les valeurs nulles (NaN)
    # Une population NaN est aussi invalide
    null_count = df["Population"].isna().sum()
    
    # 4. Si on trouve des valeurs invalides → échec
    if negative_count > 0:
        return {
            "success": False,
            "message": f"❌ {negative_count} valeurs de population négatives trouvées"
        }
    
    if null_count > 0:
        return {
            "success": False,
            "message": f"❌ {null_count} valeurs de population manquantes trouvées"
        }
    
    # 5. Sinon → succès
    return {
        "success": True,
        "message": "✅ Toutes les valeurs de population sont positives"
    }


def check_percentage_range(df):
    """Vérifie que les pourcentages sont entre 0 et 100"""
    
    # 1. Chercher automatiquement toutes les colonnes contenant "%"
    # On réutilise la même logique que dans cleaner.py
    percent_cols = [col for col in df.columns if "%" in col]
    
    # 2. Si aucune colonne de pourcentage → on ignore
    if not percent_cols:
        return {
            "success": True,
            "message": "✅ Pas de colonne pourcentage à vérifier"
        }
    
    # 3. Pour chaque colonne de pourcentage, vérifier que les valeurs sont entre 0 et 100
    for col in percent_cols:
        # Compter les valeurs hors intervalle [0, 100]
        # On ignore les NaN avec dropna() avant de comparer
        invalid_count = ((df[col].dropna() < 0) | (df[col].dropna() > 100)).sum()
        
        # 4. Si on trouve des valeurs invalides → échec
        if invalid_count > 0:
            return {
                "success": False,
                "message": f"❌ {invalid_count} valeurs hors intervalle [0-100] dans la colonne {col}"
            }
    
    # 5. Sinon → succès
    return {
        "success": True,
        "message": "✅ Tous les pourcentages sont entre 0 et 100"
    }


def check_missing_values(df, threshold=0.15):
    """Vérifie que les valeurs manquantes sont moins de 15% par colonne"""
    
    # 1. Pour chaque colonne, calculer le pourcentage de valeurs manquantes
    # isna().mean() calcule la proportion de NaN (ex: 0.12 = 12%)
    missing_ratio = df.isna().mean()
    
    # 2. Chercher les colonnes qui dépassent le seuil de 15%
    # missing_ratio > threshold retourne True pour chaque colonne problématique
    problematic_cols = missing_ratio[missing_ratio > threshold]
    
    # 3. Si on trouve des colonnes problématiques → échec
    if len(problematic_cols) > 0:
        # Construire un message détaillé pour chaque colonne problématique
        details = ", ".join([
            f"{col} ({round(ratio * 100, 1)}%)" 
            for col, ratio in problematic_cols.items()
        ])
        return {
            "success": False,
            "message": f"❌ Colonnes avec trop de valeurs manquantes : {details}"
        }
    
    # 4. Sinon → succès
    return {
        "success": True,
        "message": f"✅ Moins de {int(threshold * 100)}% de valeurs manquantes par colonne"
    }


def check_no_duplicates(df):
    """Vérifie qu'il n'y a pas de lignes dupliquées"""
    
    # 1. Compter les lignes dupliquées
    # duplicated() retourne True pour chaque ligne qui est un doublon
    # .sum() compte le nombre de True
    duplicate_count = df.duplicated().sum()
    
    # 2. Si on trouve des doublons → échec
    if duplicate_count > 0:
        return {
            "success": False,
            "message": f"❌ {duplicate_count} lignes dupliquées trouvées"
        }
    
    # 3. Sinon → succès
    return {
        "success": True,
        "message": "✅ Aucun doublon trouvé"
    }


def validate(df):
    """Fonction principale qui exécute toutes les vérifications"""
    
    # 1. Liste de toutes les vérifications à effectuer
    checks = [
        check_no_empty_country(df),
        check_positive_population(df),
        check_percentage_range(df),
        check_missing_values(df),
        check_no_duplicates(df)
    ]
    
    # 2. Afficher le résultat de chaque vérification
    print("\n📋 Rapport de qualité des données :")
    print("-" * 50)
    for check in checks:
        print(check["message"])
    
    # 3. Vérifier si toutes les règles sont respectées
    # all() retourne True seulement si TOUS les éléments sont True
    all_passed = all(check["success"] for check in checks)
    
    # 4. Afficher le verdict final
    print("-" * 50)
    if all_passed:
        print("✅ Dataset accepté — qualité suffisante")
    else:
        print("❌ Dataset rejeté — qualité insuffisante")
    
    # 5. Retourner True si accepté, False si rejeté
    return all_passed