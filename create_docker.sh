#! /usr/bin/env bash

# Downloading missing embeddings and converting them
echo ""
echo "Downloading and converting missing embeddings, this can take a while..."
python app/preprocess/downloadEmbeddings.py
echo "Downloading and converting done!"
echo ""

echo ""

# Preloading Datasud Vectors if option -v is given
while [ -n "$1" ]; do # while loop starts

	case "$1" in

	-v) python app/preprocess/preloadVectors.py ;; # Message for -a option

	*) echo "Option $1 not recognized" ;; # In case you typed a different option other than a,b,c

	esac

	shift

done

echo ""

sudo docker build -t apitest .
sudo docker rm apitest
sudo docker run -p 80:80 --name apitest  apitest