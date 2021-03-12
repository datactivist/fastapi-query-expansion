# FastAPI Query Expansion

## Installation

`sudo bash create_docker.sh`

This command will:
- Download the missing embeddings using `data/embeddings_metadata.json` and save them in `embeddings/embeddings_type/embeddings_name.[bin|gz]`
- Extract the archive if the embeddings are in a `.gz` file 
- Run the docker build on the dockerfile, this will:
    - import the official fastapi docker https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
    - create an image: `fastapi-query-expansion:[version]`
    - start the `prestart.sh` script
        - download libraries requirements from `requirements.txt`
        - Convert the embeddings in `.magnitude` files and delete the `.bin` files
        - Save the datasud keyword as vectors for each embeddings and save them in `keywords_vectors/embeddings_type/embeddings_name.npy`
        - Preload the embeddings using magnitudeModel.most_similar()
- Run a docker container with the same name as the image

## API Documentation

Once the docker is started, the documentation of the API is available here: http://127.0.0.1/docs#/
