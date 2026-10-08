from __future__ import annotations
import re
from .models import ChatRequest, ChatResponse, SourceRef
from .triage import triage_text, EMERGENCY_REPLY, URGENT_REPLY
from .knowledge import IntentRouter, SymptomRetriever
from .drugs import DrugLabelService

router=IntentRouter(); symptoms=SymptomRetriever()

MED_PATTERN=re.compile(r'\b(?:about|of|for|taking|take|with|medicine|medication|drug)\s+([A-Za-z][A-Za-z0-9-]{2,30})\b',re.I)

def medication_candidate(text: str):
    common=['ibuprofen','paracetamol','acetaminophen','cetirizine','loratadine','omeprazole','loperamide','aspirin','warfarin','amoxicillin']
    lower=text.lower()
    for med in common:
        if med in lower: return med
    m=MED_PATTERN.search(text)
    return m.group(1) if m else None

async def respond(req: ChatRequest, drug_service: DrugLabelService | None = None):
    text=req.message.strip()
    urgency, _=triage_text(text)
    if urgency=='emergency':
        return ChatResponse(intent='emergency',urgency='emergency',reply=EMERGENCY_REPLY,
            actions=['Call emergency services now','Do not rely on the chatbot for further triage'],
            sources=[SourceRef(title='NHS urgent and emergency care',url='https://www.nhs.uk/nhs-services/urgent-and-emergency-care-services/',kind='service')],
            safety_note='This assistant does not diagnose medical conditions or replace emergency care.')

    intent=router.predict(text)
    matches=symptoms.search(text)
    if urgency=='urgent':
        src=[]
        if matches:
            g=matches[0][0]; src.append(SourceRef(title=g['source_title'],url=g['source_url'],kind='symptom_guidance'))
        return ChatResponse(intent=intent,urgency='urgent',reply=URGENT_REPLY,detected_topics=[g['name'] for g,_ in matches],
            actions=['Contact NHS 111 / urgent GP service','Escalate to 999/112 if symptoms become severe'],sources=src,
            safety_note='This assistant does not diagnose or prescribe treatment.')

    med=medication_candidate(text)
    if intent in {'medication','side_effects','interaction'} or med:
        service=drug_service or DrugLabelService()
        label=await service.lookup(med or text)
        if not label:
            return ChatResponse(intent=intent,urgency='information',reply='I could not find a matching public drug-label record. Check the exact generic or brand name, and ask a pharmacist if you need a medicine-safety decision.',
                actions=['Confirm the medicine name','Ask a pharmacist for personalised interaction or suitability advice'],
                sources=[SourceRef(title='openFDA drug labeling dataset',url='https://open.fda.gov/apis/drug/label/',kind='drug_label')],
                safety_note='Do not start, stop, combine or change a medicine based only on this assistant.')
        pieces=[f'I found a public drug-label record for {med or label.query}.']
        if intent=='interaction' and label.interactions:
            pieces.append('The label contains a drug-interactions section; review it with a pharmacist because absence of a named interaction does not prove a combination is safe.')
        elif intent=='side_effects' and label.adverse_reactions:
            pieces.append('The label includes reported adverse reactions. These do not predict what will happen to a specific person.')
        else:
            pieces.append('I can summarise labelled uses, warnings, contraindications, interactions and adverse reactions, but I do not provide personalised dosing or prescribing.')
        return ChatResponse(intent=intent,urgency='information',reply=' '.join(pieces),medication=label,
            actions=['Check the product leaflet','Ask a pharmacist/clinician about suitability, dose, pregnancy, kidney/liver disease or other medicines'],
            sources=[SourceRef(title='openFDA drug labeling dataset',url='https://open.fda.gov/apis/drug/label/',kind='drug_label')],
            safety_note='Public labels are informational and may not cover every formulation, interaction or individual risk.')

    if matches:
        g,score=matches[0]
        reply=g['summary']+'\n\nSelf-care options:\n- '+'\n- '.join(g['self_care'])
        if g['urgent']: reply+='\n\nGet medical advice sooner if: '+g['urgent'][0]
        if g['emergency']: reply+='\n\nEmergency warning: '+g['emergency'][0]
        return ChatResponse(intent=intent,urgency='self_care',reply=reply,detected_topics=[g['name']],
            actions=['Monitor symptoms','Use a pharmacist or GP if symptoms persist/worsen','Use 111/999 if red-flag symptoms develop'],
            sources=[SourceRef(title=g['source_title'],url=g['source_url'],kind='symptom_guidance')],
            safety_note='This is general information, not a diagnosis. Medicine suitability depends on age, pregnancy, conditions and other medicines.')

    return ChatResponse(intent=intent,urgency='information',reply='Tell me the main symptom, how severe it is, how long it has been present, and whether there are any red-flag symptoms such as severe breathing difficulty, severe chest pain, sudden weakness/confusion, or swelling of the mouth/throat. For medicine questions, include the exact generic or brand name.',
        actions=['Describe one main symptom at a time','Include duration and severity','For medicines, give the exact name'],
        safety_note='This assistant provides general education and triage guidance, not diagnosis or prescribing.')
