import requests

# Example OER URLs (replace with real ones for production)
urls = [
    "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/pages/lecture-notes/",
    "https://ocw.mit.edu/courses/6-0001-introduction-to-computer-science-and-programming-in-python-fall-2016/pages/readings/"
]

# 1. Build the knowledge graph
r = requests.post("http://127.0.0.1:8000/build_graph", json={"urls": urls})
print("Build Graph:", r.json())

# 2. Find a learning path (replace with real concept IDs from the graph)
path_req = {
    "start": "Python",
    "goal": "Recursion",
    "weights": {"time": 0.3, "cognitive": 0.3, "prereq": 0.2, "interest": 0.2}
}
r = requests.post("http://127.0.0.1:8000/find_path", json=path_req)
print("Find Path:", r.json())

# 3. Update learner knowledge
r = requests.post("http://127.0.0.1:8000/update_learner", json={"concept_id": "Python", "mastery": 1.0})
print("Update Learner:", r.json())
