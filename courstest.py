lst = [5, 2, 8, 1]
# TODO: Trie la liste manuellement (tri par sélection ou autre)
liste_triee=[]
for i in range(len(lst)):
  for j in range(i+1,len(lst)):
    print(f"lst[i] :{lst[i]} lst[j] : {lst[j]}")
    if lst[i] > lst[j]:
      lst[i], lst[j]=lst[j],lst[i]
      print(f"en cours: {lst}")
print(lst)