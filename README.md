# FastAPI Query Expansion

## Installation

`bash create_docker.sh [-v]`

This command will:
- Download the missing embeddings using `data/embeddings_metadata.json` and save them in `embeddings/embeddings_type/embeddings_name.[bin|gz]`
- Extract the archive if the embeddings are in a `.gz` file
- Convert the embeddings in `.magnitude` files and delete the `.bin` files
- If the option -v is used, it will preload the datasud keywords vectors for each embeddings and save them in `keywords_vectors/embeddings_type/embeddings_name.npy`
- Run the docker build on the dockerfile, this will:
    - Start the `prestart.sh` script to preload the embeddings using magnitudeModel.most_similar()
    - download libraries requirements from `requirements.txt`
    - start the docker https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker
    - create an image: `expansion-query-api:[version]`
- Run a docker container with the same name as the image

## API Documentation

Once the docker is started, the documentation of the API is available here: http://127.0.0.1/docs#/