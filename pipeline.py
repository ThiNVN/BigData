from Hybrid_Search import HybridSearch
from LLM_Response import LLMResponse
from dotenv import load_dotenv
from google import genai
import os
load_dotenv('api.env')
api_key = os.environ.get('gemini_api_key')
hybrid_search=HybridSearch(api_url="url")
llm_response=LLMResponse(api_key)
query="I want to play a multi-player shooting game with high end graphics that support French and free"
filter_result=llm_response.get_function_call(query)
result=hybrid_search.get_games(filter_result)
print("result",result)