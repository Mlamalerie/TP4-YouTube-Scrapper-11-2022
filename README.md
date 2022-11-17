# Youtube-Scraper

Scrape a list of YouYube videos and store the recovered data in a json file.

## To-do
- --input input.json --output output.json
- .venv in github
- test with pytest
- map/filter/reduce
- Découpage de vos fonctions les plus grandes (visez la trentaine de ligne maximum)
- beautify code and finish typing
- 

## How to run :

`python scrapping.py`

## How it works

> Les vidéos à scrapper sont dans le fichier .json : **input.json**
>
> ![](images/Screenshot%20from%202022-11-17%2003-12-24.png)
>
A l'aide de bs4 et Selenimum, pour chaque url :

1. Ouvrir la page
2. Scroller jusqu'en bas
3. Ouvrir tous les boutons "read more"
4. Convertir la page et l'envoyer à bs4
5. Récuperer :
   - id : identifiant de la video
   - url : l'url complet
   - title : le titre
   - author_name et author_url
   - views
   - published_date
   - description_text et description_links
   - nb_comments
   - comments

On scrappera notre liste en parallèle pour gagner du temps grace au multithreading


> Les résultats du scrapping seront dans le fichier .json : **output.json**
>
> ![](images/Screenshot%20from%202022-11-17%2003-13-37.png)


---
Mlamali SAID SALIMO. Nov 2022.


