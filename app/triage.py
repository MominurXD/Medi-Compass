from __future__ import annotations
import re

EMERGENCY_PATTERNS = [
    r'cannot breathe|can\'t breathe|gasping|choking|severe difficulty breathing',
    r'(chest pain|chest pressure|tight chest).*(sweat|short of breath|sick|light.?headed|arm|jaw|back)',
    r'sudden.*(extreme|severe).*headache',
    r'(weakness|numbness).*(face|arm|leg)|cannot speak|can\'t speak|slurred speech',
    r'(swollen|swelling).*(tongue|throat|mouth|lips)',
    r'vomit(ing)? blood|coffee ground vomit',
    r'unconscious|unresponsive|seizure|fit\b',
    r'overdose|took too much|poison(ed|ing)?',
]
URGENT_PATTERNS = [
    r'chest pain|chest discomfort|chest pressure',
    r'shortness of breath|breathless|difficulty breathing',
    r'coughing up blood|blood in (stool|poo)|bloody diarrh',
    r'cannot keep fluids down|can\'t keep fluids down|dehydrated|dehydration',
    r'high fever|very high temperature',
    r'pregnan(t|cy).*(bleeding|severe pain)',
]

def triage_text(text: str):
    cleaned = text.lower()
    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, cleaned):
            return 'emergency', pattern
    for pattern in URGENT_PATTERNS:
        if re.search(pattern, cleaned):
            return 'urgent', pattern
    return None, None

EMERGENCY_REPLY = (
    'This could describe a medical emergency. If you are in the UK, call 999 now (or 112) or go to A&E. '
    'Do not drive yourself if you are seriously unwell. If you are outside the UK, use your local emergency number.'
)
URGENT_REPLY = (
    'This needs prompt medical assessment rather than relying only on self-care. In the UK, contact NHS 111 or an urgent GP service; '
    'if symptoms become severe or life-threatening, call 999/112.'
)
