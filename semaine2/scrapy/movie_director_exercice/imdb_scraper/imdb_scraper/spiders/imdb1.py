import scrapy
# import requests              # <-- supprimé : on n'utilise plus requests dans un spider Scrapy
# import logging
# import os
# from scrapy.crawler import CrawlerProcess          # <-- pas besoin ici (lancé via commande scrapy crawl)
# from parsel import Selector                        # <-- pas besoin (response est déjà un Selector)

# On suppose que parse_vote_count est dans utils/parsing.py
#pour externaliser le code de parsing et le rendre réutilisable dans d'autres spiders du projet
# créer un repertoire (ex utils/) et un fichier "parsing.py" pour y mettre le code "def votre_fonction(): ..."
#      l'importer avec 
#                   from imdb_scraper.utils.parsing import votre_fonction

# Version locale de parse_vote_count (recommandée pour commencer)
def parse_vote_count(vote_parts):
    """
    Extrait le nombre de votes à partir des parties extraites.
    Exemple : [' (', '3,2\xa0M', ')'] → 3200000
    """
    if len(vote_parts) < 3:
        return 0
    
    raw = vote_parts[1].replace('\xa0', '').strip()  # '3,2M'
    
    multi = 1
    if 'M' in raw.upper():
        multi = 1_000_000
        raw = raw.rstrip('Mm')
    elif 'K' in raw.upper():
        multi = 1_000
        raw = raw.rstrip('Kk')
    
    raw = raw.replace(',', '.').strip()
    
    try:
        return int(float(raw) * multi)
    except (ValueError, TypeError):
        return 0


class ImdbSpider(scrapy.Spider):
    name = "imdb1"
    allowed_domains = ["imdb.com"]
    
    start_urls = ["https://www.imdb.com/chart/top/"]
    
    def parse(self, response):
        classement = 0     
        
        for film in response.css("li.ipc-metadata-list-summary-item"):
            classement += 1
            
            # ### On récupère le titre
            titre_raw = film.css("h3.ipc-title__text::text").get()
            titre = titre_raw.split('. ', 1)[-1].strip() if titre_raw else '?'  # ← nettoyé
            
            # ### On récupère l'URL
            # base_url="https://www.imdb.com"
            film_relative_url = film.css('a.ipc-title-link-wrapper::attr(href)').get('')
            if not film_relative_url:
                continue
            
            # url_details = response.urljoin(film_relative_url)   # ← on le fait dans Request
            
            # ### On récupère le rating
            # rating = film.css("span.ipc-rating-star--rating::text").get(), mais on prefere le data-testid plus robuste
            # pour info le.get(default='?') permet de retourner '?' si le sélecteur ne trouve rien, au lieu de retourner 'None'
            rating = film.css('span[data-testid="ratingGroup--imdb-rating"] ::text').get(default='?').strip()
            
            # ### On récupère le nombre de votants
            vote_parts = film.css("span.ipc-rating-star--voteCount::text").getall()
            nb_voteurs = parse_vote_count(vote_parts)
            
            # ### On a tout scrappé sur la 1ere page, on avance vers le lien detail du film
            # pour scraper le revenu brut mondial
            # detail_resp = requests.get(url_details, headers=headers, timeout=10)
            # detail_sel = Selector(text=detail_resp.text)    
            # revenu_brut_mondial = detail_sel.css( ... ).get(default='?').strip()
            # → Remplacé par :
           
            yield scrapy.Request(
                url=response.urljoin(film_relative_url),
                callback=self.parse_detail,
                meta={
                    'classement': classement,
                    'titre': titre,
                    'rating': rating,
                    'nb_voteurs': nb_voteurs,
                }
            )
            
            """ ce YIELD ci-dessus signifie : Quand tu auras téléchargé et parsé cette nouvelle page (la page détail du film),
            appelle automatiquement la méthode parse_detail et passe-lui la réponse. 
            
            Pour suivre les liens je pourrais aussi faire un 'response.follow' :
            yield response.follow(
                url=film_relative_url,              # relatif ou absolu
                callback=self.parse_detail,
                meta={...}
            )
            """


    # ici on estparti de la 1ere page et on est dans
    # la page détail du film, on peut scraper le revenu brut mondial
    def parse_detail(self, response):
        classement   = response.meta['classement']
        titre        = response.meta['titre']
        rating       = response.meta['rating']
        nb_voteurs   = response.meta['nb_voteurs']

        # Revenu brut mondial – plusieurs variantes pour plus de robustesse
        """
            Explication du sélecteur multiple pour revenu_brut_mondial :
            On utilise une union de plusieurs sélecteurs (séparés par des virgules)
            pour augmenter la robustesse face aux changements de structure ou de langue sur IMDb.

            Partie du sélecteur                                      | Ce qu'elle cible                                              | Quand elle est utile
            ----------------------------------------------------------|---------------------------------------------------------------|------------------------------------------------------
            li[data-testid="title-boxoffice-cumulativeworldwidegross"]| L'élément avec l'attribut data-testid spécifique              | Version la plus fiable quand IMDb utilise cet attribut
            span.ipc-metadata-list-item__list-content-item::text      | Toute span de valeur dans la liste des métadonnées            | Cas où le data-testid est absent ou changé, mais la classe de contenu reste
            li:contains("Gross worldwide")::text                      | N'importe quel <li> contenant exactement ce texte anglais     | Quand le site est en anglais et pas de data-testid
            li:contains("Montant brut mondial")::text                 | N'importe quel <li> contenant ce texte français               | Quand la page est en français
            li:contains("Cumulative Worldwide Gross")::text           | Variante anglaise plus longue (parfois utilisée)              | Anciennes versions ou variantes de la page

            Plus on ajoute de variantes, moins on risque de tout perdre si IMDb change une formulation.
        """
        revenu_brut_mondial = response.css(
            'li[data-testid="title-boxoffice-cumulativeworldwidegross"] '
            'span.ipc-metadata-list-item__list-content-item::text, '
            'li:contains("Gross worldwide")::text, '
            'li:contains("Montant brut mondial")::text, '
            'li:contains("Cumulative Worldwide Gross")::text'
        ).get(default='?').strip()

        # Nettoyage léger
        if revenu_brut_mondial != '?':
            revenu_brut_mondial = revenu_brut_mondial.replace('\xa0', ' ').strip()

        yield {
            'classement': classement,
            'title': titre,
            'url_details': response.url,
            'revenu_brut_mondial': revenu_brut_mondial,
            'rating': rating,
            'nb_voters': nb_voteurs
        }