# CV and LinkedIn wording

## CV project entry

**MediCompass — Healthcare Guidance & Medication Information Assistant**  
*Python, FastAPI, scikit-learn, httpx, JavaScript, Docker, GitHub Actions*

- Built a web-based healthcare guidance assistant combining a **TF-IDF + Logistic Regression classifier trained on an intent-labelled dataset**, TF-IDF retrieval over a structured symptom-guidance dataset, and deterministic red-flag triage.
- Integrated the public **openFDA Drug Labeling dataset/API** to display medication indications, warnings, contraindications, interactions and adverse reactions with source provenance.
- Designed a safety architecture that runs emergency/urgent escalation rules before the conversational NLP layer and deliberately excludes diagnosis, prescribing and personalised dose changes.
- Added an NHS-inspired responsive chat dashboard, source-linked symptom guidance, automated tests, Docker packaging and CI.

## LinkedIn project description

Built **MediCompass**, a safety-first healthcare guidance chatbot for symptom self-care information and medication education.

The project uses three distinct data layers:

- an intent-labelled dataset used to train a TF-IDF + Logistic Regression classifier;
- a structured source-linked symptom dataset used for TF-IDF retrieval;
- live medication label data from the public openFDA Drug Labeling dataset/API.

The key engineering challenge was separating conversational behaviour from safety logic: emergency red flags are evaluated before the NLP layer, and medication responses preserve source provenance instead of inventing drug information.

Tech: **Python, FastAPI, scikit-learn, httpx, Pydantic, JavaScript, Docker and GitHub Actions**.
