import pandas as pd
import re

def remove_useless_columns(df, colonnes=[]):
    # Supprimer les colonnes inutiles
    df = df.drop(columns=colonnes, errors="ignore")
    return df

def remove_references(df):
    # Supprimer [1], [b], [3]...
    df = df.replace(r'\[.*?\]', '', regex=True)
    return df

def clean_population(df):
    if "Population" in df.columns:
        # 1. Enlever les virgules "8,232,000,000" → "8232000000"
        df["Population"] = df["Population"].str.replace(",", "")
    
        # 2. Convertir en nombre entier
        df["Population"] = pd.to_numeric(df["Population"], errors="coerce")
    return df

def clean_percentage(df):
    # Convertir "17.2%" en 17.2
    percent_cols = [col for col in df.columns if "%" in col]
    
    for col in percent_cols:
        # 1. Enlever le symbole "%"
        df[col] = df[col].str.replace("%", "")
        
        # 2. Convertir en nombre décimal
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def remove_empty_rows(df):
    # Supprimer les lignes vides
    df = df.dropna(how="all")
    
    # Supprimer les lignes où la colonne principale est vide
    df = df.dropna(subset=[df.columns[0]])
    
    # Réinitialiser l'index après suppression
    df = df.reset_index(drop=True)
    return df

def clean(df, colonnes_inutiles=[]):
    # Fonction principale qui appelle toutes les autres
    df = remove_useless_columns(df, colonnes=colonnes_inutiles)
    df = remove_references(df)
    df = clean_population(df)
    df = clean_percentage(df)
    df = remove_empty_rows(df)
    return df