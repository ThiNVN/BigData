from pyngrok import ngrok
from fastapi import FastAPI
from pydantic import BaseModel
import nest_asyncio
import uvicorn
from threading import Thread
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os
load_dotenv('api.env')
ngrok_authtoken=os.environ.get('ngrok_authtoken')

ngrok.set_auth_token(ngrok_authtoken) 

app = FastAPI()
model = SentenceTransformer('all-MiniLM-L6-v2')  

class EncodeRequest(BaseModel):
    text: str

@app.post("/encode")
def encode(req: EncodeRequest):
    embedding = model.encode(req.text).tolist()
    return {"embedding": embedding}


def run():
    uvicorn.run(app, host="0.0.0.0", port=8000)

nest_asyncio.apply()
Thread(target=run).start()

public_url = ngrok.connect(8000)
print("Public URL:", public_url)
