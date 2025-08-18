import unittest
from app import learner, models

class TestLearner(unittest.TestCase):
    def setUp(self):
        self.learner = models.Learner(id="test")

    def test_update_knowledge_state(self):
        learner.update_knowledge_state(self.learner, "Python", 0.8)
        self.assertEqual(self.learner.knowledge_state["Python"], 0.8)

    def test_add_interest(self):
        learner.add_interest(self.learner, "Recursion")
        self.assertIn("Recursion", self.learner.interests)

    def test_invalid_mastery(self):
        with self.assertRaises(ValueError):
            learner.update_knowledge_state(self.learner, "Python", 1.5)

if __name__ == "__main__":
    unittest.main()
