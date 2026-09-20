import unittest
from services.six_paper_service import evaluate_paper,build_candidate

class ScoringTests(unittest.TestCase):
    def test_deleted_blank_multiple(self):
        r=evaluate_paper({1:'A',2:'BLANK',3:'*',4:'B'},{1:'A',2:'C',3:'D',4:'DELETED'},set())
        self.assertEqual((r['correct'],r['wrong'],r['unanswered'],r['bonus']),(1,1,1,1))
        self.assertEqual(r['score'],2)
        self.assertEqual(r['max_score'],5)

    def test_reject_incomplete(self):
        for answers in ({},{1:'REVIEW'},{2:'B'}):
            with self.assertRaises(ValueError):
                evaluate_paper(answers,{1:'A'},set())

    def test_six_papers(self):
        r=evaluate_paper({1:'A'},{1:'A'},set())
        papers={f'p{i}':dict(r) for i in range(1,7)}
        candidate=build_candidate('Test','001',papers)
        self.assertEqual(candidate['merit_total'],4)
        papers['p2']['percentage']=0
        self.assertFalse(build_candidate('Test','001',papers)['qualifying_pass'])

if __name__=='__main__':
    unittest.main()
