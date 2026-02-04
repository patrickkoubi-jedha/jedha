def tri_insertion_recursive(lst):
    # Cas de base : liste vide ou 1 élément → déjà triée
    if len(lst) <= 1:
        return lst
    
    # On prend le dernier élément et on trie le reste
    dernier = lst.pop()           # on enlève le dernier
    print(f"dernier élément extrait: {dernier}, reste de la liste: {lst}")
    liste_triee = tri_insertion_recursive(lst)  # récursion
    
    # On regarde si on peut INSERER directement le dernier élément (lst.pop) ailleurs qu'a sa place initiale
    #en parcourant et comparant avec les éléments de la liste
    for i in range(len(liste_triee)):
        print(f"comparaison de {dernier} avec {liste_triee[i]}")
        if liste_triee[i] > dernier:
            liste_triee.insert(i, dernier)
            print(f"insertion de {dernier} à l'index {i}: {liste_triee}")
            return liste_triee
    
    # Sinon on le remet à la fin
    liste_triee.append(dernier)
    print(f"ajout de {dernier} à la fin: {liste_triee}")
    return liste_triee


# Exemple d'utilisation
nombres = [7, 3, 42, 1, 9, 4, 8]
print(tri_insertion_recursive(nombres))