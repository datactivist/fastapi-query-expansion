import json
import numpy as np
from enum import Enum
from pathlib import Path
import requests

import sql_query
import request_lexical_resources

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


def compute_feedback_score(keyword1, keyword2):

    """
    Compute the feedback score

    Input:  keyword1: keyword entered by the user and at the origin of the proposed keyword
            keyword2: proposed keyword by the expansion API

    Output: Feedback score, default value to -1 if no feedbacks available
    """

    # get feedback for that particular keyword1 -> keyword2 sequence (TODO: check for similar search?)
    feedbacks = sql_query.get_feedback_for_expansion(keyword1, keyword2)

    if len(feedbacks) > 0:
        # Normalize mean of all feedbacks (-1->1 to 0->1)
        feedback_score = (np.mean(feedbacks) - (-1)) / (1 - (-1))
    else:
        # Default value if no feedbacks available
        feedback_score = -1


def combine_similarity_and_feedback_score(feedback_score, similarity_score, alpha=0.5):

    """
    Compute the combination of embedding similarity and feedback score

    Input:  feedback_score: feedback score computed by compute_feedback_score, if no feedbacks, default to (1 - alpha)
            similarity_score: similarity between the two keywords
            alpha: higher alpha = higher feedback weight

    Output: score combination of similarity and feedback
    """

    if feedback_score == -1:
        feedback_score = 1 - alpha

    return (1 - alpha) * similarity_score + alpha * feedback_score


def use_feedback(original_keyword, keyword_sim_list, alpha=0.5):

    """
    Apply feedback score to the list of similarity using the compute similarity feedback score method

    Input:  original_keyword: keyword at the origin of the proposed keywords
            keyword_sim_list: list of tuple of type (keyword, similariy)
            alpha: higher alpha = higher feedback weight

    Output: list of tuple of type (keyword, similarity) with the newly computed scores
    """

    new_list = []

    for keyword_sim in keyword_sim_list:

        feedback_score = compute_feedback_score(original_keyword, keyword_sim[0])

        new_sim = combine_similarity_and_feedback_score(
            feedback_score, keyword_sim[1], alpha
        )
        new_list.append((keyword_sim[0], new_sim))

    return new_list

  
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

        # Apply feedback scores
        similar_words[SimilarityType.similar] = use_feedback(
            keyword, similar_words[SimilarityType.similar]
        )

        # Resort the array with new scores
        similar_words[SimilarityType.similar] = sort_array_of_tuple_with_second_value(
            similar_words[SimilarityType.similar]
        )

        # Remove scores and keep only keywords
        similar_words[SimilarityType.similar] = remove_second_key_from_array_of_tuple(
            similar_words[SimilarityType.similar]
        )

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
