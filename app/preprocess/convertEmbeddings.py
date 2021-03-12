"""
Script to convert every downloaded files from dowloadEmbeddings.py in the directory tree app/embeddings/* into .magnitude files
"""

import os
import json
from pathlib import Path

data_path = Path("data")
embeddings_path = Path("embeddings")


def convert_embeddings_to_magnitude(input_file):
    """
    convert the embeddings in parameter in a magnitude file, delete the old embeddings
    """

    input_file = (
        embeddings_path
        / Path(input_file["embeddings_type"])
        / Path(input_file["embeddings_name"])
    )
    output_file = input_file.with_suffix(".magnitude")

    # if magnitude file does not exists already
    if not os.path.exists(output_file):
        print("converting", input_file)
        command = (
            "python3 -m pymagnitude.converter -i "
            + str(input_file)
            + " -e 'ignore' -o "
            + str(output_file)
        )
        os.system(command)
        # os.remove(input_name)


# Open embeddings metadata to get urls
with open(data_path / Path("embeddings_metadata.json")) as json_file:
    data = json.load(json_file)

# Loop on embeddings to convert them
for embeddings in data:
    convert_embeddings_to_magnitude(embeddings)
