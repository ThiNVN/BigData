from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from sklearn.preprocessing import MinMaxScaler
import numpy as np

class HybridSearch:
    def __init__(self, es_url="https://4ca02f04fab74e44a2ab8c97bfec0bd0.asia-southeast1.gcp.elastic-cloud.com:443",es_api_key="T2VwanhaWUJDZGNLQUpCV1FSQXA6cGtVNDVybFduVFdmRzA5dFNKTElRUQ==", model_name="all-MiniLM-L6-v2"):
        self.es = Elasticsearch(es_url,api_key=es_api_key)
        self.model = SentenceTransformer(model_name)
        self.index_name="games"

    # --- Vector Encoder ---
def encode_query(self,text):
    return self.model.encode(text).tolist()

# --- Search Functions ---
def search_bm25(self,query_text, size=100, filtered_ids=None):
    bm25_query = {
        "size": size,
        "query": {
            "bool": {
                "must": [
                    {"match": {"detailed_description": query_text}}
                ]
            }
        }
    }

    if filtered_ids:
        bm25_query["query"]["bool"]["filter"] = {
            "ids": {"values": list(filtered_ids)}
        }

    res = self.es.search(index=self.index_name, body=bm25_query)
    return {hit["_id"]: hit["_score"] for hit in res["hits"]["hits"]}

def search_vector(self,query_vector, k=100, candidates=200, filtered_ids=None):
    if filtered_ids:
        # Fallback: manually filter after search (ES does not support knn+ids directly)
        vector_query = {
            "knn": {
                "field": "description_vector",
                "query_vector": query_vector,
                "k": candidates,
                "num_candidates": candidates
            }
        }
        res = self.es.search(index=self.index_name, body=vector_query)
        return {
            hit["_id"]: hit["_score"]
            for hit in res["hits"]["hits"] if hit["_id"] in filtered_ids
        }

    else:
        vector_query = {
            "knn": {
                "field": "description_vector",
                "query_vector": query_vector,
                "k": k,
                "num_candidates": candidates
            }
        }
        res = self.es.search(index=self.index_name, body=vector_query)
        return {hit["_id"]: hit["_score"] for hit in res["hits"]["hits"]}

# --- Normalize Scores ---
def normalize(self,scores_dict):
    ids = list(scores_dict.keys())
    scores = np.array(list(scores_dict.values())).reshape(-1, 1)
    normalized = MinMaxScaler().fit_transform(scores).flatten()
    return dict(zip(ids, normalized))

# --- Combine Scores ---
def combine_scores(self,bm25_scores, vec_scores, weight_bm25=0.5, weight_vec=0.5):
    norm_bm25 = self.normalize(bm25_scores)
    norm_vec = self.normalize(vec_scores)

    combined = {}
    for _id in set(norm_bm25.keys()).union(norm_vec.keys()):
        bm25 = norm_bm25.get(_id, 0)
        vec = norm_vec.get(_id, 0)
        combined[_id] = weight_bm25 * bm25 + weight_vec * vec
    return combined

# --- Final Hybrid Search ---
import json

def hybrid_search(self,query_text, top_k=10, filtered_ids=None):
    print(f"\nSearching for: {query_text}")

    query_vector = self.encode_query(query_text)
    bm25_scores = self.search_bm25(query_text, filtered_ids=filtered_ids)
    vec_scores = self.search_vector(query_vector, filtered_ids=filtered_ids)

    combined = combine_scores(bm25_scores, vec_scores)
    top_results = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_k]

    results = []
    for rank, (_id, score) in enumerate(top_results, start=1):
        doc = self.es.get(index=self.index_name, id=_id)
        source = doc["_source"]

        filtered_source = {
            k: v for k, v in source.items()
            if k not in ["cluster", "description_vector"]
        }

        result = {
            "rank": rank,
            "score": round(score, 2),
            **filtered_source
        }

        results.append(result)

    return json.dumps(results, indent=2, ensure_ascii=False)

# --- Direct Search by Name ---
def direct_elastic(self,name):
    query = {
        "query": {
            "term": {
                "name.raw": name
            }
        }
    }

    res = self.es.search(index=self.index_name, body=query)

    results = []
    for hit in res["hits"]["hits"]:
        source = hit["_source"]
        filtered_source = {
            k: v for k, v in source.items()
            if k not in ["cluster", "description_vector"]
        }
        results.append(filtered_source)

    return json.dumps(results, ensure_ascii=False)

# --- Optional Filter Function ---
def filter_elastic(self,filters,use_cluster=True):
    query = {
        "query": {
            "bool": {
                "must": []
            }
        }
    }

    # Year Range Filter
    if filters.get("year_range"):
        year_range = filters["year_range"]
        if isinstance(year_range, str) and "-" in year_range:
            try:
                start_year, end_year = map(int, year_range.split("-"))
            except ValueError:
                start_year = end_year = int(year_range)
        else:
            start_year = end_year = int(year_range)

        query["query"]["bool"]["must"].append({
            "range": {
                "release_date": {
                    "gte": f"{start_year}-01-01",
                    "lte": f"{end_year}-12-31"
                }
            }
        })

    # Developer Filter
    if filters.get("developer"):
        query["query"]["bool"]["must"].append({
            "term": {
                "developers": filters["developer"]
            }
        })

    # Publisher Filter
    if filters.get("publisher"):
        query["query"]["bool"]["must"].append({
            "term": {
                "publishers": filters["publisher"]
            }
        })

    # Game Description (full-text search)
    if filters.get("game_description"):
        query["query"]["bool"]["must"].append({
            "match": {
                "detailed_description": filters["game_description"]
            }
        })

    # Cluster Filter
    if use_cluster and filters.get("cluster"):
        query["query"]["bool"]["must"].append({
            "term": {
                "cluster": filters["cluster"]
            }
        })

    # Platform Filter (windows/mac/linux)
    if filters.get("platform"):
        platform_field = f"platforms_{filters['platform'].lower()}"
        query["query"]["bool"]["must"].append({
            "term": {
                platform_field: True
            }
        })

    # Currency Filter
    if filters.get("currency"):
        query["query"]["bool"]["must"].append({
            "term": {
                "price_currency": filters["currency"]
            }
        })

    # Price Limit
    if filters.get("price_limit"):
        try:
            price = float(filters["price_limit"])
            query["query"]["bool"]["must"].append({
                "range": {
                    "price_final": {
                        "lte": price
                    }
                }
            })
        except ValueError:
            pass

    # Language Filter
    if filters.get("language"):
        query["query"]["bool"]["must"].append({
            "terms": {
                "supported_languages.keyword": filters["language"]
        }
    })

    query["size"] = 1000
    res = self.es.search(index=self.index_name, body=query)

    return [hit["_id"] for hit in res["hits"]["hits"]]


def get_games(self,results):
    func_name=results.get("function_name")
    if func_name=="direct_search":
        name=results.get("name")
        return self.direct_elastic(name)
    elif func_name=="filter_search":
        result_filter = self.filter_elastic(results, use_cluster=True)
        print(result_filter)
        if not result_filter or len(result_filter) < 5:
          result_filter = filter_elastic(results, use_cluster=False)
        query_text=results.get("game_description")
        return self.hybrid_search(query_text,filtered_ids=result_filter)
    else:
        return results.get("response")