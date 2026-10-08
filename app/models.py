from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field

Urgency = Literal['emergency','urgent','routine','self_care','information']

class ChatContext(BaseModel):
    age_group: Literal['adult','child','older_adult','unknown'] = 'unknown'
    pregnant: bool | None = None
    medicines: list[str] = Field(default_factory=list, max_length=20)

class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=1200)
    context: ChatContext = Field(default_factory=ChatContext)

class SourceRef(BaseModel):
    title: str
    url: str
    kind: Literal['symptom_guidance','drug_label','service']

class MedicationSummary(BaseModel):
    query: str
    generic_names: list[str] = []
    brand_names: list[str] = []
    indications: list[str] = []
    warnings: list[str] = []
    contraindications: list[str] = []
    interactions: list[str] = []
    adverse_reactions: list[str] = []
    effective_time: str | None = None
    dataset: str = 'openFDA drug labeling'

class ChatResponse(BaseModel):
    intent: str
    urgency: Urgency
    reply: str
    detected_topics: list[str] = []
    actions: list[str] = []
    medication: MedicationSummary | None = None
    sources: list[SourceRef] = []
    safety_note: str
