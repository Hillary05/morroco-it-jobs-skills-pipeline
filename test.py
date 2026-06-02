from scrapers.wikipedia import scrape
from pipeline.cleaner import clean
from pipeline.validator import validate
from pipeline.versioning import save_and_version

df = scrape("https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population")
colonnes_inutiles=["Source (official or fromthe United Nations)", "Notes"]

df_cleaned = clean(df, colonnes_inutiles)
print(df_cleaned.head(10))
print(df_cleaned.dtypes)

result_population = validate(df_cleaned)

if result_population:
    # ✅ Tu donnes toi-même le nom du sujet
    filepath, version = save_and_version(df_cleaned, subject="population")
    print(f"\n🎉 Dataset sauvegardé : {filepath}")
else:
    print("\n❌ Dataset rejeté — non sauvegardé")