import requests

lexical_resources_API_host_name = '127.0.0.1'
lexical_resources_API_port = '8003'
lexical_resources_API_url = (
    "http://" + lexical_resources_API_host_name + ":" + lexical_resources_API_port + "/"
)


def get_available_embeddings(embeddings_type):

    get_embeddings_url = (
        lexical_resources_API_url + "help_embeddings/" + embeddings_type
    )

    return requests.get(get_embeddings_url).json()


def get_available_referentiels():

    get_referentiels_url = lexical_resources_API_url + "help_referentiels"

    return requests.get(get_referentiels_url).json()


def get_similarity(
    keyword1,
    keyword2,
    embeddings_type="word2vec",
    embeddings_name="frWac_non_lem_no_postag_no_phrase_200_cbow_cut0.magnitude",
):

    get_similarity_url = lexical_resources_API_url + "similarity"

    body = {
        "keyword1": keyword1,
        "keyword2": keyword2,
        "embeddings_type": embeddings_type,
        "embeddings_name": embeddings_name,
    }

    return requests.post(get_similarity_url, json=body).json()


def get_most_similar(
    keyword,
    embeddings_type="word2vec",
    embeddings_name="frWac_non_lem_no_postag_no_phrase_200_cbow_cut0.magnitude",
    topn=10,
    slider=0,
):

    get_most_similar_url = lexical_resources_API_url + "most_similar"

    body = {
        "keyword": keyword,
        "embeddings_type": embeddings_type,
        "embeddings_name": embeddings_name,
        "topn": topn,
        "slider": slider,
    }

    return requests.post(get_most_similar_url, json=body).json()


def get_most_similar_referentiels(
    keyword,
    referentiel,
    ref_type,
    embeddings_type="word2vec",
    embeddings_name="frWac_non_lem_no_postag_no_phrase_200_cbow_cut0.magnitude",
    topn=10,
    slider=0,
):

    get_most_similar_referentiels_url = (
        lexical_resources_API_url + "most_similar_referentiel"
    )

    body = {
        "keyword": keyword,
        "referentiel": referentiel,
        "ref_type": ref_type,
        "embeddings_type": embeddings_type,
        "embeddings_name": embeddings_name,
        "topn": topn,
        "slider": slider,
    }

    return requests.post(get_most_similar_referentiels_url, json=body).json()

