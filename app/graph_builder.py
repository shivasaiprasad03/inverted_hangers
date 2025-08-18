

"""
graph_builder.py
----------------
Knowledge graph construction pipeline for Adaptive Learning Pathfinder.
Includes scraping, concept extraction, and graph building with documentation and error handling.
"""

import requests
from bs4 import BeautifulSoup
import spacy
import networkx as nx
from sentence_transformers import SentenceTransformer, util
from .models import Concept, LearningResource
from typing import List, Set

# Load NLP models globally for efficiency
try:
	nlp = spacy.load("en_core_web_sm")
except OSError:
	raise RuntimeError("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

def scrape_text_from_url(url: str) -> str:
	"""
	Scrape main text content from a given URL.
	Returns concatenated paragraph text or empty string on failure.
	"""
	try:
		resp = requests.get(url, timeout=10)
		resp.raise_for_status()
		soup = BeautifulSoup(resp.text, 'html.parser')
		paragraphs = [p.get_text() for p in soup.find_all('p')]
		return '\n'.join(paragraphs)
	except Exception as e:
		print(f"[scrape_text_from_url] Error scraping {url}: {e}")
		return ""

def extract_concepts(text: str) -> List[str]:
	"""
	Extract candidate concepts (noun phrases) from text using spaCy.
	Returns a list of unique noun phrases.
	"""
	doc = nlp(text)
	concepts: Set[str] = set(chunk.text.strip() for chunk in doc.noun_chunks if len(chunk.text.strip()) > 2)
	return list(concepts)

def build_knowledge_graph(urls: List[str]) -> nx.DiGraph:
	"""
	Build a directed knowledge graph from a list of OER URLs.
	Nodes: Concepts and LearningResources. Edges: EXPLAINS, HAS_PREREQUISITE.
	"""
	G = nx.DiGraph()
	all_concepts: Set[str] = set()
	resource_nodes = []
	for idx, url in enumerate(urls):
		text = scrape_text_from_url(url)
		if not text:
			continue
		concepts = extract_concepts(text)
		all_concepts.update(concepts)
		res_id = f"res_{idx}"
		G.add_node(res_id, type="LearningResource", url=url, concepts=concepts)
		resource_nodes.append((res_id, concepts))
	# Add concept nodes
	for concept in all_concepts:
		G.add_node(concept, type="Concept")
	# Add EXPLAINS edges
	for res_id, concepts in resource_nodes:
		for c in concepts:
			G.add_edge(res_id, c, type="EXPLAINS", coverage_score=1.0)
	# Add HAS_PREREQUISITE edges using semantic similarity (simple heuristic)
	concept_list = list(all_concepts)
	if len(concept_list) > 1:
		embeddings = embedder.encode(concept_list, convert_to_tensor=True)
		for i, c1 in enumerate(concept_list):
			for j, c2 in enumerate(concept_list):
				if i != j:
					sim = util.pytorch_cos_sim(embeddings[i], embeddings[j]).item()
					if sim > 0.7:  # threshold for relatedness
						G.add_edge(c1, c2, type="HAS_PREREQUISITE", weight=sim)
	return G
