from elasticsearch import Elasticsearch
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import json
import requests


class HybridSearch:
    def __init__(
        self,
        es_url="https://4ca02f04fab74e44a2ab8c97bfec0bd0.asia-southeast1.gcp.elastic-cloud.com:443",
        es_api_key="T2VwanhaWUJDZGNLQUpCV1FSQXA6cGtVNDVybFduVFdmRzA5dFNKTElRUQ==",
        api_url="http://localhost:8000",
        ngrok_url=None
    ):
        # If ngrok_url is provided, use it instead of the default es_url
        if ngrok_url:
            self.es = Elasticsearch(ngrok_url)
        else:
            self.es = Elasticsearch(es_url, api_key=es_api_key)
        self.api_url = api_url
        self.index_name = "games"

    # --- Vector Encoder ---
    def encode_query(self, text):
        try:
            response = requests.post(f"{self.api_url}/encode", json={"text": text})
            response.raise_for_status()  # Raise an exception for bad status codes
            return response.json()["embedding"]
        except Exception as e:
            print(f"Error encoding query: {str(e)}")
            raise

    # --- Search Functions ---
    def search_bm25(self, query_text, size=100, filtered_ids=None):
        bm25_query = {
            "size": size,
            "query": {
                "bool": {"must": [{"match": {"detailed_description": query_text}}]}
            },
        }

        if filtered_ids:
            bm25_query["query"]["bool"]["filter"] = {
                "ids": {"values": list(filtered_ids)}
            }

        res = self.es.search(index=self.index_name, body=bm25_query)
        return {hit["_id"]: hit["_score"] for hit in res["hits"]["hits"]}

    def search_vector(self, query_vector, k=100, candidates=200, filtered_ids=None):
        if filtered_ids:
            # Fallback: manually filter after search (ES does not support knn+ids directly)
            vector_query = {
                "knn": {
                    "field": "description_vector",
                    "query_vector": query_vector,
                    "k": candidates,
                    "num_candidates": candidates,
                }
            }
            res = self.es.search(index=self.index_name, body=vector_query)
            return {
                hit["_id"]: hit["_score"]
                for hit in res["hits"]["hits"]
                if hit["_id"] in filtered_ids
            }

        else:
            vector_query = {
                "knn": {
                    "field": "description_vector",
                    "query_vector": query_vector,
                    "k": k,
                    "num_candidates": candidates,
                }
            }
            res = self.es.search(index=self.index_name, body=vector_query)
            return {hit["_id"]: hit["_score"] for hit in res["hits"]["hits"]}

    # --- Normalize Scores ---
    def normalize(self, scores_dict):
        if not scores_dict:
            return {}
        ids = list(scores_dict.keys())
        scores = np.array(list(scores_dict.values())).reshape(-1, 1)
        normalized = MinMaxScaler().fit_transform(scores).flatten()
        return dict(zip(ids, normalized))

    # --- Combine Scores ---
    def combine_scores(self, bm25_scores, vec_scores, weight_bm25=0.7, weight_vec=0.3):
        if not bm25_scores and not vec_scores:
            return {}

        # If one of the score sets is empty, use only the non-empty one
        if not bm25_scores:
            return self.normalize(vec_scores)
        if not vec_scores:
            return self.normalize(bm25_scores)

        norm_bm25 = self.normalize(bm25_scores)
        norm_vec = self.normalize(vec_scores)

        combined = {}
        for _id in set(norm_bm25.keys()).union(norm_vec.keys()):
            bm25 = norm_bm25.get(_id, 0)
            vec = norm_vec.get(_id, 0)
            combined[_id] = weight_bm25 * bm25 + weight_vec * vec
        return combined

    # --- Final Hybrid Search ---

    def hybrid_search(self, query_text, top_k=10, filtered_ids=None):
        print(f"\nSearching for: {query_text}")

        query_vector = self.encode_query(query_text)
        bm25_scores = self.search_bm25(query_text, filtered_ids=filtered_ids)
        vec_scores = self.search_vector(query_vector, filtered_ids=filtered_ids)

        combined = self.combine_scores(bm25_scores, vec_scores)
        top_results = sorted(combined.items(), key=lambda x: x[1], reverse=True)[:top_k]

        results = []
        for rank, (_id, score) in enumerate(top_results, start=1):
            doc = self.es.get(index=self.index_name, id=_id)
            source = doc["_source"]

            filtered_source = {
                k: v
                for k, v in source.items()
                if k not in ["cluster", "description_vector"]
            }

            result = {"rank": rank, "score": round(score, 2), **filtered_source}

            results.append(result)

        return json.dumps(results, indent=2, ensure_ascii=False)

    # --- Direct Search by Name ---
    def direct_elastic(self, name):
        # Using match query with fuzziness for more flexible name matching
        query = {
            "query": {
                "match": {
                    "name": {
                        "query": name,
                        "fuzziness": "AUTO",  # Automatically adjust fuzziness based on term length
                        "prefix_length": 2,    # First 2 characters must match exactly
                        "operator": "or"       # Match any of the terms
                    }
                }
            },
            "size": 10  # Limit results to top 10 matches
        }

        res = self.es.search(index=self.index_name, body=query)

        results = []
        for hit in res["hits"]["hits"]:
            source = hit["_source"]
            filtered_source = {
                k: v
                for k, v in source.items()
                if k not in ["cluster", "description_vector"]
            }
            # Add relevance score to the result
            filtered_source["relevance_score"] = round(hit["_score"], 2)
            results.append(filtered_source)

        return json.dumps(results, ensure_ascii=False)

    # --- Optional Filter Function ---
    def filter_elastic(self, filters):
        query = {
            "query": {
                "bool": {
                    "must": []
                }
            }
        }
        # Age Limit Filter
        # Age Limit Filter
        if filters.get("age_limit"):
            try:
                age_limit = float(filters["age_limit"])
                query["query"]["bool"]["must"].append({
                    "range": {
                        "required_age": {
                            "gte": age_limit
                        }
                    }
                })
            except ValueError:
                pass
        # Year Range Filter (keep as is since it's a range query)
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

        # Developer Filter - Changed back to term for exact match
        if filters.get("developer"):
            query["query"]["bool"]["must"].append({
                "term": {
                    "developers.keyword": filters["developer"]  # Using .keyword for exact match
                }
            })

        # Publisher Filter - Changed back to term for exact match
        if filters.get("publisher"):
            query["query"]["bool"]["must"].append({
                "term": {
                    "publishers.keyword": filters["publisher"]  # Using .keyword for exact match
                }
            })

        # Platform Filter (keep as term since it's a boolean)
        if filters.get("platform"):
            platform_field = f"platforms_{filters['platform'].lower()}"
            query["query"]["bool"]["must"].append({
                "term": {
                    platform_field: True
                }
            })

        # Currency Filter - Changed to term for exact match
        if filters.get("currency"):
            query["query"]["bool"]["must"].append({
                "term": {
                    "price_currency.keyword": filters["currency"]  # Using .keyword for exact match
                }
            })

        # Price Limit (keep as is since it's a range query)
        if filters.get("price_limit"):
            try:
                price = float(filters["price_limit"])
                query["query"]["bool"]["must"].append({
                    "range": {
                        "price_final": {
                            "gte": price
                        }
                    }
                })
            except ValueError:
                pass
        # Language Filter - Changed to term for exact match
        if filters.get("language"):
            languages = [lang.strip() for lang in filters["language"].split(",")]
            if len(languages) == 1:
                query["query"]["bool"]["must"].append({
                    "term": {
                        "supported_languages.keyword": languages[0]  # Using .keyword for exact match
                    }
                })
            else:
                # For multiple languages, use terms query
                query["query"]["bool"]["must"].append({
                    "terms": {
                        "supported_languages.keyword": languages  # Using .keyword for exact match
                    }
                })

        # Genre Filter - Changed to match with fuzziness
        if filters.get("genre"):
            query["query"]["bool"]["must"].append({
                "match": {
                    "genres": {
                        "query": filters["genre"],
                        "fuzziness": "AUTO",
                        "prefix_length": 2,
                        "operator": "or"
                    }
                }
            })

        # Category Filter - Changed to match with fuzziness
        if filters.get("category"):
            query["query"]["bool"]["must"].append({
                "match": {
                    "categories": {
                        "query": filters["category"],
                        "fuzziness": "AUTO",
                        "prefix_length": 2,
                        "operator": "or"
                    }
                }
            })

        query["size"] = 1000
        print(json.dumps(query, indent=2))
        res = self.es.search(index=self.index_name, body=query)

        return [hit["_id"] for hit in res["hits"]["hits"]]

    def get_games(self, results):
        func_name = results.get("function_name")
        if func_name == "direct_search":
            name = results.get("game_name")
            return self.direct_elastic(name)
        elif func_name == "filter_search":
            result_filter = self.filter_elastic(results)
            print(result_filter)
            
            # If there's a game description, perform hybrid search
            if results.get("game_description"):
                query_text = results.get("game_description")
                return self.hybrid_search(query_text, filtered_ids=result_filter)
            else:
                # If no game description, return filtered results directly (max 20 games)
                filtered_results = []
                for _id in result_filter[:20]:  # Limit to first 20 results
                    doc = self.es.get(index=self.index_name, id=_id)
                    source = doc["_source"]
                    filtered_source = {
                        k: v for k, v in source.items()
                        if k not in ["cluster", "description_vector"]
                    }
                    filtered_results.append(filtered_source)
                
                return json.dumps(filtered_results, indent=2, ensure_ascii=False)
        else:
            return results.get("response")