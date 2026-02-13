import re

def parse_vote_count(film):
    # Exemple de texte réel que tu obtiens souvent
    texte = "".join(film.css("span.ipc-rating-star--voteCount::text").getall())
    # → typiquement : ' (3,2\xa0M)'   ou ' (1,45\xa0M)'   ou ' (456\xa0K)'   ou ' (12345)'

    # Regex qui capture le nombre ET le suffixe optionnel (M/K)
    match = re.search(r'([\d,.]+)\s*([KM])?', texte, re.IGNORECASE)

    if match:
        nombre_str = match.group(1)          # '3,2' ou '1,45' ou '456'
        suffixe    = match.group(2) or ''    # 'M' ou 'K' ou ''

        # Nettoyage
        nombre_str = nombre_str.replace(',', '.').strip()   # '3.2'

        # Multiplicateur
        multi = 1
        if suffixe.upper() == 'M':
            multi = 1_000_000
        elif suffixe.upper() == 'K':
            multi = 1_000

        try:
            votes = int(float(nombre_str) * multi)

        except ValueError:
            print("Conversion impossible")
    else:
        print("Aucun nombre trouvé")            # → 320000
    return votes