import pandas as pd
import numpy as np

class DataAuditor:
    """
    Classe dédiée à l'audit / diagnostic qualité d'un DataFrame pandas.

    Objectif :
    ----------
    Identifier rapidement les problèmes courants de qualité des données sans modifier
    le DataFrame original (lecture seule).

    Principaux contrôles effectués :
    - forme du dataset et répartition des types de colonnes
    - valeurs manquantes (nombre, pourcentage, colonnes les plus touchées)
    - lignes dupliquées (exactes)
    - colonnes constantes ou quasi-constantes
    - détection d'outliers (méthode IQR et Z-score simple)
    - colonnes à très haute cardinalité (souvent des identifiants)
    - problèmes fréquents dans les colonnes texte (vides, trop longues, etc.)

    Exemples d'utilisation (commentaires) :
    --------------------------------------
    # 1. Audit basique
    auditor = DataAuditor(df)
    auditor.print_report()

    # 2. Utilisation avec un DataFrame pandas existant
    import pandas as pd
    df = pd.read_csv("mon_fichier.csv")
    audit = DataAuditor(df)
    audit.print_report()

    # 3. Vérifier uniquement les valeurs manquantes (accès direct au rapport)
    print(audit.report['missing_values'])

    # 4. Chaîner avec un nettoyage si besoin
    if audit.report['missing_values']['pct_total'] > 10:
        print("Attention : plus de 10% de valeurs manquantes → nettoyage recommandé")
    """

    def __init__(self, df: pd.DataFrame):
        """
        Initialise l'auditeur avec une copie du DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            Le DataFrame à auditer (une copie est créée)

        Exemple :
        --------
        df = pd.DataFrame({'A': [1, 2, np.nan], 'B': ['x', 'x', 'y']})
        auditor = DataAuditor(df)
        """
        self.df = df.copy()
        self.report = {}
        self._run_audit()

    def _run_audit(self) -> None:
        """Exécute séquentiellement tous les contrôles d'audit."""
        self._check_shape_and_dtypes()
        self._check_missing_values()
        self._check_duplicates()
        self._check_constants_and_low_variance()
        self._check_outliers()
        self._check_high_cardinality()
        self._check_string_issues()

    def _check_shape_and_dtypes(self) -> None:
        """Enregistre la forme et les types de colonnes."""
        self.report['shape'] = self.df.shape
        self.report['dtypes_count'] = self.df.dtypes.value_counts().to_dict()
        self.report['columns_by_type'] = {
            'numeric': self.df.select_dtypes(include='number').columns.tolist(),
            'text': self.df.select_dtypes(include=['object', 'string', 'category']).columns.tolist(),
            'datetime': self.df.select_dtypes(include='datetime').columns.tolist(),
            'bool': self.df.select_dtypes(include='bool').columns.tolist()
        }

    def _check_missing_values(self) -> None:
        """Statistiques sur les valeurs manquantes."""
        missing = self.df.isna().sum()
        missing = missing[missing > 0].sort_values(ascending=False)

        self.report['missing_values'] = {
            'total': self.df.isna().sum().sum(),
            'pct_total': (self.df.isna().sum().sum() / len(self.df)) * 100 if len(self.df) > 0 else 0,
            'by_column': missing.to_dict(),
            'worst_column': missing.index[0] if not missing.empty else None,
            'worst_count': missing.iloc[0] if not missing.empty else 0
        }

    def _check_duplicates(self) -> None:
        """Compte les doublons exacts."""
        dup = self.df.duplicated().sum()
        self.report['duplicates'] = {
            'count': dup,
            'pct': (dup / len(self.df)) * 100 if len(self.df) > 0 else 0
        }

    def _check_constants_and_low_variance(self) -> None:
        """Détecte colonnes constantes ou quasi-constantes."""
        const = [col for col in self.df.columns if self.df[col].nunique() <= 1]
        low_var = [
            (col, self.df[col].nunique())
            for col in self.df.columns
            if 1 < self.df[col].nunique() <= 5 and len(self.df) > 20
        ]

        self.report['constants'] = const
        self.report['low_variance'] = low_var

    def _check_outliers(self) -> None:
        """Détection d'outliers (IQR et Z-score)."""
        outliers_info = {}
        numeric_cols = self.df.select_dtypes('number').columns

        for col in numeric_cols:
            if self.df[col].nunique() < 5:
                continue

            q1, q3 = self.df[col].quantile([0.25, 0.75])
            iqr = q3 - q1
            outliers_iqr = ((self.df[col] < q1 - 1.5 * iqr) | (self.df[col] > q3 + 1.5 * iqr)).sum()

            z = np.abs((self.df[col] - self.df[col].mean()) / self.df[col].std(ddof=0))
            outliers_z = (z > 3).sum()

            outliers_info[col] = {
                'iqr_count': outliers_iqr,
                'z3_count': outliers_z,
                'min_val': self.df[col].min(),
                'max_val': self.df[col].max()
            }

        self.report['outliers'] = outliers_info

    def _check_high_cardinality(self) -> None:
        """Colonnes à très haute cardinalité (souvent IDs)."""
        high_card = {}
        for col in self.df.select_dtypes(['object', 'category', 'string']).columns:
            ratio = self.df[col].nunique() / len(self.df)
            if ratio > 0.25:
                high_card[col] = {
                    'unique_count': self.df[col].nunique(),
                    'ratio': round(ratio, 3)
                }
        self.report['high_cardinality'] = high_card

    def _check_string_issues(self) -> None:
        """Anomalies fréquentes dans les colonnes texte."""
        issues = {}
        for col in self.df.select_dtypes(['object', 'string']).columns:
            s = self.df[col].astype(str).str
            problems = {
                'empty_or_whitespace': (s.strip() == '').sum(),
                'very_long_200': (s.len() > 200).sum(),
                'very_short_nonempty': ((s.len() > 0) & (s.len() <= 2)).sum()
            }
            if any(problems.values()):
                issues[col] = problems
        self.report['string_problems'] = issues

    def print_report(self) -> None:
        """
        Affiche un rapport textuel clair et structuré.

        Exemple d'appel :
        ----------------
        audit = DataAuditor(df)
        audit.print_report()
        """
        r = self.report

        print("\n" + "═" * 80)
        print(" AUDIT QUALITÉ DATASET ".center(80))
        print("═" * 80)

        print(f"\nForme : {r['shape']} lignes × colonnes")
        print("Types principaux :")
        for t, cols in r['columns_by_type'].items():
            if cols:
                print(f"  • {t:<12} {len(cols):3d} colonnes")

        if r['missing_values']['total'] > 0:
            print("\nValeurs manquantes :")
            print(f"  Total : {r['missing_values']['total']} ({r['missing_values']['pct_total']:.1f} %)")
            if r['missing_values']['worst_column']:
                print(f"  Pire colonne : {r['missing_values']['worst_column']} "
                      f"({r['missing_values']['worst_count']} NaN)")

        print("\nDoublons & constantes :")
        print(f"  Doublons exacts : {r['duplicates']['count']} ({r['duplicates']['pct']:.1f} %)")
        if r['constants']:
            print(f"  Colonnes constantes : {', '.join(r['constants'])}")
        if r['low_variance']:
            print("  Quasi-constantes : " + ", ".join([c for c, _ in r['low_variance']]))

        if r['outliers']:
            print("\nOutliers détectés (IQR 1.5× & Z>3) :")
            for col, info in r['outliers'].items():
                if info['iqr_count'] > 0 or info['z3_count'] > 0:
                    print(f"  • {col:<18} IQR: {info['iqr_count']:3d} | Z>3: {info['z3_count']:3d} "
                          f"| extrêmes: {info['min_val']:.2f} → {info['max_val']:.2f}")

        if r['high_cardinality']:
            print("\nHaute cardinalité (souvent IDs) :")
            for col, info in r['high_cardinality'].items():
                print(f"  • {col:<20} {info['unique_count']} uniques ({info['ratio']*100:.1f} %)")

        if r['string_problems']:
            print("\nProblèmes texte :")
            for col, iss in r['string_problems'].items():
                print(f"  • {col:<20} vides: {iss['empty_or_whitespace']:3d} | "
                      f"très longs (>200): {iss['very_long_200']:3d}")

        print("\n" + "═" * 80)


