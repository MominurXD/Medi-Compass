from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)

def test_health():
    assert client.get('/api/health').json()['status']=='ok'

def test_topics():
    r=client.get('/api/topics')
    assert r.status_code==200
    assert len(r.json())>=8

def test_chat():
    r=client.post('/api/chat',json={'message':'I have a sore throat','context':{}})
    assert r.status_code==200
    assert r.json()['urgency']=='self_care'
