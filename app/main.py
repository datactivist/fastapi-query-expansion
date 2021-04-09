from __future__ import annotations
import os
import json
import numpy as np
from pathlib import Path

import expansion
import requestLexicalResources

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional

model_list = {}


class Referentiel(BaseModel):

    name: str
    tags: Optional[bool] = True
    width: Optional[int] = Field(10, ge=0, le=50)


class Referentiel_Output(BaseModel):

    tags: Optional[List[str]]


class Search_Expand_Query(BaseModel):
    """
    Structure for the expand query
    """

    keywords: str
    embeddings_type: Optional[
        expansion.EmbeddingsType
    ] = expansion.EmbeddingsType.word2vec
    embeddings_name: Optional[
        str
    ] = "frWac_non_lem_no_postag_no_phrase_200_cbow_cut0.magnitude"
    max_depth: Optional[int] = Field(1, ge=0, le=3)
    max_width: Optional[int] = Field(5, ge=0, le=50)
    referentiel: Optional[Referentiel]

    class Config:
        schema_extra = {
            "example": {
                "keywords": "éolien",
                "embeddings_type": "word2vec",
                "embeddings_name": "frWac_non_lem_no_postag_no_phrase_200_cbow_cut0.magnitude",
                "max_depth": 1,
                "max_width": 5,
                "referentiel": {"name": "datasud"},
            }
        }


class Cluster(BaseModel):
    """
    Recursive class to build data tree
    """

    sense: str
    similar_senses: Optional[List[Tuple[Cluster, expansion.SimilarityType]]]
    sense_definition: Optional[str]


Cluster.update_forward_refs()


class ResponseFromSense(BaseModel):
    """
    Structure for expand query's results
    """

    original_keyword: str
    tree: Optional[List[Cluster]]
    referentiel: Referentiel_Output

    class Config:
        schema_extra = {
            "example": {
                "original_keyword": "éolien",
                "tree": [
                    {
                        "sense": "éolien",
                        "similar_senses": [
                            [
                                {
                                    "sense": "éolienne",
                                    "similar_senses": None,
                                    "sense_definition": None,
                                },
                                "similar",
                            ],
                            [
                                {
                                    "sense": "éoliennes",
                                    "similar_senses": None,
                                    "sense_definition": None,
                                },
                                "similar",
                            ],
                            [
                                {
                                    "sense": "photovoltaïque",
                                    "similar_senses": None,
                                    "sense_definition": None,
                                },
                                "similar",
                            ],
                            [
                                {
                                    "sense": "éoliens",
                                    "similar_senses": None,
                                    "sense_definition": None,
                                },
                                "similar",
                            ],
                            [
                                {
                                    "sense": "mw",
                                    "similar_senses": None,
                                    "sense_definition": None,
                                },
                                "similar",
                            ],
                        ],
                    },
                ],
                "referentiel": {
                    "tags": [
                        "éolienne",
                        "photovoltaïque",
                        "géothermie",
                        "biomasse",
                        "énergie",
                    ],
                },
            }
        }


# Launch API
app = FastAPI()


@app.get("/help_embeddings/{embeddings_type}")
async def get_embeddings_names(embeddings_type: expansion.EmbeddingsType):
    """
    ## Function
    Return every variant embeddings available for the embeddings_type given in parameter
    ## Parameter
    ### Required
    - **embeddings_type**: Type of the embeddings
    ## Output
    List of embeddings variant available
    """

    return requestLexicalResources.get_available_embeddings(embeddings_type)


@app.get("/help_referentiels")
async def get_referentiels():
    """
    ## Function
    Return every referentiels available
    """

    return requestLexicalResources.get_available_referentiels()


@app.post("/query_expand", response_model=List[ResponseFromSense])
async def manage_query_expand(query: Search_Expand_Query):
    """
    ## Function
    Returns results of the search query expansion given in parameter:
    ## Parameters
    ### Required Parameters:
    - **keywords**: String
    ### Optional Parameters:
    - **embeddings_type**: Type of the embeddings | default value: word2vec
    - **embeddings_name**: Variant of the embeddings | default value: frWac_non_lem_no_postag_no_phrase_200_cbow_cut0.magnitude
    - **max_depth**: Depth of the keyword search | default value: 1
    - **max_width**: Width of the keyword search | default value: 5 # Ignored when using wordnet
    - **referentiel**: Referentiel to use | default value: None
    ## Output: 
    list of expand results per keyword
    - **expand result**:
        - **original_keyword**: keyword at the root of the resulting tree
        - **tree**: list of clusters
            - **cluster**: 
                - **sense**: sense at the center of the cluster
                - **similar_words**: list of tuples of type (cluster, similarityType)
                    - **similarityType**: relation between two clusters (similars | synonyms, hyponyms, hypernyms, holonyms when using wordnet)
        - **referentiel**:
            - **tags**: List of string
    """

    data = expansion.expand_keywords(
        query.keywords,
        query.embeddings_type,
        query.embeddings_name,
        query.max_depth,
        query.max_width,
        query.referentiel,
    )

    print(data)

    return data
