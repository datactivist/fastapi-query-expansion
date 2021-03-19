# FastAPI Query Expansion

## Déploiement sans docker

Requirements: 
- python >= 3.X

### Installation dépendances

```
pip install fastapi uvicorn
pip install git+https://github.com/moreymat/magnitude.git@0.1.143.1#egg=pymagnitude
```

Dans le fichier `fastapi-query-expansion/api-config.py`, changer la valeur de `deployment_method` en `local` et créez la configuration que vous souhaitez.

Depuis le répertoire `fastapi-query-expansion/`

```
bash ./start_service.sh
```

## Créer une image docker

Requirements:
- Python >= 3.X
- Docker >= 20.X

Dans le fichier `fastapi-query-expansion/api-config.py`, changer la valeur de `deployment_method` en `docker` et créez la configuration que vous souhaitez.

Depuis le répertoire `fastapi-query-expansion/`

```
bash ./start_service.sh
```


## Preprocessing et preloading

Il y a cinq étapes avant de lancer le service:

- Prise en comptes du fichier config
- Téléchargement des embeddings manquant
- Conversion de ces derniers    (non sauvegardé localement via docker)
- Préchargement avec la méthode most_similar 
- Préchargement des mots-clés de datasud 

## API Documentation

Une fois le service lancé (localement), une documentation intéractible est disponible à cette adresse: http://127.0.0.1/docs#/
