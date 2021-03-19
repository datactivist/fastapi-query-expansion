"""
Script to preload and save datasud keywords as vector for each embeddings of type .magnitude in the directory tree app/embeddings/*
"""

import json
import os
import numpy as np
from pathlib import Path

from pymagnitude import *

data_path = Path("data")
keyw_path = Path("keywords_vectors")
embeddings_path = Path("embeddings")


def is_activated(embeddings, embeddings_metadata):
    for metadata in embeddings_metadata:
        if (
            str(Path(metadata["name"]).with_suffix(".magnitude"))
            == str(embeddings.name)
            and metadata["is_activated"]
        ):
            return True
    return False


def preload_datasud_vectors(model, embeddings_type, embeddings_name, datasud_keywords):
    """
    Preload datasud vectors by saving them separately in "datasud_keywords_vectors/embeddings_type/embeddings_name.npy"
    Input:  model: magnitude model
            embeddings_type: type of the embeddings
            embeddings_name: name of the embeddings
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
        vectors = model.query(datasud_keywords)
        np.save(path_vec, vectors)

    else:
        print("vectors for", embeddings_name, "already exist")

    model = None


# Load datasud keywords as a list of string
with open(data_path / Path("datasud_keywords.json"), encoding="utf-16") as json_file:
    datasud_keywords = json.load(json_file,)["result"]


# embeddings metadata
with open(data_path / Path("embeddings_metadata.json")) as json_file:
    metadata = json.load(json_file)

# Looping on available .magnitude embeddings to preload them
for embeddings in list(embeddings_path.glob("**/*.magnitude")):
    if is_activated(embeddings, metadata):
        preload_datasud_vectors(
            Magnitude(embeddings),
            embeddings.parent.name,
            embeddings.name,
            datasud_keywords,
        )
