import asyncio
import httpx
from app.chat import respond
from app.models import ChatRequest
from app.drugs import DrugLabelService

def test_emergency_breathing_escalates():
    result=asyncio.run(respond(ChatRequest(message='I cannot breathe and I am gasping')))
    assert result.urgency=='emergency'
    assert '999' in result.reply

def test_headache_retrieval():
    result=asyncio.run(respond(ChatRequest(message='I have had a mild headache today')))
    assert result.urgency=='self_care'
    assert 'Headache' in result.detected_topics

def test_chest_pain_is_at_least_urgent():
    result=asyncio.run(respond(ChatRequest(message='I have chest pain that comes and goes')))
    assert result.urgency in {'urgent','emergency'}

def test_drug_label_parsing():
    async def handler(request: httpx.Request):
        return httpx.Response(200,json={'results':[{
            'effective_time':'20250101',
            'openfda':{'generic_name':['IBUPROFEN'],'brand_name':['TEST BRAND']},
            'indications_and_usage':['For temporary relief of minor aches.'],
            'warnings':['Ask a doctor before use in some circumstances.'],
            'drug_interactions':['Anticoagulant interaction warning.'],
            'adverse_reactions':['Possible stomach upset.']
        }]})
    client=httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        result=asyncio.run(respond(ChatRequest(message='tell me about ibuprofen'),DrugLabelService(client)))
    finally:
        asyncio.run(client.aclose())
    assert result.medication.generic_names==['IBUPROFEN']
    assert result.urgency=='information'

def test_unknown_prompt_requests_more_detail():
    result=asyncio.run(respond(ChatRequest(message='something feels off today')))
    assert result.urgency=='information'
