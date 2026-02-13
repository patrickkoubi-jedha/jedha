import requests
import pandas as pd
from typing import Dict, Any, Optional, List
import json

class MyGeckoApi:
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.root_url = "https://api.coingecko.com/api/v3/"

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Any:
        """
        Méthode interne réutilisable pour factoriser les requêtes
        """
        url = self.root_url + endpoint
        
        # On prépare les paramètres
        payload = params.copy() if params else {}
        
        # On ajoute la clé API si elle existe et qu'elle n'est pas déjà présente
        if self.api_key and "x_cg_demo_api_key" not in payload:
            payload["x_cg_demo_api_key"] = self.api_key

        try:
            response = requests.get(url, params=payload, timeout=15)
            response.raise_for_status()  # Lève une exception pour les codes 4xx/5xx
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Erreur CoinGecko API ({response.status_code}): {response.text or str(e)}")

    # ────────────────────────────────────────────────
    # Méthodes existantes / déjà écrites
    # ────────────────────────────────────────────────
    def get_crypto_currencies_list(self, payload: Dict = None) -> List[Dict]:
        """
        Récupère la liste des cryptomonnaies avec leurs données de marché.

        Payload (paramètres de requête) les plus courants :
        ----------------------------------------------------------------
        vs_currency         str     'usd', 'eur', 'btc', 'eth'...     Obligatoire
        ids                 str     'bitcoin,ethereum,solana'         IDs spécifiques (séparés par virgule)
        category            str     'layer-1', 'defi', 'stablecoin'...
        order               str     'market_cap_desc', 'volume_desc', 'price_desc'...
        per_page            int     100, 250, 500 (max 250 sur plan gratuit)
        page                int     1, 2, 3... (pagination)
        sparkline           bool    True/False (petit graphique 7 jours)
        price_change_percentage str  '1h,24h,7d,14d,30d,200d,1y'     (séparés par virgule)
        ----------------------------------------------------------------

        Exemple simple :
        payload = {'vs_currency': 'usd', 'order': 'market_cap_desc', 'per_page': 100, 'page': 1}

        Exemple avec filtres :
        payload = {
            'vs_currency': 'eur',
            'ids': 'bitcoin,ethereum,binancecoin',
            'price_change_percentage': '1h,24h,7d'
        }

        Retourne : liste de dictionnaires (chaque dict = une crypto)
        """
        if payload is None:
            payload = {}
        return self._make_request("coins/markets", payload)

    # ────────────────────────────────────────────────
    # Fourni les données OHLC pour une ou plusieurs cryptos, en fonction des paramètres fournis
    #  sous forme d'un dictionnaire de listes, avec les données au format origine
    #  ────────────────────────────────────────────────
    def get_ohlc_data(self, payload: List = None) -> List[Dict]:
        """Récupère les données OHLC pour une crypto donnée"""
        if payload is None:
            payload = {}
        if len(payload.get("coin_id")) == 0:
            raise ValueError("coin_id must be provided for OHLC data retrieval.")
        else:
            ohlc_dict = {}
            coins_ids=payload.get("coin_id")
            for coin_id in coins_ids:
                ohlc_dict[coin_id]=(self._make_request(f"coins/{coin_id}/ohlc", payload))
        if ohlc_dict == {}:
            raise ValueError("No OHLC data retrieved for the provided coin_id(s).")
        return ohlc_dict
    # ────────────────────────────────────────────────
    # Fourni les données OHLC pour une ou plusieurs cryptos, en fonction des paramètres fournis
    #  sous forme d'un dictionnaire de dictionnaires, avec les dates en format 
    # YYYY-MM-DD et les valeurs OHLC associées
    # ────────────────────────────────────────────────
    def get_ohlc_data_date(self, payload: List = None) -> List[Dict]:
        """Récupère les données OHLC pour une crypto donnée"""
        if payload is None:
            payload = {}
        if len(payload.get("coin_id")) == 0:
            raise ValueError("coin_id must be provided for OHLC data retrieval.")
        else:
            coins_ids=payload.get("coin_id")
            ohlc_dict = {}
            for coin_id in coins_ids:
                ohlc_dict[coin_id] = {}
                ohlc_curr=(self._make_request(f"coins/{coin_id}/ohlc", payload))
                for ts,open_, high, low, close in ohlc_curr:
                    ts=pd.to_datetime(ts, unit='ms').strftime('%Y-%m-%d')
                    ohlc_dict[coin_id][str(ts)] = [open_, high, low, close]
                
        if ohlc_dict == {}:
            raise ValueError("No OHLC data retrieved for the provided coin_id(s).")
        return ohlc_dict
        
        
"""        
 EXEMPLES D4UTILISATION DE LA CLASSE MyGeckoApi
"""
""" 
#fonction pour obtenir la liste de toutes les cryptos disponibles sur CoinGecko
my_gecko_api = MyGeckoApi(api_key=my_api_key)
params1={
    "per_page": 250,
    "order": "market_cap_desc",
    "vs_currency": "usd"
}
crypto_currencies_list=my_gecko_api.get_crypto_currencies_list(params1)
#affiche les id des 10 premières cryptos de la liste
coin_ids=(list(map(lambda x: x['id'], crypto_currencies_list[:10])))
print(coin_ids)


params2={
    "coin_id": coin_ids,
    "days": 365,
    "vs_currency": "usd"
}
ohlc_dict=my_gecko_api.get_ohlc_data_date(params2)
ohlc_dict
 """