# %%
# =============================================================================
# DataCleaner – Classe utilitaire pour nettoyer des DataFrames pandas
# =============================================================================
#
# POURQUOI NETTOYER LES DONNÉES ?
# ------------------------------
# - Doublons → fausse impression de volume
# - Valeurs manquantes → algorithmes qui plantent ou biais
# - Outliers → moyenne / régression déformées
# - Texte incohérent ("Paris ", "paris", " PAris  ") → group by raté
# - Mauvais types → calculs impossibles
#
# Exemple concret :
#   Avant : moyenne salaire = 4500€ (mais 3 lignes à 999999€ faussent tout)
#   Après nettoyage : moyenne salaire = 2850€ → décision métier réaliste
#
# =============================================================================

import pandas as pd
import numpy as np
from datetime import datetime

# %%
class DataCleaner:
    """
    Classe utilitaire pour nettoyer un DataFrame pandas de façon structurée.
    - Log des opérations effectuées
    - Méthodes chaînables
    - Nettoyage spécifique texte + valeurs manquantes + outliers + types
    """

    def __init__(self, df: pd.DataFrame):
        """ Initialise avec une copie du DataFrame """
        self.df = df.copy()
        self.log = []               # Historique des actions

    def _log_action(self, message: str):
        """ Enregistre une action avec horodatage """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.log.append(entry)
        # print(entry)              # décommente pour voir en direct

    def get_log(self):
        """ Retourne tout le journal des opérations """
        if not self.log:
            return "Aucune opération effectuée."
        return "\n".join(self.log)

# %%
    def drop_duplicates(self, keep='first'):
        """ Supprime les lignes identiques """
        before = len(self.df)
        self.df = self.df.drop_duplicates(keep=keep)
        removed = before - len(self.df)
        self._log_action(f"Suppression doublons → {removed} lignes enlevées (keep={keep})")
        return self

# %%
    def handle_missing(self, strategy='drop', columns=None, fill_value=None):
        """
        Stratégies : 'drop', 'mean', 'median', 'mode', 'zero', 'custom'
        
        - 'mean'   → moyenne arithmétique
        - 'median' → valeur centrale après tri (robuste aux outliers)
        """
        target_cols = columns if columns else self.df.columns
        before_na = self.df.isna().sum().sum()

        if strategy == 'drop':
            self.df = self.df.dropna(subset=target_cols)
            self._log_action(f"Drop NaN → ~{before_na} valeurs traitées")

        elif strategy in ['mean', 'median', 'mode']:
            for col in target_cols:
                if pd.api.types.is_numeric_dtype(self.df[col]):
                    if strategy == 'mean':
                        val = self.df[col].mean()
                    elif strategy == 'median':
                        val = self.df[col].median()
                    else:
                        val = self.df[col].mode()[0] if not self.df[col].mode().empty else np.nan
                    self.df[col] = self.df[col].fillna(val)
                    self._log_action(f"{col} → {strategy} = {val}")

        elif strategy == 'zero':
            self.df[target_cols] = self.df[target_cols].fillna(0)
            self._log_action(f"Imputation 0 sur {target_cols}")

        elif strategy == 'custom' and fill_value is not None:
            self.df[target_cols] = self.df[target_cols].fillna(fill_value)
            self._log_action(f"Imputation '{fill_value}' sur {target_cols}")

        return self

# %%
    def clean_strings(self, columns=None, lowercase=True, strip=True, remove_extra_spaces=True, replace_na=''):
        """ Normalise le texte (minuscules, strip, espaces multiples → un seul) """
        target_cols = columns if columns else self.df.select_dtypes(include=['object', 'string']).columns

        for col in target_cols:
            if replace_na is not None:
                self.df[col] = self.df[col].fillna(replace_na)

            if pd.api.types.is_object_dtype(self.df[col]) or pd.api.types.is_string_dtype(self.df[col]):
                s = self.df[col].str
                if lowercase:       s = s.lower()
                if strip:           s = s.strip()
                if remove_extra_spaces:
                    s = s.replace(r'\s+', ' ', regex=True)
                self.df[col] = s

            self._log_action(f"Nettoyage texte '{col}' (lower={lowercase}, strip={strip}, extra_sp={remove_extra_spaces})")

        return self

