#utils

def rapport_data_complet(df, colonnes=None, total_lignes=None):
    """
    Rapport complet des valeurs manquantes + suspectes
    Utilise un DataFrame pandas pour un affichage plus propre
    """
    if total_lignes is None:
        total_lignes = len(df)

    if colonnes is None:
        colonnes = df.columns.tolist()

    data = []
    for col in colonnes:
        if col not in df.columns:
            continue

        na_count = df[col].isna().sum()

        # Chaînes problématiques (seulement sur colonnes texte)
        vide = none_str = na_variants = 0
        if df[col].dtype in ['object', 'string']:
            str_col = df[col].astype(str).str.strip().str.lower()
            vide       = (str_col == '').sum()
            none_str   = (str_col == 'none').sum()
            na_variants = str_col.isin(['na', 'n/a', 'null']).sum()

        total_suspect = na_count + vide + none_str + na_variants
        pct = round((total_suspect / total_lignes) * 100, 1) if total_lignes > 0 else 0.0

        # Commentaire court relatif au pct de manques/erronés
        if total_suspect == 0:
            commentaire = "parfait"
        elif pct <= 3:
            commentaire = "excellent"
        elif pct <= 6:
            commentaire = "très bon"
        elif pct <= 10:
            commentaire = "bon"
        elif pct <= 15:
            commentaire = "moyen – prudence"
        else:
            commentaire = "problématique"

        data.append({
            'Colonne': col,
            'NaN': na_count,
            'Vide': vide,
            'None': none_str,
            'na/n/a/null': na_variants,
            'Total suspect': total_suspect,
            '%': pct,
            'Commentaire': commentaire
        })

    # Création du DataFrame
    rapport_df = pd.DataFrame(data)

    # Tri : parfait d'abord, puis par % croissant
    rapport_df = rapport_df.sort_values(by=['Total suspect', '%'])

    # ────────────────────────────────────────────────
    # Affichage
    # ────────────────────────────────────────────────
    print(f"\n=== Rapport complet – {total_lignes:,} lignes ===\n")

    # 1. Colonnes parfaites
    parfaites = rapport_df[rapport_df['Total suspect'] == 0]['Colonne'].tolist()
    if parfaites:
        print("1. Colonnes sans aucun problème (0 suspect)")
        print("On peut les utiliser sans filtre :")
        print(", ".join(parfaites))
        print()

    # Tableau principal avec Styler (optionnel : couleurs)
    print("2. Rapport détaillé (toutes colonnes analysées)")

    print(rapport_df.to_markdown(index=False, tablefmt="pipe", floatfmt=".1f"))   # ← très important : affiche le tableau stylé dans Jupyter/Colab

    # Note + recommandations génériques
    print("\nNote : les colonnes numériques convertissent souvent '' ou 'None' en NaN lors du chargement.")
    print("Pour les colonnes texte, les chaînes vides et 'na'/'None' sont plus fréquentes.\n")
#guidelines relatives aux manques et leur impact
    print("""
            Recommandations pratiques génériques (indépendant des colonnes analysées) :
            • Colonnes avec 0 % ou < 3 % de manquants
                → Utilisation sans restriction (moyennes, corrélations, regroupements, visualisations)
            • Colonnes avec 3 % à 6–7 % de manquants
                → Très souvent acceptable pour des analyses descriptives
                → On peut calculer des moyennes, médianes, distributions sans filtre
                → Pour des corrélations ou modèles → filtrer les lignes incomplètes si possible
            • Colonnes avec 8 % à 15 % de manquants
                → Utilisation avec prudence
                → Préférer filtrer les lignes incomplètes (dropna) quand cette colonne est centrale
                → Attention au biais potentiel si les manquants ne sont pas aléatoires
            • Colonnes > 15 % de manquants
                → À manipuler très prudemment
                → Déconseillé pour des moyennes / corrélations globales sans filtre
                → À réserver à des analyses secondaires ou à des sous-populations complètes
                → Éviter de construire des scores / moyennes qui incluent fortement cette colonne

            Astuces opérationnelles :
            • Pour toute analyse impliquant plusieurs colonnes → utiliser dropna(subset=[...]) sur les variables clés
            • Perte < 5–6 % → généralement négligeable sur 8000+ lignes
            • Perte > 10–12 % → toujours vérifier le nombre de lignes restantes avant / après filtre
        """)

# ────────────────────────────────────────────────
# Exemple d'appel
# ────────────────────────────────────────────────
# Appel des colonnes identifiées au debut du projet
rapport_data_complet(df, colonnes=cols_debut)