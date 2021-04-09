import json
import numpy as np
from enum import Enum
from pathlib import Path

from nltk.corpus import wordnet as wn
import nltk

from pymagnitude import *

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


def get_senses_from_keyword(embeddings_type, keyword):

    """
    Get the senses from keyword

    if model is wordnet: list of synset
    if model is not wordnet: list of size 1 containing only keyword

    output: list of senses
    """

    return (
        print("TODO")
        if embeddings_type == EmbeddingsType.wordnet
        else [keyword]
    )


def split_user_entry(user_entry):
    """
    Split the user entry into keywords

    Input: keywords as string
    Output: keywords as list

    Currently splitting them with space char
    """

    return user_entry.split(" ")


def sort_array_of_tuple_with_second_value(array):
    """
    Return an array of tuple sorted by second key values
    """

    array.sort(key=lambda x: x[1], reverse=True)
    return array


def get_cluster(keyword, embeddings_type, embeddings_name, max_width, max_depth, current_depth):

    """
    Recursive function to build the data structure tree

    Input:  keywords: a string
            embeddings_type: type of the embeddings
            embeddings_name: name of the embeddings
            width: maximum depth of keywords search
            depth: maximum width of keywords search
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

    if current_depth < max_depth:

        # to avoid looping on most similar words
        slider = 1 if current_depth > 0 else 0

        similar_words = request_lexical_resources.get_most_similar(
            keyword, embeddings_type, embeddings_name, max_width, slider
        )

        for word in similar_words[SimilarityType.synonym]:
            sub_cluster = {}
            sub_cluster["sense"] = word
            cluster["similar_senses"].append([sub_cluster, SimilarityType.synonym])

        for word in similar_words[SimilarityType.similar]:
            sub_cluster = get_cluster(
                word, embeddings_type, embeddings_name, max_width, max_depth, current_depth + 1
            )
            cluster["similar_senses"].append([sub_cluster, SimilarityType.similar])

    if current_depth + 1 < max_depth:

        for sim_type in SimilarityType:
            if (
                sim_type != SimilarityType.synonym
                and sim_type != SimilarityType.similar
            ):
                for sense in similar_words[sim_type]:
                    sub_cluster = get_cluster(
                        sense, embeddings_type, embeddings_name, max_width, max_depth, current_depth + 1
                    )
                    cluster["similar_senses"].append([sub_cluster, sim_type])

    if len(cluster["similar_senses"]) == 0:
        cluster["similar_senses"] = None

    return cluster


def build_tree(keyword, embeddings_type, embeddings_name, max_depth, max_width, referentiel):

    """
    Build the data structure tree for one particular sense list (originating from one keyword)

    Input:  keywords: a string
            embeddings_type: type of the embeddings
            embeddings_name: name of the embeddings
            max_depth: maximum depth of keywords search
            max_width: maximum width of keywords search
            referentiel: referentiel to use for expansion
    
    Output: Data tree for keyword
    """

    search_result = {}
    search_result["original_keyword"] = keyword

    tree = []

    senses = get_senses_from_keyword(embeddings_type, keyword)

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
        else:
            referentiel_output = []
        current_search_result["referentiel"] = referentiel_output

        tree.append(get_cluster(sense, embeddings_type, embeddings_name, max_width, max_depth, 0))

    search_result["tree"] = tree

    return search_result


def expand_keywords(keywords, embeddings_type, embeddings_name, max_depth, max_width, referentiel):
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

    keywords_list = split_user_entry(keywords)

    data = []

    for keyword in keywords_list:

        if len(keyword) > 3:

            keyword = keyword.lower()

            data.append(
                build_tree(keyword, embeddings_type, embeddings_name, max_depth, max_width, referentiel)
            )

    return data
