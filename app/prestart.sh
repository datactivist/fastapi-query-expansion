#! /usr/bin/env bash
echo ""
echo "Starting conversion of embeddings to .magnitude, this may take some times..."
python /app/preprocess/convertEmbeddings.py
echo "Conversion done"
echo ""

echo ""
echo "Starting preload of embeddings using most_similar function"
python /app/preprocess/preloadEmbeddings.py
echo "Preloading done"
echo ""

echo ""
echo "Starting saving of datasud vectors"
python /app/preprocess/preloadVectors.py
echo "Saving done"
echo ""

