from pyngrok import ngrok
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import nest_asyncio
import uvicorn
from threading import Thread
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from Hybrid_Search import HybridSearch
from LLM_Response import LLMResponse
import os
import json

load_dotenv("api.env")
ngrok_authtoken = os.environ.get("ngrok_authtoken")
api_key = os.environ.get("gemini_api_key")
hybird_search = HybridSearch()
llm_response = LLMResponse(api_key)

ngrok.set_auth_token(ngrok_authtoken)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
model = SentenceTransformer("all-MiniLM-L6-v2")


class EncodeRequest(BaseModel):
    text: str


@app.post("/encode")
def encode(req: EncodeRequest):
    embedding = model.encode(req.text).tolist()
    return {"embedding": embedding}


@app.post("/search")
def search(req: EncodeRequest):
    filter_result = llm_response.get_function_call(req.text)
    games = hybird_search.get_games(filter_result)
    games_data = json.loads(games)
    if "message" in games_data:
        raise HTTPException(
            status_code=404,
            detail="No games matched your filters. Try adjusting your search criteria.",
        )
    return {"games": games_data}


def run():
    uvicorn.run(app, host="0.0.0.0", port=8000)


nest_asyncio.apply()
Thread(target=run).start()

public_url = ngrok.connect(8000)
print("Public URL:", public_url)
