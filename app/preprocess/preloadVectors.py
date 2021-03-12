import json
import os
import timeit
import numpy as np
from pathlib import Path

from pymagnitude import *

data_path = Path("app/data")
keyw_path = Path("app/keywords_vectors")
embeddings_path = Path("app/embeddings")


def preload_datasud_vectors(model, embeddings_type, embeddings_name, datasud_keywords):
    """
    Preload datasud vectors by saving them separately in "datasud_keywords_vectors/embedding_type/embedding_name.npy"
    Input:  model: magnitude model
            datasud_keywords: Datasud keywords as list of string
    """

    if not os.path.isdir(keyw_path):
        os.mkdir(keyw_path)

    path_dir = keyw_path / Path(embeddings_type)
    path_vec = path_dir / Path(embeddings_name).with_suffix(".npy")

    if not os.path.isdir(path_dir):
        os.mkdir(path_dir)

    if not os.path.isfile(path_vec):

        print("Saving datasud keywords vectors for", embeddings_name)
        start = timeit.default_timer()
        vectors = model.query(datasud_keywords)
        np.save(path_vec, vectors)
        end = timeit.default_timer()
        print("Vectors saved")

    else:
        print("vectors for", embeddings_name, "already exist")

    model = None


# Load datasud keywords as a list of string
with open(data_path / Path("datasud_keywords.json"), encoding="utf-16") as json_file:
    datasud_keywords = json.load(json_file,)["result"]

# Looping on available .magnitude embeddings to preload them
print("\nStarting Preloading of datasud vectors")
start = timeit.default_timer()
for embeddings in list(embeddings_path.glob("**/*.magnitude")):
    model = Magnitude(embeddings)
    preload_datasud_vectors(
        model, embeddings.parent.name, embeddings.name, datasud_keywords
    )
end = timeit.default_timer()
print("Preloading of datasud vectors done:", end - start, "\n")