# =============================================================================
# EXEMPLES D'UTILISATION (à copier-coller dans votre code ou notebook)
# =============================================================================

"""
# Exemple 1 : Audit rapide sur un petit DataFrame
import pandas as pd
import numpy as np

df = pd.DataFrame({
    'id': [101, 102, 101, 104],
    'nom': ['alice ', 'Bob', ' alice', None],
    'age': [25, 999, 25, 30],
    'salaire': [2800, 3200, 2800, np.nan],
    'ville': ['Paris', 'paris ', 'Paris', 'Lyon']
})

audit = DataAuditor(df)
audit.print_report()


# Exemple 2 : Vérification ciblée après chargement d'un fichier
df = pd.read_csv("ventes_2025.csv")
audit = DataAuditor(df)

# Regarder seulement les valeurs manquantes
print("Valeurs manquantes :")
print(audit.report['missing_values'])

# Vérifier s'il y a des doublons importants
if audit.report['duplicates']['pct'] > 5:
    print("Attention : plus de 5% de doublons détectés !")


# Exemple 3 : Intégration dans un pipeline
def quality_check(df):
    audit = DataAuditor(df)
    audit.print_report()
    return audit.report['missing_values']['pct_total'] < 5 and \
           audit.report['duplicates']['pct'] < 2

if quality_check(df):
    print("Les données semblent prêtes pour l'analyse")
else:
    print("Problèmes détectés → nettoyage nécessaire")
"""

from charset_normalizer import from_path

results = from_path("perso/speed_dating_project/Speed+Dating+Data.csv").best()

if results:
    enc = results.encoding
    # Deux façons d'accéder à la confiance (compatible ancien / nouveau)
    confiance = getattr(results, 'confidence', getattr(results, 'percentage', 0.0))
    print(f"Encodage détecté : {enc}")
    print(f"Confiance : {confiance:.1%}")

    df = pd.read_csv("perso/speed_dating_project/Speed+Dating+Data.csv", encoding=enc)
else:
    print("Détection échouée → essai manuel")
    df = pd.read_csv("perso/speed_dating_project/Speed+Dating+Data.csv", encoding="cp1252")
audit = DataAuditor(df)
print("Valeurs manquantes :")
audit.print_report()