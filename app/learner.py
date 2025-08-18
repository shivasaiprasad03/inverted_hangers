

"""
learner.py
----------
Learner state management for Adaptive Learning Pathfinder.
Includes functions for updating knowledge and interests with documentation and error handling.
"""

from .models import Learner
from typing import Optional

def update_knowledge_state(learner: Learner, concept_id: str, mastery: float) -> Learner:
	"""
	Update the learner's knowledge state for a given concept.
	Args:
		learner: Learner object
		concept_id: Concept identifier
		mastery: Mastery score (0.0-1.0)
	Returns:
		Updated Learner object
	"""
	if not 0.0 <= mastery <= 1.0:
		raise ValueError("Mastery score must be between 0.0 and 1.0")
	learner.knowledge_state[concept_id] = mastery
	return learner

def add_interest(learner: Learner, concept_id: str) -> Learner:
	"""
	Add a concept to the learner's interests if not already present.
	Args:
		learner: Learner object
		concept_id: Concept identifier
	Returns:
		Updated Learner object
	"""
	if concept_id not in learner.interests:
		learner.interests.append(concept_id)
	return learner
