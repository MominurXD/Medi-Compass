from __future__ import annotations
import re
import httpx
from .models import MedicationSummary

BASE='https://api.fda.gov/drug/label.json'

class DrugLabelService:
    def __init__(self, client: httpx.AsyncClient | None = None):
        self.client=client

    async def lookup(self, name: str):
        q=name.strip()
        if not q: return None
        owns=self.client is None
        client=self.client or httpx.AsyncClient(timeout=15.0)
        searches=[f'openfda.generic_name:"{q}"',f'openfda.brand_name:"{q}"']
        try:
            for search in searches:
                try:
                    r=await client.get(BASE,params={'search':search,'limit':1})
                    if r.status_code==404: continue
                    r.raise_for_status(); payload=r.json(); rows=payload.get('results') or []
                    if rows: return self._parse(q,rows[0])
                except httpx.HTTPStatusError:
                    continue
            return None
        finally:
            if owns: await client.aclose()

    @staticmethod
    def _first(record, key, limit=2):
        vals=record.get(key) or []
        if isinstance(vals,str): vals=[vals]
        cleaned=[]
        for value in vals[:limit]:
            text=re.sub(r'\s+',' ',str(value)).strip()
            cleaned.append(text[:900])
        return cleaned

    def _parse(self, query, row):
        ofda=row.get('openfda') or {}
        return MedicationSummary(
            query=query,
            generic_names=(ofda.get('generic_name') or [])[:5],
            brand_names=(ofda.get('brand_name') or [])[:5],
            indications=self._first(row,'indications_and_usage'),
            warnings=self._first(row,'warnings') or self._first(row,'warnings_and_cautions'),
            contraindications=self._first(row,'contraindications'),
            interactions=self._first(row,'drug_interactions'),
            adverse_reactions=self._first(row,'adverse_reactions'),
            effective_time=row.get('effective_time'),
        )
