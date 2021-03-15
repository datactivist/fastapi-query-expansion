# FastAPI Query Expansion

## Déploiement sans docker

### Installation dépendances
```
pip install fastapi, uvicorn
```

Depuis le répertoire `fastapi-query-expansion/`

```
python3 start_service.py
```

## Déploiement avec docker (créer une image docker)

Dans le fichier `fastapi-query-expansion/config.py`, changer la valeur de `deployment_method` en `docker`

Depuis le répertoire `fastapi-query-expansion/`

```
python3 start_service.py
```


## Preprocessing et preloading

Il y a quatre étapes avant de lancer le service:

- Téléchargement des embeddings manquant
- Conversion de ces derniers
- Préchargement avec la méthode most_similar
- Préchargement des mots-clés de datasud

## API Documentation

Once the docker is started (in local mode), the documentation of the API is available here: http://127.0.0.1/docs#/
