# MediCompass

**Safety-first symptom guidance and medication information assistant.**

Personal project by **Mohammed Mominur Rahman Miah**.

MediCompass is a web-based healthcare guidance assistant that combines **machine-learning intent classification**, **source-grounded symptom retrieval**, **deterministic red-flag triage**, and **public drug-label data**. It is designed as an educational software-engineering project, not as a diagnostic or prescribing system.

## Visual design

The web interface uses an **NHS-inspired digital colour palette** for familiarity and accessibility: blue/white as the dominant colours, pale grey backgrounds, green actions, red urgent states and yellow keyboard focus states.

MediCompass is an independent portfolio project and is **not affiliated with or endorsed by the NHS**. It does not use the NHS logo or claim to be an NHS service.

## What it does

- Web-based healthcare chatbot for common symptom and medicine questions.
- Runs emergency/urgent **red-flag rules before the conversational layer**.
- Uses a trained **TF-IDF + Logistic Regression classifier** to identify the type of question.
- Retrieves self-care and escalation guidance from a structured symptom dataset.
- Queries the **openFDA Drug Labeling dataset/API** for public medicine-label information.
- Displays labelled uses, warnings, contraindications, drug interactions and adverse reactions when available.
- Keeps source provenance attached to symptom and medication responses.
- Does **not** diagnose conditions, prescribe medicines or recommend personalised dose changes.
- Does **not** claim that absence of a listed interaction proves a medicine combination is safe.
- Does not persist patient chat messages to a conversation database by default.
- Includes automated tests, Docker and GitHub Actions CI.

# Datasets and data sources

MediCompass deliberately uses different data sources for different jobs rather than training one model to predict a medical diagnosis.

## 1. Intent-training dataset — `data/intents.csv`

This is the dataset used to **train the NLP classifier**.

It contains example patient messages labelled with conversational intents such as:

- `greeting`
- `symptom`
- `self_care`
- `medication`
- `side_effects`
- `interaction`
- `emergency`

Example rows:

```csv
text,intent
I have a headache,symptom
home remedies for cough,self_care
tell me about ibuprofen,medication
side effects of ibuprofen,side_effects
can I take ibuprofen with warfarin,interaction
I cannot breathe,emergency
```

At startup, scikit-learn trains a pipeline:

```text
patient message
      |
      v
TF-IDF vectorisation
      |
      v
Logistic Regression classifier
      |
      v
predicted conversational intent
```

The model is used for **routing the conversation**, not for diagnosing a disease.

## 2. Symptom-guidance dataset — `data/symptom_guidance.json`

This structured dataset is used for **information retrieval**, not disease prediction.

Each record contains:

- symptom/topic name;
- retrieval keywords;
- plain-language summary;
- general self-care options;
- urgent escalation guidance;
- emergency red flags;
- public source title;
- public source URL.

The current demonstration dataset contains:

- headache;
- cough;
- sore throat;
- diarrhoea/vomiting;
- fever;
- chest pain;
- shortness of breath;
- allergic reactions.

The retrieval layer uses **TF-IDF similarity** to match the patient's wording to the most relevant source-linked guidance record.

This dataset is intentionally small and transparent rather than pretending to be an exhaustive clinical knowledge base.

## 3. openFDA Drug Labeling dataset

Medication information is retrieved at runtime from the public **openFDA Drug Labeling** API:

https://open.fda.gov/apis/drug/label/

When a matching label is available, MediCompass can surface fields such as:

- generic and brand names;
- indications and labelled uses;
- warnings;
- contraindications;
- drug interactions;
- adverse reactions;
- label effective date.

The optional development utility:

```text
scripts/sync_openfda_labels.py
```

can cache selected public label records for local development.

Public drug-label data is presented as educational information only. A pharmacist or clinician should make personalised medicine-safety, interaction and dosing decisions.

## What is trained vs retrieved?

| Component | Technique | Data |
| --- | --- | --- |
| Question routing | TF-IDF + Logistic Regression | `data/intents.csv` |
| Symptom matching | TF-IDF similarity retrieval | `data/symptom_guidance.json` |
| Emergency triage | Deterministic safety rules | Explicit red-flag patterns |
| Medication information | Live API retrieval | openFDA Drug Labeling dataset |

MediCompass **does not train a model to diagnose medical conditions from symptoms**.

That is an intentional safety and engineering boundary: the classifier identifies the type of request, while source-linked guidance and deterministic escalation rules handle the response.

## Safety architecture

```text
User message
    |
    v
Red-flag triage rules  ---- emergency/urgent ----> escalation response
    |
    v
TF-IDF + Logistic Regression intent classifier
    |
    +---- symptom/self-care ---> symptom guidance retrieval dataset
    |
    +---- medicine -----------> openFDA drug-label lookup
    |
    +---- interaction --------> label interaction section + pharmacist warning
    |
    v
Source-linked response + safety note
```

Safety rules deliberately sit outside the statistical NLP classifier. This prevents a high-risk phrase from being downgraded simply because the intent classifier predicts another category.

## Tech stack

- Python 3.12
- FastAPI
- scikit-learn
- httpx
- Pydantic
- HTML / CSS / JavaScript
- Pytest
- Docker
- GitHub Actions

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
PYTHONPATH=. uvicorn app.main:app --reload
```

Open `http://localhost:8000`.

## Tests

```bash
PYTHONPATH=. pytest -q
node --check web/app.js
docker build -t medicompass .
```

The automated tests cover emergency escalation, symptom retrieval, chest-pain urgency, drug-label parsing, API health and topic endpoints.

## API

- `GET /api/health`
- `GET /api/topics`
- `POST /api/chat`

Example request:

```json
{
  "message": "Tell me about ibuprofen",
  "context": {
    "age_group": "adult",
    "pregnant": false,
    "medicines": []
  }
}
```

## Healthcare boundary

MediCompass is a portfolio project and general-information assistant. It must not be used to replace a clinician, pharmacist, emergency service or official medicine leaflet.

It does not:

- diagnose medical conditions;
- prescribe treatment;
- recommend prescription medicines;
- provide personalised medicine doses;
- advise a patient to stop or change prescribed treatment;
- guarantee that a medication combination is safe.

For the UK-oriented demonstration, urgent/emergency routing references NHS 111 and 999/112. A production healthcare deployment would require substantially more clinical governance, data-protection review, validation and regulatory assessment.

## Licence

MIT. Third-party/public health content and datasets remain subject to their original terms and licences.
