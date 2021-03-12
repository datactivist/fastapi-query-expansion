"""
Script to preload every .magnitude files in the directory tree app/embeddings/* by using most_similar() on them
"""

from pathlib import Path

from pymagnitude import *

embeddings_path = Path("embeddings")

# Looping on available .magnitude embeddings to preload them
for embeddings in list(embeddings_path.glob("**/*.magnitude")):
    print("Preloading", embeddings)
    model = Magnitude(embeddings)
    model.most_similar("Chargement")
    model = None