# %%
    def remove_accents(self, columns=None):
        """ Transforme é → e, ç → c, etc. """
        import unicodedata

        target_cols = columns if columns else self.df.select_dtypes(include=['object', 'string']).columns

        def strip_accents(s):
            if pd.isna(s): return s
            return ''.join(c for c in unicodedata.normalize('NFD', str(s))
                           if unicodedata.category(c) != 'Mn')

        for col in target_cols:
            self.df[col] = self.df[col].apply(strip_accents)
            self._log_action(f"Accents supprimés sur '{col}'")

        return self

# %%
    def replace_in_strings(self, columns=None, to_replace: dict = None):
        """ Remplacements texte personnalisés """
        if not to_replace:
            return self

        target_cols = columns if columns else self.df.select_dtypes(include=['object', 'string']).columns

        for col in target_cols:
            for old, new in to_replace.items():
                self.df[col] = self.df[col].str.replace(old, new, regex=False)
            self._log_action(f"Remplacements sur '{col}' → {to_replace}")

        return self

# %%
    def remove_outliers_iqr(self, columns=None, multiplier=1.5):
        """
        Supprime outliers avec méthode IQR :
          borne basse = Q1 - multiplier × IQR
          borne haute = Q3 + multiplier × IQR
        """
        target_cols = columns if columns else self.df.select_dtypes(include=['number']).columns

        for col in target_cols:
            Q1 = self.df[col].quantile(0.25)
            Q3 = self.df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - multiplier * IQR
            upper = Q3 + multiplier * IQR

            before = len(self.df)
            self.df = self.df[(self.df[col] >= lower) & (self.df[col] <= upper)]
            removed = before - len(self.df)
            if removed > 0:
                self._log_action(f"{col} → {removed} outliers supprimés (IQR × {multiplier})")

        return self

# %%
    def convert_types(self, type_dict: dict):
        """ Convertit les types de colonnes """
        for col, dtype in type_dict.items():
            if col in self.df.columns:
                try:
                    if dtype == 'category':
                        self.df[col] = self.df[col].astype('category')
                    else:
                        self.df[col] = pd.to_numeric(self.df[col], errors='coerce').astype(dtype)
                    self._log_action(f"{col} → type converti en {dtype}")
                except Exception as e:
                    self._log_action(f"Erreur conversion {col} → {e}")
        return self

# %%
    def get_cleaned_df(self) -> pd.DataFrame:
        return self.df

    def summary(self):
        """ Affiche un rapport final """
        print("\n" + "="*50)
        print("RAPPORT FINAL DE NETTOYAGE")
        print("="*50)
        print(f"Dimensions        : {self.df.shape}")
        print(f"NaN restants      : {self.df.isna().sum().sum()}")
        print(f"Doublons restants : {self.df.duplicated().sum()}")
        print("\nHistorique des opérations :")
        print(self.get_log())
        print("="*50)
        return self

# %%
# ──── EXEMPLE D'UTILISATION ────────────────────────────────────────────────

data = {
    'Nom': ['  Alice  ', 'Bob   ', '  ÇA VA ?', None, 'ÉMILIE'],
    'Ville': ['Paris  ', ' paris', 'LYON   ', 'Marseille', None],
    'Age': [25, 30, None, 28, 999],
    'Salaire': [2500.5, 3000, None, 2800, 12000]
}
df = pd.DataFrame(data)

# %%
cleaner = DataCleaner(df)

# %%
cleaned = (
    cleaner
    .drop_duplicates()
    .handle_missing(strategy='median', columns=['Age', 'Salaire'])
    .clean_strings(lowercase=True, strip=True, remove_extra_spaces=True, replace_na='')
    .remove_accents()
    .replace_in_strings(to_replace={'ça va ?': 'comment vas-tu ?', 'lyon': 'Lyon'})
    .remove_outliers_iqr(columns=['Salaire'], multiplier=2.0)
    .convert_types({'Age': 'int', 'Salaire': 'float'})
    .summary()
    .get_cleaned_df()
)

# %%
cleaned