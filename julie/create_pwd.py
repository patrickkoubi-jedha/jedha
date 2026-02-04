sec_pwd="123toto"
pwd_valid=False

while not pwd_valid:
    pwd = input("Entrez un password: ")
    pwd_valid=False
    pwd_valid=pwd==sec_pwd
    if not pwd_valid:
        print("Password non valide, réessayez.") 
    else:
        print("Password valide!")
    