#password valide
sec_pwd="123toto"
#flag pwd valide
pwd_valid=False

#boucle tant que pwd non valide
while not pwd_valid:
    pwd = input("Entrez un password: ")
    pwd_valid=False
    #comparaison de la saisie avec le pwd secret et mise a jour du flag
    pwd_valid=pwd==sec_pwd
    #affichage du resultat
    if not pwd_valid:
        print("Password non valide, réessayez.") 
    else:
        print("Password valide!")
    