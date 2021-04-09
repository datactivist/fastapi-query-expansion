# FastAPI Query Expansion

## Déploiement sans docker

Requirements: 
- python >= 3.X

### Installation dépendances

```
pip install fastapi uvicorn
```

Dans le fichier `fastapi-query-expansion/api-config.config`, changer la valeur de `deployment_method` en `local` et créez la configuration que vous souhaitez.

Depuis le répertoire `fastapi-query-expansion/`

```
bash ./start_service.sh
```

## Créer une image docker

Requirements:
- Python >= 3.X
- Docker >= 20.X

Dans le fichier `fastapi-query-expansion/api-config.config`, changer la valeur de `deployment_method` en `docker` et créez la configuration que vous souhaitez.

Depuis le répertoire `fastapi-query-expansion/`

```
bash ./start_service.sh
```

## API Documentation

Une fois le service lancé (localement), une documentation intéractible est disponible à cette adresse: http://127.0.0.1:8002/docs#/
