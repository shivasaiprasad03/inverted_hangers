

"""
pathfinder.py
-------------
Multi-objective A* (MOA*) pathfinding for Adaptive Learning Pathfinder.
Includes cost functions, normalization, and robust error handling.
"""

import heapq
import networkx as nx
from typing import Dict, List, Optional

def min_max_scale(val: float, min_val: float, max_val: float) -> float:
	"""
	Normalize a value to [0,1] using min-max scaling.
	"""
	if max_val == min_val:
		return 0.0
	return (val - min_val) / (max_val - min_val)

def moa_star(
	G: nx.DiGraph,
	start: str,
	goal: str,
	weights: Dict[str, float],
	concept_durations: Optional[Dict[str, float]] = None,
	concept_difficulties: Optional[Dict[str, float]] = None,
	learner_interests: Optional[Dict[str, float]] = None,
	learner_knowledge: Optional[Dict[str, float]] = None
) -> List[str]:
	"""
	Multi-objective A* search for optimal learning path.
	Args:
		G: Directed knowledge graph (NetworkX DiGraph)
		start: Start node id
		goal: Goal node id
		weights: Dict with keys 'time', 'cognitive', 'prereq', 'interest'
		concept_durations: Dict of concept id -> estimated duration
		concept_difficulties: Dict of concept id -> difficulty
		learner_interests: Dict of concept id -> interest strength
		learner_knowledge: Dict of concept id -> mastery score
	Returns:
		List of node ids representing the optimal path, or empty list if not found.
	"""
	if G is None or start not in G or goal not in G:
		return []
	open_list = []
	heapq.heappush(open_list, (0, [start]))
	visited = set()
	while open_list:
		cost, path = heapq.heappop(open_list)
		node = path[-1]
		if node == goal:
			return path
		if node in visited:
			continue
		visited.add(node)
		for succ in G.successors(node):
			edge = G[node][succ]
			# Compute costs (default to 1.0 if not provided)
			time_cost = concept_durations.get(succ, 1.0) if concept_durations else 1.0
			cognitive_cost = concept_difficulties.get(succ, 1.0) if concept_difficulties else 1.0
			prereq_cost = 1.0 - edge.get('weight', 1.0) if edge.get('type') == 'HAS_PREREQUISITE' else 0.0
			interest_cost = 1.0 - learner_interests.get(succ, 0.0) if learner_interests else 1.0
			# Weighted sum (assume all costs in [0,1])
			total = (
				weights.get('time', 0.25) * time_cost +
				weights.get('cognitive', 0.25) * cognitive_cost +
				weights.get('prereq', 0.25) * prereq_cost +
				weights.get('interest', 0.25) * interest_cost
			)
			heapq.heappush(open_list, (cost + total, path + [succ]))
	return []  # No path found
