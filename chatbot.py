from LLM_Response import LLMResponse
from Hybrid_Search import HybridSearch
from google import genai
import os
from dotenv import load_dotenv

load_dotenv('api.env')
api_key = os.environ.get('gemini_api_key')
genai_client =genai.Client(api_key=api_key)
llm=LLMResponse(api_key)
hybird_search=HybridSearch()

query_text="I want to play a single-player racing game with high end graphics that from support French"
result=llm.get_function_call(query_text)
game=hybird_search.get_games(result)
print(game)