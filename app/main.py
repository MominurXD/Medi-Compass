from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .models import ChatRequest
from .chat import respond
from .knowledge import GUIDANCE

app=FastAPI(title='MediCompass',version='1.0.0',description='Safety-first symptom and medication guidance assistant.')

@app.get('/api/health')
def health(): return {'status':'ok','service':'MediCompass','version':'1.0.0'}

@app.get('/api/topics')
def topics(): return [{'id':x['id'],'name':x['name'],'keywords':x['keywords']} for x in GUIDANCE]

@app.post('/api/chat')
async def chat(request: ChatRequest): return await respond(request)

WEB=Path(__file__).resolve().parent.parent/'web'
app.mount('/',StaticFiles(directory=WEB,html=True),name='web')
