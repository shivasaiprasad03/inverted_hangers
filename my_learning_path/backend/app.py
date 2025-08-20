from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Models ---
class BuildGraphRequest(BaseModel):
    urls: List[str]

class BuildGraphResponse(BaseModel):
    nodes: List[str]

class FindPathRequest(BaseModel):
    start: str
    goal: str
    weights: Dict[str, float]

class FindPathResponse(BaseModel):
    path: List[str]

class UpdateLearnerRequest(BaseModel):
    concept_id: str
    mastery: float

class UpdateLearnerResponse(BaseModel):
    knowledge_state: Dict[str, float]

# --- Dummy in-memory data ---
topics = ["Intro", "Basics", "Advanced", "Project"]
paths = {
    ("Intro", "Basics"): ["Intro", "Basics"],
    ("Basics", "Advanced"): ["Basics", "Advanced"],
    ("Intro", "Project"): ["Intro", "Basics", "Advanced", "Project"]
}
learner_state = {}

@app.post("/build_graph", response_model=BuildGraphResponse)
def build_graph(req: BuildGraphRequest):
    # Dummy: return static topics
    return BuildGraphResponse(nodes=topics)

@app.post("/find_path", response_model=FindPathResponse)
def find_path(req: FindPathRequest):
    # Dummy: return a static path
    key = (req.start, req.goal)
    path = paths.get(key, [req.start, req.goal])
    return FindPathResponse(path=path)

@app.post("/update_learner", response_model=UpdateLearnerResponse)
def update_learner(req: UpdateLearnerRequest):
    learner_state[req.concept_id] = req.mastery
    return UpdateLearnerResponse(knowledge_state=learner_state)
