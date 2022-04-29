import json
import numpy as np
from enum import Enum
from pathlib import Path
import re

import sql_query
import request_lexical_resources

data_path = Path("data")
keyw_path = Path("keywords_vectors")
embeddings_path = Path("embeddings")

keywords_delimitor = " |,|;|_|\|"


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

    return print("TODO") if embeddings_type == EmbeddingsType.wordnet else [keyword]


def compute_feedback_score(original_keyword, proposed_keyword):

    """
    Compute the feedback score
    Input:  original_keyword: keyword at the origin of the proposition
            proposed_keyword: keyword proposed to the user
    Output: Feedback score, default value to 0.4 if no feedbacks available
    """

    # This old version take into account when a user doesn't choose a keyword, I changed it so that a keyword not chosen doesn't get as much as a penality
    """
    # get feedback for that particular search_id -> result_url sequence (TODO: check for similar search?)
    feedbacks = sql_query.get_feedback_for_reranking(user_search, result)
    if feedbacks != None and len(feedbacks) > 0:
        # Normalize mean of all feedbacks (-1->1 to 0->1)
        feedback_score = (np.mean(feedbacks) - (-1)) / (1 - (-1))
    else:
        # Default value if no feedbacks available
        feedback_score = 0
    return feedback_score
    """

    # get feedback for that particular keyword1 -> keyword2 sequence (TODO: check for similar search?)
    feedbacks = sql_query.get_feedback_for_expansion(original_keyword, proposed_keyword)
    chosen = 0
    ignored = 0
    base_score = 0.4
    if feedbacks is not None and len(feedbacks) > 0:
        for feedback in feedbacks:
            if feedback == 1:
                chosen += 1
            if feedback == -1:
                ignored += 1

        # remove a point for every 10 users that didn't choose it
        chosen -= int(ignored / 10)

        feedback_score = base_score + (chosen / len(feedbacks))

    else:
        feedback_score = base_score

    # print(result.title, ":", max(0, min(feedback_score, 1)))

    return max(0, min(feedback_score, 1))


def combine_similarity_and_feedback_score(feedback_score, similarity_score, alpha=0.5):

    """
    Compute the combination of embedding similarity and feedback score

    Input:  feedback_score: feedback score computed by compute_feedback_score, if no feedbacks, default to (1 - alpha)
            similarity_score: similarity between the two keywords
            alpha: higher alpha = higher feedback weight

    Output: score combination of similarity and feedback
    """

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

        # print(keyword_sim[0], ":", keyword_sim[1], "->", new_sim)

        new_list.append((keyword_sim[0], new_sim))

    return new_list


def split_user_entry(user_entry):
    """
    Split the user entry into keywords

    Input: keywords as string
    Output: keywords as list

    Currently splitting them with space char
    """

    return re.split(keywords_delimitor, user_entry)


def sort_array_of_tuple_with_second_value(array):
    """
    Return an array of tuple sorted by second key values
    """

    array.sort(key=lambda x: x[1], reverse=True)
    return array


def get_geoloc_parents(ref_name, tag_name):

    parent_list = request_lexical_resources.get_most_similar_referentiels(
        tag_name, ref_name, "geoloc"
    )

    parents = [parent["word"] for parent in parent_list]

    return {"name": ref_name, "type": "geoloc", "tags": parents}


def get_cluster(
    keyword,
    referentiel,
    embeddings_type,
    embeddings_name,
    max_width,
    max_depth,
    current_depth,
):

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
            keyword,
            referentiel.name,
            embeddings_type,
            embeddings_name,
            max_width,
            slider,
        )

        # Process for using feedback
        temp_sim = []
        for word_sim in similar_words["similar"]:
            temp_sim.append((word_sim["word"], word_sim["similarity"]))
        temp_sim = use_feedback(keyword, temp_sim, 0.6)
        temp_sim = sort_array_of_tuple_with_second_value(temp_sim)
        similar_words["similar"] = []
        for temp in temp_sim:
            similar_words["similar"].append({"word": temp[0], "similarity": temp[1]})
        # Process for using feedback

        for word in similar_words[SimilarityType.synonym]:
            sub_cluster = {}
            sub_cluster["sense"] = word
            cluster["similar_senses"].append([sub_cluster, SimilarityType.synonym])

        for word in similar_words[SimilarityType.similar]:
            sub_cluster = get_cluster(
                word,
                referentiel,
                embeddings_type,
                embeddings_name,
                max_width,
                max_depth,
                current_depth + 1,
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
                        sense,
                        referentiel,
                        embeddings_type,
                        embeddings_name,
                        max_width,
                        max_depth,
                        current_depth + 1,
                    )
                    cluster["similar_senses"].append([sub_cluster, sim_type])

    if len(cluster["similar_senses"]) == 0:
        cluster["similar_senses"] = None

    return cluster


def build_tree(
    keyword, embeddings_type, embeddings_name, max_depth, max_width, referentiels
):

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

        referentiel_output = []
        if referentiels is not None:
            for referentiel in referentiels:
                if referentiel.type == "tags":

                    results = request_lexical_resources.get_most_similar_referentiels(
                        sense,
                        referentiel.name,
                        referentiel.type,
                        embeddings_type,
                        embeddings_name,
                        referentiel.width,
                        0,
                    )

                    keyword_sim_list = []
                    for result in results:
                        keyword_sim_list.append((result["word"], result["similarity"]))
                    keyword_sim_list = use_feedback(sense, keyword_sim_list, 0.6)
                    keyword_sim_list = sort_array_of_tuple_with_second_value(
                        keyword_sim_list
                    )

                    referentiel_output = {
                        "name": referentiel.name,
                        "type": referentiel.type,
                        "tags": [x[0] for x in keyword_sim_list],
                    }

        search_result["referentiel"] = referentiel_output

        tree.append(
            get_cluster(
                sense,
                referentiel,
                embeddings_type,
                embeddings_name,
                max_width,
                max_depth,
                0,
            )
        )

    search_result["tree"] = tree

    return search_result


def expand_keywords(
    keywords, embeddings_type, embeddings_name, max_depth, max_width, referentiels
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

    keywords_list = split_user_entry(keywords)

    data = []
    for keyword in keywords_list:
        if len(keyword) > 3:
            keyword = keyword.lower()
            data.append(
                build_tree(
                    keyword,
                    embeddings_type,
                    embeddings_name,
                    max_depth,
                    max_width,
                    referentiels,
                )
            )
    for referentiel in referentiels:
        if referentiel.type == "geoloc":
            data.append(
                {
                    "original_keyword": referentiel.tag,
                    "referentiel": get_geoloc_parents(
                        referentiel.name, referentiel.tag
                    ),
                }
            )
    return data
