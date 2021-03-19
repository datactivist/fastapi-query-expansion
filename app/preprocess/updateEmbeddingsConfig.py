"""
Script to convert every downloaded files from dowloadEmbeddings.py in the directory tree app/embeddings/* into .magnitude files
"""

import json
from pathlib import Path
import sys

data_path = Path("app/data")

with open(data_path / Path("embeddings_metadata.json")) as json_file:
    data = json.load(json_file)

if len(sys.argv) > 1:
    activation = sys.argv[1].split("|")
else:
    print("Usage: python3 updateEmbeddingsConfig.py <config-string>")
    exit(1)

flag_no_embed = True
for i, embedding in enumerate(data):
    if i < len(activation):
        if activation[i] == "activate":
            flag_no_embed = False
            embedding["is_activated"] = True
        else:
            embedding["is_activated"] = False
    else:
        embedding["is_activated"] = False


if flag_no_embed:
    print(
        "Warning: No embeddings selected, please add at least one embedding in the app/api-config.config file"
    )

with open(data_path / Path("embeddings_metadata.json"), "w") as json_file:
    json.dump(data, json_file)
