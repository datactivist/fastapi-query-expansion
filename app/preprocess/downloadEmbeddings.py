import requests
import os
import gzip
import shutil
import json
from pathlib import Path

data_path = Path("app/data")
embeddings_path = Path("app/embeddings")


def convert_embeddings_to_magnitude(embedding_temp):
    """
    convert the embeddings in parameter in a magnitude file, delete the embeddings
    """

    print("Converting", embedding_temp)
    input_name = str(embedding_temp)
    filename, ext = os.path.splitext(embedding_temp)
    output_name = filename + ".magnitude"
    command = (
        "python -m pymagnitude.converter -i "
        + input_name
        + "-e 'ignore' -o "
        + output_name
    )
    os.system(command)
    os.remove(input_name)


def decompress_archive(archivename, filename):
    """
    decompress an archive of .gz, result in filename, and delete archivename
    """

    with gzip.open(archivename, "rb") as f_in:
        with open(filename, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    os.remove(archivename)
    return filename


def download_and_convert_embeddings():
    """
    download and convert all the missing embeddings from the embeddings_metadata.json file
    """

    with open(data_path / Path("embeddings_metadata.json")) as json_file:
        data = json.load(json_file)

    if not os.path.isdir(embeddings_path):
        os.mkdir(embeddings_path)

    for embedding in data:

        dir_path = embeddings_path / Path(embedding["embedding_type"])
        embedding_final = dir_path / Path(embedding["embedding_name"])
        embedding_temp = dir_path / embedding["dl_url"].rsplit("/", 1)[1]

        if not os.path.isdir(dir_path):
            os.mkdir(dir_path)

        embedding_path, embedding_extension = os.path.splitext(embedding_temp)

        # if the embedding is already downloaded
        if os.path.exists(embedding_final):

            print(embedding["embedding_name"], "already exist")

        else:

            print(embedding_final, "does not exist, downloading it...")

            embed = requests.get(embedding["dl_url"], allow_redirects=True)

            open(embedding_temp, "wb").write(embed.content)

            # if compressed, extract it (for fasttext)
            if embedding_extension == ".gz":
                embedding_temp = decompress_archive(embedding_temp, embedding_path)

            convert_embeddings_to_magnitude(embedding_temp)

            print("download done!")


download_and_convert_embeddings()
