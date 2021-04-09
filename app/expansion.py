import json
import numpy as np
from enum import Enum
from pathlib import Path
import requests

import requestLexicalResources

data_path = Path("data")
keyw_path = Path("keywords_vectors")
embeddings_path = Path("embeddings")


class EmbeddingsType(str, Enum):
    word2vec = "word2vec"
    wordnet = "wordnet"
    fasttext = "fasttext"
    bert = "bert"
    elmo = "elmo"


class SimilarityType(str, Enum):
    synonym = "synonym"
    hyponym = "hyponym"
    hypernym = "hypernym"
    holonym = "holonym"
    similar = "similar"


def split_user_entry(user_entry):
    """
    Split the user entry into keywords

    Input: keywords as string
    Output: keywords as list

    Currently splitting them with space char
    """

    return user_entry.split(" ")


def second_key_from_tuple(tuple):
    """
    Return second value of a tuple, used for sorting array of dimension [n, 2] on the second value
    """

    return tuple[1]


def get_cluster(keyword, embeddings_type, embeddings_name, width, depth, current_depth):

    """
    Recursive function to build the data structure tree

    Input:  keyword: string or synset
            width: width of each cluster #Ignore when using WordnetModel
            depth: depth to achieve
            current_depth: current depth
    Output: A cluster
    """

    cluster = {}
    if type(keyword) == str:
        pass
    elif type(keyword) == dict:
        keyword = keyword["word"]
    else:
        keyword = str(keyword)
    cluster["sense"] = keyword

    cluster["similar_senses"] = []

    if current_depth < depth:

        # to avoid looping on most similar words
        slider = 1 if current_depth > 0 else 0

        print(keyword)

        similar_words = requestLexicalResources.get_most_similar(
            keyword, embeddings_type, embeddings_name, width, slider
        )

        print(similar_words)
        print(similar_words["synonym"])
        print()
        print()

        for word in similar_words[SimilarityType.synonym]:
            sub_cluster = {}
            sub_cluster["sense"] = word
            cluster["similar_senses"].append([sub_cluster, SimilarityType.synonym])

        for word in similar_words[SimilarityType.similar]:
            sub_cluster = get_cluster(
                word, embeddings_type, embeddings_name, width, depth, current_depth + 1
            )
            cluster["similar_senses"].append([sub_cluster, SimilarityType.similar])

    if current_depth + 1 < depth:

        for sim_type in SimilarityType:
            if (
                sim_type != SimilarityType.synonym
                and sim_type != SimilarityType.similar
            ):
                for sense in similar_words[sim_type]:
                    sub_cluster = get_cluster(
                        sense,
                        embeddings_type,
                        embeddings_name,
                        width,
                        depth,
                        current_depth + 1,
                    )
                    cluster["similar_senses"].append([sub_cluster, sim_type])

    if len(cluster["similar_senses"]) == 0:
        cluster["similar_senses"] = None

    return cluster


def expand_keywords(
    keywords, embeddings_type, embeddings_name, max_depth, max_width, referentiel
):
    """
    Return the most similar keywords from the initial keywords

    Input:  keywords: a string
            embeddings_type: type of the embeddings
            embeddings_name: name of the embeddings
            max_depth: maximum depth of keywords search
            max_width: maximum width of keywords search
            referentiel: object of type main.referentiel
    Output: Data structure with most similar keywords found
    """

    keywords = split_user_entry(keywords)

    data = []

    for keyword in keywords:
        if len(keyword) > 3:

            keyword = keyword.lower()

            # Generate list of sense for wordnet (just a list of size 1 if other embeddings type)
            senses = (
                wn.synsets(keyword, lang="fra")
                if embeddings_type == EmbeddingsType.wordnet
                else [keyword]
            )

            current_tree = []
            current_search_result = {}
            current_search_result["original_keyword"] = keyword

            for sense in senses:

                if referentiel is not None:
                    results = requestLexicalResources.get_most_similar_referentiels(
                        sense,
                        referentiel.name,
                        embeddings_type,
                        embeddings_name,
                        referentiel.width,
                        0,
                    )

                    if type(results) is list:
                        referentiel_output = {
                            "tags": [result["word"] for result in results]
                        }
                    else:
                        referentiel_output = []
                    current_search_result["referentiel"] = referentiel_output

                current_tree.append(
                    get_cluster(
                        sense, embeddings_type, embeddings_name, max_width, max_depth, 0
                    )
                )

            current_search_result["tree"] = current_tree
            data.append(current_search_result)

    return data
