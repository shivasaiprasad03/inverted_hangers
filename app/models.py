

"""
models.py
-----------
Data models and schema definitions for Adaptive Learning Pathfinder.
Includes Pydantic models for API validation and documentation of graph node/edge types.
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class Concept(BaseModel):
	"""
	Represents a fundamental unit of knowledge (e.g., 'Python Lists', 'Dijkstra's Algorithm').
	"""
	id: str
	name: str
	definition: Optional[str] = None
	domain: Optional[str] = None

class LearningResource(BaseModel):
	"""
	Represents an OER content item that teaches one or more concepts.
	"""
	id: str
	type: str  # e.g., video, text, quiz
	url: str
	source: Optional[str] = None
	estimated_duration: Optional[float] = None  # in minutes
	concepts: List[str] = Field(default_factory=list)  # concept ids explained

class Assessment(BaseModel):
	"""
	Represents an assessment tool to measure mastery of a concept.
	"""
	id: str
	type: str  # e.g., multiple-choice, coding-exercise
	difficulty: Optional[float] = None
	concepts: List[str] = Field(default_factory=list)  # concept ids assessed

class Learner(BaseModel):
	"""
	Represents a user, storing preferences and current knowledge state.
	"""
	id: str
	interests: List[str] = Field(default_factory=list)  # concept ids
	knowledge_state: Dict[str, float] = Field(default_factory=dict)  # concept id -> mastery score

# Edge Types (for graph schema, not Pydantic):
#   - HAS_PREREQUISITE: Concept -> Concept (weight: float)
#   - EXPLAINS: LearningResource -> Concept (coverage_score: float)
#   - ASSESSES: Assessment -> Concept (alignment_score: float)
#   - INTERESTED_IN: Learner -> Concept (strength: float)
#   - HAS_MASTERED: Learner -> Concept (mastery_score: float)
