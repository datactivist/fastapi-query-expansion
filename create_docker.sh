#! /usr/bin/python

# Downloading missing embeddings and converting them
echo ""
echo "Downloading missing embeddings, this can take a while..."
python3 app/preprocess/downloadEmbeddings.py
echo "Downloading done!"
echo ""

sudo docker build -t fastapi-query-expansion:1.0.0 .
sudo docker rm apitest
sudo docker run -p 80:80 --name fastapi-query-expansion:1.0.0  fastapi-query-expansion:1.0.0