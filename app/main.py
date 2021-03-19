from __future__ import annotations
import expansion
import os
import json
import numpy as np
from pathlib import Path

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional

model_list = {}


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
    max_datasud_keywords: Optional[int] = Field(5, ge=0, le=50)

    class Config:
        schema_extra = {
            "example": {
                "keywords": "éolien",
                "embeddings_type": "word2vec",
                "embeddings_name": "frWac_non_lem_no_postag_no_phrase_200_cbow_cut0.magnitude",
                "max_depth": 1,
                "max_width": 5,
                "max_datasud_keywords": 5,
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
    datasud_keywords: Optional[List[str]]

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
                "datasud_keywords": [
                    "éolienne",
                    "photovoltaïque",
                    "géothermie",
                    "biomasse",
                    "énergie",
                ],
            }
        }


embeddings_path = Path("embeddings")
# Looping on available .magnitude embeddings to save them in dictionnary
print("Starting saving embeddings in dictionnary")
for embeddings in list(embeddings_path.glob("**/*.magnitude")):
    model_list[embeddings.name] = expansion.MagnitudeModel(
        embeddings.parent.name, embeddings.name
    )
print("Saving done")

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
    if embeddings_type != expansion.EmbeddingsType.wordnet:
        path = Path("./embeddings") / Path(embeddings_type.value)
        results = []
        for filename in list(path.glob("**/*.magnitude")):
            results.append(filename.name)
        return results
    else:
        return [
            "This API uses the library NLTK, which uses the Open Multilingual Wordnet, which uses the wolf-1.0b4 embeddings, therefore you don't have to specify an embeddings name."
        ]


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
    - **max_datasud_keywords**: If >0, include the first <max> most similar words from the datasud database for each word | default value: 5
    ## Output: 
    list of expand results per keyword
    - **expand result**:
        - **original_keyword**: keyword at the root of the resulting tree
        - **tree**: list of clusters
            - **cluster**: 
                - **sense**: sense at the center of the cluster
                - **similar_words**: list of tuples of type (cluster, similarityType)
                    - **similarityType**: relation between two clusters (similars | synonyms, hyponyms, hypernyms, holonyms when using wordnet)
        - **datasud_keywords**: list of string
    """

    if query.embeddings_type == expansion.EmbeddingsType.bert:
        raise HTTPException(
            status_code=501, detail="Bert embeddings not implemented yet"
        )

    if query.embeddings_type != expansion.EmbeddingsType.wordnet:
        try:
            model = model_list[query.embeddings_name]
        except:
            raise HTTPException(
                status_code=404,
                detail="This embeddings_name doesn't exist for this embeddings_type. You can request the list of embeddings available for a particular embeddings type by requesting get(http/[...]/help_embeddings/{embeddings_type}",
            )
    else:
        model = expansion.WordnetModel()
        # TODO mettre dans le dict

    data = expansion.expand_keywords(
        model,
        query.keywords,
        query.max_depth,
        query.max_width,
        query.max_datasud_keywords,
    )
    return data
