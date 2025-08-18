"""
main.py
-------
FastAPI entrypoint for Adaptive Learning Pathfinder.
Includes API endpoints for graph building, pathfinding, and learner state management.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
import networkx as nx
from . import graph_builder, pathfinder, learner, models

app = FastAPI(
    title="Adaptive Learning Pathfinder API",
    description="Multi-objective optimization for personalized education on dynamic knowledge graphs.",
    version="1.0.0",
    openapi_tags=[
        {"name": "Graph", "description": "Knowledge graph construction and management."},
        {"name": "Pathfinding", "description": "Personalized learning path generation."},
        {"name": "Learner", "description": "Learner state and personalization."}
    ]
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:8080"] for more security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory objects for demo
G = None
learner_state = models.Learner(id="demo")

@app.get("/", tags=["General"])
def read_root():
    """Health check endpoint."""
    return {"message": "Adaptive Learning Pathfinder API is running."}

class BuildGraphRequest(BaseModel):
    urls: List[str]

@app.post("/build_graph", tags=["Graph"])
def build_graph(req: BuildGraphRequest):
    """Build a knowledge graph from a list of OER URLs."""
    global G
    if not req.urls:
        raise HTTPException(status_code=400, detail="No URLs provided.")
    G = graph_builder.build_knowledge_graph(req.urls)
    if G is None or len(G.nodes) == 0:
        raise HTTPException(status_code=500, detail="Failed to build graph.")
    return {"nodes": list(G.nodes), "edges": list(G.edges)}

class PathRequest(BaseModel):
    start: str
    goal: str
    weights: Dict[str, float]

@app.post("/find_path", tags=["Pathfinding"])
def find_path(req: PathRequest):
    """Find a personalized learning path from start to goal concept."""
    if G is None:
        raise HTTPException(status_code=400, detail="Graph not built yet.")
    path = pathfinder.moa_star(G, req.start, req.goal, req.weights)
    if not path:
        raise HTTPException(status_code=404, detail="No path found.")
    return {"path": path}

class UpdateLearnerRequest(BaseModel):
    concept_id: str
    mastery: float

@app.post("/update_learner", tags=["Learner"])
def update_learner(req: UpdateLearnerRequest):
    """Update the learner's knowledge state for a concept."""
    global learner_state
    try:
        learner_state = learner.update_knowledge_state(learner_state, req.concept_id, req.mastery)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"knowledge_state": learner_state.knowledge_state}
