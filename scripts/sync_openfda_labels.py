"""Optional utility to cache openFDA label records for named medicines."""
import json, sys
from pathlib import Path
import httpx

names=sys.argv[1:] or ['ibuprofen','cetirizine','loratadine','omeprazole']
out=[]
with httpx.Client(timeout=20.0) as client:
    for name in names:
        r=client.get('https://api.fda.gov/drug/label.json',params={'search':f'openfda.generic_name:"{name}"','limit':1})
        if r.status_code==200:
            out.append({'query':name,'record':r.json()['results'][0]})
Path('data/openfda_cache.json').write_text(json.dumps(out,indent=2))
print(f'wrote {len(out)} label records')
