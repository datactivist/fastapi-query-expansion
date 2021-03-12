import timeit
from pathlib import Path

from pymagnitude import *

embeddings_path = Path("embeddings")


def preload_magnitude_embeddings(model, embeddings_type, embeddings_name):
    """
    Preload embeddings by calling magnitude.most_similar()
    Input:  embedding_type: Type of the embedding
            embedding_name: Name of the embedding
            datasud_keywords: Datasud keywords as list of string
    """

    model.most_similar("Chargement")
    model = None


# Looping on available .magnitude embeddings to preload them
print("\nStarting Preloading of embeddings using most similar")
start = timeit.default_timer()
for embeddings in list(embeddings_path.glob("**/*.magnitude")):
    model = Magnitude(embeddings)
    preload_magnitude_embeddings(model, embeddings.parent.name, embeddings.name)
end = timeit.default_timer()
print("Preloading of embeddings done:", end - start, "\n")
